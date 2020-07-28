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

        myids = self.env['account.invoice.line'].search([
            ('invoice_id.type','=','out_invoice'),
            ('invoice_id.date_invoice','>=',date_start),
            ('invoice_id.date_invoice','<=',date_end)
            ])

        iterator = 1
        sheet = workbook.add_worksheet()
#         sheet.write(0, 0, "Product")
#         sheet.write(0, 1, "Invoice Number")
#         sheet.write(0, 2, "State")
#         sheet.write(0, 3, "Date")
#         sheet.write(0, 4, "Salesperson")
#         sheet.write(0, 5, "Origin")
#         sheet.write(0, 6, "Account")
#         sheet.write(0, 7, "Analytic")
#         sheet.write(0, 8, "QTY Delivered")
#         sheet.write(0, 9, "QTY Invoiced")
#         sheet.write(0, 10, "Subtotal")
#         sheet.write(0, 11, "Total Cost")
#         sheet.write(0, 12, "Gross Margin")
#         sheet.write(0, 13, "Customer")
#         sheet.write(0, 14, "Due Date")
#         sheet.write(0, 15, "Last Payment Date")

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

#         for obj in myids:
#             report_name = obj.name
#             sheet.write(iterator, 0, obj.name)
#             sheet.write(iterator, 1, obj.invoice_id.number)
#             sheet.write(iterator, 2, obj.invoice_id.state)
#             sheet.write(iterator, 3, obj.invoice_id.date_invoice)
#             sheet.write(iterator, 4, obj.invoice_id.user_id.name)
#             sheet.write(iterator, 5, obj.invoice_id.origin)
#             sheet.write(iterator, 6, obj.account_id.display_name)
#             sheet.write(iterator, 7, obj.account_analytic_id.name)
#             if len(obj.sale_line_ids) > 0:
#                 mysline = obj.sale_line_ids[0]
#                 sheet.write(iterator, 8, mysline.qty_delivered)
#                 sheet.write(iterator, 9, mysline.qty_invoiced)
#                 sheet.write(iterator, 10, mysline.price_subtotal)
#                 sheet.write(iterator, 11, mysline.total_cost)
#                 sheet.write(iterator, 12, mysline.gross_margin)
#             else:
#                 sheet.write(iterator, 9, obj.quantity)
#                 sheet.write(iterator, 10, obj.price_subtotal)


#             sheet.write(iterator, 13, obj.invoice_id.partner_id.name)
#             sheet.write(iterator, 14, obj.invoice_id.date_due)
#             if len(obj.invoice_id.payment_move_line_ids) > 0:
#                 last_payment = obj.invoice_id.payment_move_line_ids[-1]
#                 sheet.write(iterator, 15, last_payment.date)
            
#             iterator = iterator + 1

        for obj in myids:
            report_name = obj.name
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
            
            move_lines = obj.invoice_id.move_id.line_ids
            have_sales = False
            sales_amount = 0
            cost_amount = 0
            if move_lines:
                for move in move_lines:
                    if move.product_id == obj.product_id:
                        if move.account_id.code in sales_account:
                            sales_amount += move.credit
                            have_sales = True
                        elif move.account_id.code in cost_account:
                            cost_amount += move.debit
                                
                for move in move_lines:
                    if move.product_id == obj.product_id:
                        if not move.account_id.code in sales_account and not have_sales:
                            sales_amount += move.credit
                            
            sheet.write(iterator, 10, sales_amount)
            sheet.write(iterator, 11, cost_amount)
            
#             if len(obj.sale_line_ids) > 0:
#                 mysline = obj.sale_line_ids[0]
#                 sheet.write(iterator, 12, mysline.gross_margin)
            gross_margin = sales_amount - cost_amount
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

 
        
 