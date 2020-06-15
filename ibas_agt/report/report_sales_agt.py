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


        myids = self.env['account.invoice.line'].search([
            ('invoice_id.type','=','out_invoice'),
            ('invoice_id.date_invoice','>=',date_start),
            ('invoice_id.date_invoice','<=',date_end)
            ])

        iterator = 1
        sheet = workbook.add_worksheet()
        sheet.write(0, 0, "Product")
        sheet.write(0, 1, "Invoice Number")
        sheet.write(0, 2, "State")
        sheet.write(0, 3, "Date")
        sheet.write(0, 4, "Salesperson")
        sheet.write(0, 5, "Origin")
        sheet.write(0, 6, "Account")
        sheet.write(0, 7, "Analytic")
        sheet.write(0, 8, "QTY Delivered")
        sheet.write(0, 9, "QTY Invoiced")
        sheet.write(0, 10, "Subtotal")
        sheet.write(0, 11, "Total Cost")
        sheet.write(0, 12, "Gross Margin")
        sheet.write(0, 13, "Customer")
        sheet.write(0, 14, "Due Date")
        sheet.write(0, 15, "Last Payment Date")
        for obj in myids:
            report_name = obj.name
            sheet.write(iterator, 0, obj.name)
            sheet.write(iterator, 1, obj.invoice_id.number)
            sheet.write(iterator, 2, obj.invoice_id.state)
            sheet.write(iterator, 3, obj.invoice_id.date_invoice)
            sheet.write(iterator, 4, obj.invoice_id.user_id.name)
            sheet.write(iterator, 5, obj.invoice_id.origin)
            sheet.write(iterator, 6, obj.account_id.display_name)
            sheet.write(iterator, 7, obj.account_analytic_id.name)
            if len(obj.sale_line_ids) > 0:
                mysline = obj.sale_line_ids[0]
                sheet.write(iterator, 8, mysline.qty_delivered)
                sheet.write(iterator, 9, mysline.qty_invoiced)
                sheet.write(iterator, 10, mysline.price_subtotal)
                sheet.write(iterator, 11, mysline.total_cost)
                sheet.write(iterator, 12, mysline.gross_margin)

            sheet.write(iterator, 13, obj.invoice_id.partner_id.name)
            sheet.write(iterator, 14, obj.invoice_id.date_due)
            if len(obj.invoice_id.payment_move_line_ids) > 0:
                last_payment = obj.invoice_id.payment_move_line_ids[-1]
                sheet.write(iterator, 15, last_payment.date)
            
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

 
        
 