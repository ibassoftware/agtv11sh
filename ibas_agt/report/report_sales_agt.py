# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class SalesXlsx(models.AbstractModel):
    _name = 'report.ibas_agt.sales_report_xlsx'
    _description = 'AGT Sales Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        
        sales_account = ['501000','502000','50400']
        cost_account = ['510000', '520000','531000']
        matched_cost_line = []

        myids = self.env['account.invoice.line'].search([
            ('invoice_id.type','in',['out_invoice','out_refund']),
            ('invoice_id.date_invoice','>=',date_start),
            ('invoice_id.date_invoice','<=',date_end),
            ('invoice_id.state','in',['open','paid']),
            ])

        iterator = 1
        sheet = workbook.add_worksheet()

        sheet.write(0, 0, "Sales Order")
        sheet.write(0, 1, "Analytic")
        sheet.write(0, 2, "Salesperson")
        sheet.write(0, 3, "Account")
        sheet.write(0, 4, "Invoice Date")
        sheet.write(0, 5, "Due Date")
        sheet.write(0, 6, "Invoice Number")
        sheet.write(0, 7, "Customer")
        sheet.write(0, 8, "Description")
        sheet.write(0, 9, "Quantity")
        sheet.write(0, 10, "Sales")
        sheet.write(0, 11, "Cost of Sales")
        sheet.write(0, 12, "Gross Margin")
        sheet.write(0, 13, "Date Paid")
        sheet.write(0, 14, "Amount Paid")
        sheet.write(0, 15, "Invoice Total Amount")

        for obj in myids:
            report_name = obj.name
            account_code = obj.account_id.code
            include_line = account_code.startswith('50')
            if include_line:
                sheet.write(iterator, 0, obj.invoice_id.origin or '')
                sheet.write(iterator, 1, obj.account_analytic_id.name or '')
                sheet.write(iterator, 2, obj.invoice_id.user_id.name or '')
                sheet.write(iterator, 3, obj.account_id.display_name or '')
                sheet.write(iterator, 4, obj.invoice_id.date_invoice or '')
                sheet.write(iterator, 5, obj.invoice_id.date_due or '')
                sheet.write(iterator, 6, obj.invoice_id.move_name or '')
                sheet.write(iterator, 7, obj.invoice_id.partner_id.name or '')
                sheet.write(iterator, 8, obj.name or '')
                sheet.write(iterator, 9, obj.quantity)

                move_lines = obj.invoice_id.move_id.line_ids.filtered(lambda move: move.product_id == obj.product_id and move.account_id.code in cost_account)
#                 move_lines = obj.invoice_id.move_id.line_ids.filtered(lambda move: move.account_id.code in cost_account)
#                 sales_amount = obj.price_subtotal
                sales_amount = obj.price_subtotal_signed
                cost_amount = 0
                _logger.info("YOW")
                if len(move_lines) > 1:
                    debit_lines = move_lines.mapped('debit')
                    nearest_debit_line = min(debit_lines, key=lambda x:abs(int(x)-int(sales_amount)))
                    for move in move_lines:
                        if move.debit == nearest_debit_line and move.id not in matched_cost_line:
                            cost_amount += move.debit
                            matched_cost_line.append(move.id)
                else:
                     for move in move_lines:
                        if move.id not in matched_cost_line:
                            cost_amount += move.debit
                            matched_cost_line.append(move.id)

                gross_margin = sales_amount - cost_amount          
                if obj.invoice_id.type == 'out_refund':
                    sheet.write(iterator, 10, -abs(sales_amount))
                    sheet.write(iterator, 11, -abs(cost_amount))
                    sheet.write(iterator, 12, -abs(gross_margin))
                else:
                    sheet.write(iterator, 10, sales_amount)
                    sheet.write(iterator, 11, cost_amount)
                    sheet.write(iterator, 12, gross_margin)

                sheet.write(iterator, 13, obj.invoice_id.last_date_paid or '')
                sheet.write(iterator, 14, obj.invoice_id.total_amount_paid)
                sheet.write(iterator, 15, obj.invoice_id.amount_total_company_signed)

                iterator = iterator + 1
        
class SalesReportWizard(models.TransientModel):
    _name = 'ibas_agt.sales.report'
    

    # from_date = fields.Datetime(string='From', required=True)
    # to_date = fields.Datetime(string='To', required=True)
    from_date = fields.Date(string='From', required=True)
    to_date = fields.Date(string='To', required=True)  

    @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.from_date,
                'date_end': self.to_date,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `get_report_values()` and pass `data` automatically.
        return self.env.ref('ibas_agt.report_sales_xlsx').report_action(self, data=data)

 
        
 