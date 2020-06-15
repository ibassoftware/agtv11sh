# # -*- RCS -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class LandedCost(models.Model):
	_inherit = 'stock.landed.cost'

	state = fields.Selection([
		('draft', 'Draft'),
		('validate', 'Validated'),
		('done', 'Posted'),
		('cancel', 'Cancelled')], 'State', default='draft',
		copy=False, readonly=True, track_visibility='onchange')
	date = fields.Date(states={'validate': [('readonly', True)], 'done': [('readonly', True)]})
	picking_ids = fields.Many2many(states={'validate': [('readonly', True)], 'done': [('readonly', True)]})
	cost_lines = fields.One2many(states={'validate': [('readonly', True)], 'done': [('readonly', True)]})
	valuation_adjustment_lines = fields.One2many(states={'validate': [('readonly', True)], 'done': [('readonly', True)]})
	description = fields.Text(states={'validate': [('readonly', True)], 'done': [('readonly', True)]})
	account_journal_id = fields.Many2one(states={'validate': [('readonly', True)], 'done': [('readonly', True)]})

	@api.multi
	def button_validate(self):
		move_status = self.env['ir.config_parameter'].get_param('stock.group_account_landed_cost_status')

		if any(cost.state != 'draft' for cost in self):
			raise UserError(_('Only draft landed costs can be validated'))
		if any(not cost.valuation_adjustment_lines for cost in self):
			raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
		if not self._check_sum():
			raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

		for cost in self:
			move = self.env['account.move'].create({
				'journal_id': cost.account_journal_id.id,
				'date': cost.date,
				'ref': cost.name
			})
			for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
				# Prorate the value at what's still in stock
				cost_to_add = (line.move_id.remaining_qty / line.move_id.product_qty) * line.additional_landed_cost

				new_landed_cost_value = line.move_id.landed_cost_value + line.additional_landed_cost
				line.move_id.write({
					'landed_cost_value': new_landed_cost_value,
					'remaining_value': line.move_id.remaining_value + cost_to_add,
					'price_unit': (line.move_id.value + new_landed_cost_value) / line.move_id.product_qty,
				})
				# `remaining_qty` is negative if the move is out and delivered proudcts that were not
				# in stock.
				qty_out = 0
				if line.move_id._is_in():
					qty_out = line.move_id.product_qty - line.move_id.remaining_qty
				elif line.move_id._is_out():
					qty_out = line.move_id.product_qty
				move_line = line._create_accounting_entries(move, qty_out)
				move.write({'line_ids': move_line})

			move.assert_balanced()
			cost.write({'state': 'validate', 'account_move_id': move.id})
			# POST ACCOUNTING ENTRIES IF SET TO AUTOPOST
			if move_status == 'post':
				cost.write({'state': 'done'})
				move.post()
		return True

	@api.multi
	def button_post(self):
		for cost in self:
			cost.write({'state': 'done'})
			cost.account_move_id.post()
		return True
