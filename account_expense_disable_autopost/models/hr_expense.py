from odoo import models, fields, api, _
from collections import defaultdict
from odoo.tools import float_is_zero

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class HrExpense(models.Model):
	_inherit = 'hr.expense'

	state = fields.Selection([
		('draft', 'To Submit'),
		('reported', 'Reported'),
		('unpost', 'Unposted'),
		('done', 'Posted'),
		('refused', 'Refused')
	])

	# OVERRIDE TO RECOMPUTE STATE
	@api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
	def _compute_state(self):
		for expense in self:
			if not expense.sheet_id:
				expense.state = "draft"
			elif expense.sheet_id.state == "cancel":
				expense.state = "refused"
			elif not expense.sheet_id.account_move_id:
				expense.state = "reported"
			elif expense.sheet_id.account_move_id and expense.sheet_id.state == "unpost":
				expense.state = "unpost"
			else:
				expense.state = "done"

	@api.multi
	def action_move_create(self):
		move_status = self.env['ir.config_parameter'].sudo().get_param('hr_expense.group_account_expense_status')
		'''
		main function that is called when trying to create the accounting entries related to an expense
		'''
		move_group_by_sheet = {}
		for expense in self:
			journal = expense.sheet_id.bank_journal_id if expense.payment_mode == 'company_account' else expense.sheet_id.journal_id
			#create the move that will contain the accounting entries
			acc_date = expense.sheet_id.accounting_date or expense.date
			if not expense.sheet_id.id in move_group_by_sheet:
				move = self.env['account.move'].create({
					'journal_id': journal.id,
					'company_id': self.env.user.company_id.id,
					'date': acc_date,
					'ref': expense.sheet_id.name,
					# force the name to the default value, to avoid an eventual 'default_name' in the context
					# to set it to '' which cause no number to be given to the account.move when posted.
					'name': '/',
				})
				move_group_by_sheet[expense.sheet_id.id] = move
			else:
				move = move_group_by_sheet[expense.sheet_id.id]
			company_currency = expense.company_id.currency_id
			diff_currency_p = expense.currency_id != company_currency
			#one account.move.line per expense (+taxes..)
			move_lines = expense._move_line_get()

			#create one more move line, a counterline for the total on payable account
			payment_id = False
			total, total_currency, move_lines = expense._compute_expense_totals(company_currency, move_lines, acc_date)
			if expense.payment_mode == 'company_account':
				if not expense.sheet_id.bank_journal_id.default_credit_account_id:
					raise UserError(_("No credit account found for the %s journal, please configure one.") % (expense.sheet_id.bank_journal_id.name))
				emp_account = expense.sheet_id.bank_journal_id.default_credit_account_id.id
				journal = expense.sheet_id.bank_journal_id
				#create payment
				payment_methods = (total < 0) and journal.outbound_payment_method_ids or journal.inbound_payment_method_ids
				journal_currency = journal.currency_id or journal.company_id.currency_id
				payment = self.env['account.payment'].create({
					'payment_method_id': payment_methods and payment_methods[0].id or False,
					'payment_type': total < 0 and 'outbound' or 'inbound',
					'partner_id': expense.employee_id.address_home_id.commercial_partner_id.id,
					'partner_type': 'supplier',
					'journal_id': journal.id,
					'payment_date': expense.date,
					'state': 'reconciled',
					'currency_id': diff_currency_p and expense.currency_id.id or journal_currency.id,
					'amount': diff_currency_p and abs(total_currency) or abs(total),
					'name': expense.name,
				})
				payment_id = payment.id
			else:
				if not expense.employee_id.address_home_id:
					raise UserError(_("No Home Address found for the employee %s, please configure one.") % (expense.employee_id.name))
				emp_account = expense.employee_id.address_home_id.property_account_payable_id.id

			aml_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
			move_lines.append({
					'type': 'dest',
					'name': aml_name,
					'price': total,
					'account_id': emp_account,
					'date_maturity': acc_date,
					'amount_currency': diff_currency_p and total_currency or False,
					'currency_id': diff_currency_p and expense.currency_id.id or False,
					'payment_id': payment_id,
					'expense_id': expense.id,
					})

			#convert eml into an osv-valid format
			lines = [(0, 0, expense._prepare_move_line(x)) for x in move_lines]
			move.with_context(dont_create_taxes=True).write({'line_ids': lines})
			expense.sheet_id.write({'account_move_id': move.id})
			if expense.payment_mode == 'company_account':
				expense.sheet_id.paid_expense_sheets()

		# OPTION TO POST BASED ON CONFIGURATION
		if move_status == 'post':
			for move in move_group_by_sheet.values():
				move.post()
		return True

class HrExpenseSheet(models.Model):
	_inherit = 'hr.expense.sheet'

	# EXTEND TO ADD UNPOSTED STATE
	state = fields.Selection([
		('submit', 'Submitted'),
		('approve', 'Approved'),
		('unpost', 'Unposted'),
		('post', 'Posted'),
		('done', 'Paid'),
		('cancel', 'Refused')
	])

	# EXTEND TO ALLOW EDIT ON APPROVED STATE
	expense_line_ids = fields.One2many('hr.expense', 'sheet_id', string='Expense Lines', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, copy=False)

	@api.multi
	def action_sheet_move_create(self):
		move_status = self.env['ir.config_parameter'].sudo().get_param('hr_expense.group_account_expense_status')
		if any(not expense.analytic_account_id or not expense.account_id for expense in self.expense_line_ids):
			raise UserError(_("Please specify analytic/expense account in expense report lines."))

		if any(sheet.state != 'approve' for sheet in self):
			raise UserError(_("You can only generate accounting entry for approved expense(s)."))

		if any(not sheet.journal_id for sheet in self):
			raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

		expense_line_ids = self.mapped('expense_line_ids')\
			.filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.user.company_id.currency_id).rounding))
		res = expense_line_ids.action_move_create()

		if not self.accounting_date:
			self.accounting_date = self.account_move_id.date

		if self.payment_mode == 'own_account' and expense_line_ids:
			# self.write({'state': 'post'})
			# OPTION TO POST BASED ON CONFIGURATION
			if move_status == 'post':
				self.write({'state': 'post'})
			else:
				self.write({'state': 'unpost'}) 
		else:
			self.write({'state': 'done'})
		return res

	# @api.multi
	# def update_move_analytic(self):
	# 	for record in self.expense_line_ids:
	# 		_logger.info("YEAHHH")
	# 		if self.account_move_id and record.analytic_account_id:
	# 			account_move_line = self.account_move_id.line_ids.filtered(lambda line: line.expense_id.id == record.id and line.account_id.id == record.account_id.id)
	# 			_logger.info(account_move_line)
	# 			if account_move_line:
	# 				account_move_line.write({'analytic_account_id': record.analytic_account_id.id})

	@api.multi
	def action_sheet_move_post(self):
		self.ensure_one()
		# self.update_move_analytic()
		self.account_move_id.post()
		self.write({'state': 'post'})
