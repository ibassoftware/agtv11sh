from odoo import models, fields, api, _
from num2words import num2words
from odoo.tools.misc import formatLang, format_date

import logging
_logger = logging.getLogger(__name__)

INV_LINES_PER_STUB = 9

class AccountRegisterPayments(models.TransientModel):
	_inherit = "account.register.payments"
	
	@api.onchange('amount')
	def _onchange_amount(self):
		if hasattr(super(AccountRegisterPayments, self), '_onchange_amount'):
			super(AccountRegisterPayments, self)._onchange_amount()
		whole = num2words(int(self.amount)) + ' Pesos '
		whole = whole.replace(' and ',' ')
		if "." in str(self.amount): # quick check if it is decimal
			decimal_no = str(round(self.amount, 2)).split(".")[1]
			if len(decimal_no) == 1:
				decimal_no = decimal_no + "0"
			if decimal_no:
				whole = whole + "and " + decimal_no + '/100'
		whole = whole.replace(',','')
		self.check_amount_in_words = whole.upper() + " ONLY"
		
	def _prepare_payment_vals(self, invoices):
		res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)
		res.update({
			'check_amount_in_words': self.check_amount_in_words,
			'check_manual_sequencing': self.check_manual_sequencing,
		})
		return res

class AccountPayment(models.Model):
	_inherit = 'account.payment'
	
	amount_in_words = fields.Char(string='Amount In Words', compute='_onchange_amount')
	
	@api.multi
	@api.onchange('amount','currency_id')
	def _onchange_amount(self):
		res = super(AccountPayment, self)._onchange_amount()
		for rec in self:
			whole = num2words(int(rec.amount)) + ' Pesos '
			whole = whole.replace(' and ',' ')
			if "." in str(rec.amount): # quick check if it is decimal
				decimal_no = str(round(rec.amount, 2)).split(".")[1]
				if len(decimal_no) == 1:
					decimal_no = decimal_no + "0"
				if decimal_no:
					whole = whole + "and " + decimal_no + '/100'
			whole = whole.replace(',','')
			# rec.amount_in_words = whole.upper() + " ONLY"
			rec.check_amount_in_words = whole.upper() + " ONLY"
		return res
	
	@api.multi
	def compute_check_amount_in_words(self):
		for record in self:
			if not record.check_amount_in_words or not record.amount_in_words:
				record._onchange_amount()
		return True
	
	# Override to remove asterisk
	def fill_line(self, amount_str):
		return amount_str
	
	def get_pages(self):
		stub_pages = self.make_stub_pages() or [False]
		multi_stub = self.company_id.us_check_multi_stub
		pages = []
		for i, p in enumerate(stub_pages):
			pages.append({
				'sequence_number': self.check_number\
					if (self.journal_id.check_manual_sequencing and self.check_number != 0)\
					else False,
				'payment_date': format_date(self.env, self.payment_date),
				'partner_id': self.partner_id,
				'partner_name': self.partner_id.name,
				'currency': self.currency_id,
				'state': self.state,
				'amount': formatLang(self.env, self.amount) if i == 0 else 'VOID',
				'amount_in_word': self.fill_line(self.check_amount_in_words) if i == 0 else 'VOID',
				'memo': self.communication,
				'stub_cropped': not multi_stub and len(self.invoice_ids) > INV_LINES_PER_STUB,
				# If the payment does not reference an invoice, there is no stub line to display
				'stub_lines': p,
			})
		return pages