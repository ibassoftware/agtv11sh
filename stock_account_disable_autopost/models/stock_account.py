from odoo import models, fields, api
from collections import defaultdict

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
	_inherit = 'stock.move'

	def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
		self.ensure_one()
		move_status = self.env['ir.config_parameter'].get_param('stock.group_account_move_status')

		AccountMove = self.env['account.move']
		move_lines = self._prepare_account_move_line(self.product_qty, abs(self.value), credit_account_id, debit_account_id)
		if move_lines:
			date = self._context.get('force_period_date', fields.Date.context_today(self))
			new_account_move = AccountMove.create({
				'journal_id': journal_id,
				'line_ids': move_lines,
				'date': date,
				'ref': self.picking_id.name,
				'stock_move_id': self.id,
			})
			if move_status == 'post':
				new_account_move.post()