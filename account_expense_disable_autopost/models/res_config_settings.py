from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	group_account_expense_status = fields.Selection([
		('draft', 'Set to draft'),
		('post', 'Set to posted')], default='draft',
		string="Status of Expense Account Entries",
		help="Option to post entries automatically or not.")
	
	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		res.update(
			group_account_expense_status=self.env['ir.config_parameter'].sudo().get_param('hr_expense.group_account_expense_status')
		)
		return res
	
	@api.multi
	def set_values(self):
		super(ResConfigSettings, self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('hr_expense.group_account_expense_status', self.group_account_expense_status)