# -*- coding: utf-8 -*-
import xlwt
from xlsxwriter.workbook import Workbook
#from cStringIO import StringIO
from io import BytesIO
import base64
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseWizard(models.Model):
    _name = 'wizard.reports'
    _description = 'purchase wizard'

    from_date = fields.Date(string='From', required=True)
    to_date = fields.Date(string='To', required=True)
    order_status = fields.Selection([('open', 'Open'), ('partial', 'Partial'), (
        'close', 'Closed')], default='open', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier', '=', True)])

    @api.multi
    def generate_excel_report(self):

        date_start = self.from_date
        date_end = self.to_date
        state = self.order_status
        partner_id = self.partner_id

        if date_start > date_end:
            raise ValidationError(
                _("From Date cannot be set before to Date."))
        else:
            if partner_id:
                orders = self.env['purchase.order'].search([
                    ('order_status', '=', state),
                    ('date_order', '>=', date_start),
                    ('date_order', '<=', date_end),
                    ('partner_id', '=', partner_id.id),
                ])
            else:
                orders = self.env['purchase.order'].search([
                    ('order_status', '=', state),
                    ('date_order', '>=', date_start),
                    ('date_order', '<=', date_end),
                ])
            

            # orders = self.env['purchase.order'].browse(
            #    self._context.get('active_ids', list()))

            filename = 'purchase.xls'
            workbook = xlwt.Workbook(encoding="UTF-8")
            worksheet = workbook.add_sheet('Sheet 1')
            style = xlwt.easyxf('font: bold off, name Arial')

            style2 = xlwt.XFStyle()
            style2.num_format_str = '#,##0.00'

            style_header = xlwt.easyxf(
                'font: bold True, name Arial; borders: bottom_color black, bottom medium; align: horiz center')
            worksheet.col(1).width = 1000
            worksheet.col(2).width = 10000
            worksheet.col(3).width = 5000
            worksheet.col(4).width = 5000
            worksheet.col(5).width = 5000
            worksheet.col(6).width = 3000
            worksheet.col(7).width = 5000
            worksheet.col(9).width = 4000
            worksheet.col(10).width = 4000

            worksheet.write(0, 2, 'Name', style_header)
            worksheet.write(0, 3, 'PO No.', style_header)
            worksheet.write(0, 4, 'PO Date', style_header)
            worksheet.write(0, 5, 'Due Date', style_header)
            worksheet.write(0, 6, 'Amount', style_header)
            worksheet.write(0, 7, 'Foreign Amount', style_header)
            worksheet.write(0, 8, 'Currency', style_header)
            worksheet.write(0, 9, 'Order Status', style_header)
            worksheet.write(0, 10, 'Remarks', style_header)

            n = 2
            i = 1
            custom_order = {}
            for order in orders:
                custom_order['partner_id'] = order.partner_id.name
                custom_order['po_no'] = order.name
                custom_order['date_order'] = order.date_order
                custom_order['date_planned'] = order.date_planned
                #custom_order['date_due'] = order.date_due
                #custom_order['debit'] = order.invoice_ids.total_analytic_acc_debit
                custom_order['amount_total'] = order.amount_total
                custom_order['currency_id'] = order.currency_id.name
                custom_order['order_status'] = order.order_status
                custom_order['remarks_status'] = order.remarks_status

                if order.date_due == False:
                    custom_order['date_due'] = " "
                else:
                    custom_order['date_due'] = order.date_due

                if order.currency_id.id == 37:
                    custom_order['debit'] = order.amount_total
                else:
                    sum_aa = 0.0
                    for inv in order.invoice_ids:
                        sum_aa += inv.total_analytic_acc_debit
                    custom_order['debit'] = sum_aa
                    #custom_order['debit'] = order.invoice_ids.total_analytic_acc_debit

                worksheet.write(n, 1, i, style)
                worksheet.write(n, 2, custom_order['partner_id'], style)
                worksheet.write(n, 3, custom_order['po_no'], style)
                worksheet.write(n, 4, custom_order['date_order'], style)
                worksheet.write(n, 5, custom_order['date_due'], style)
                worksheet.write(n, 6, custom_order['debit'], style2)
                worksheet.write(n, 7, custom_order['amount_total'], style2)
                worksheet.write(n, 8, custom_order['currency_id'], style)
                worksheet.write(
                    n, 9, custom_order['order_status'].upper(), style)
                worksheet.write(
                    n, 10, custom_order['remarks_status'].upper(), style)

                n += 1
                i += 1
            #worksheet.write(5, 1, 'Vendor', style)
            #fp = StringIO()
            fp = BytesIO()
            workbook.save(fp)
            record_id = self.env['purchase.report.out'].create(
                {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename},)
            fp.close()

            return {'view_mode': 'form',
                    'res_id': record_id.id,
                    'res_model': 'purchase.report.out',
                    'view_type': 'form',
                    'type': 'ir.actions.act_window',
                    'context': self.env.context,
                    'target': 'new',
                    }


class PurchaseReportOut(models.Model):
    _name = "purchase.report.out"

    excel_file = fields.Binary('excel file', readonly=True)
    file_name = fields.Char('Excel File', size=64)
