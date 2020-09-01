from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools.safe_eval import safe_eval

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	delivery_receipt_no = fields.Char(
		string='Delivery Receipt No.', compute='_get_deliveries')
	bus_style = fields.Char(string='Business Style')
	delivery_receipt_manual_no = fields.Char(string='Delivery Receipt No.')

	@api.multi
	def _get_deliveries(self):
		for record in self:
			delivery_receipt_no = ''
			for invoice in record.invoice_line_ids:
				for sale in invoice.sale_line_ids:
					pickings = sale.mapped('order_id').mapped('picking_ids')
					for pick in pickings:
						if pick.state not in ['draft', 'cancel']:
							if not delivery_receipt_no:
								delivery_receipt_no = pick.name
							else:
								delivery_receipt_no += ', %s' % pick.name
			record.delivery_receipt_no = delivery_receipt_no


class AccountInvoiceLine(models.Model):
	_inherit = 'account.invoice.line'

	@api.multi
	def _get_description(self):
		for record in self:
			description_name = ''
			if record.name:
				description_name = record.name.replace('\n', ' ')
			record.description_name = description_name

	@api.model
	def _default_account_analytic(self):
		return self.env.ref('asiaglobal.analytic_account_undefined').id

	# EXTEND TO USE CUSTOM SALES DECIMAL ACCURACY
	price_unit = fields.Float(digits=dp.get_precision('Sale Product Price'))
	description_name = fields.Text(compute='_get_description')

	account_analytic_id = fields.Many2one(
		'account.analytic.account', string='Analytic Account', default=_default_account_analytic)
    
class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'
    
#     @api.model
#     def _get_invoice_number(self):
#         sequence_code = 'account.payment.customer.refund'
#         return self.env['ir.sequence'].with_context(ir_sequence_date=self.date_invoice).next_by_code(sequence_code)
    
#     invoice_number = fields.Char(string='Invoice Number', default=_get_invoice_number)
    sale_refund = fields.Boolean(compute='_get_refund_type')
    
    @api.depends('date_invoice')
    @api.one
    def _get_refund_type(self):
        sale_refund = False
        invoice_id = self.env['account.invoice'].browse(self._context.get('active_id',False))
        if invoice_id.type == 'out_invoice':
            sale_refund = True
        self.sale_refund = sale_refund
    
    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'cancel']:
                    raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(_('Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)
                
                if form.sale_refund:
                    sequence_code = 'account.payment.customer.refund'
                    move_name = self.env['ir.sequence'].with_context(ir_sequence_date=form.date_invoice).next_by_code(sequence_code)
                    
                    refund.write({
                        'move_name': move_name,
                    })

                created_inv.append(refund.id)
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                    to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
                    if mode == 'modify':
                        invoice = inv.read(inv_obj._get_refund_modify_read_fields())
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                        })
                        for field in inv_obj._get_refund_common_fields():
                            if inv_obj._fields[field].type == 'many2one':
                                invoice[field] = invoice[field] and invoice[field][0]
                            else:
                                invoice[field] = invoice[field] or False
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
                         inv.type == 'out_refund' and 'action_invoice_tree1' or \
                         inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
                         inv.type == 'in_refund' and 'action_invoice_tree2'
                # Put the reason in the chatter
                subject = _("Credit Note")
                body = description
                refund.message_post(body=body, subject=subject)
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True