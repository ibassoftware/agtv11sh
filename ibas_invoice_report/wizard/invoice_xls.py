# -*- coding: utf-8 -*-
import xlwt
from xlsxwriter.workbook import Workbook
# from cStringIO import StringIO
from io import BytesIO
import base64
from odoo import api, fields, models, _


class InvoiceWizard(models.Model):
    _name = 'invoice.wizard.reports'
    _description = 'invoice wizard'

    @api.multi
    def generate_excel_report(self):
        invoices = self.env['account.invoice'].browse(
            self._context.get('active_ids', list()))

        filename = 'invoice.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        worksheet = workbook.add_sheet('Sheet 1')
        style = xlwt.easyxf('font: bold off, name Arial')
        style_header = xlwt.easyxf(
            'font: bold True, name Arial; borders: bottom_color black, bottom medium; align: horiz center')
        worksheet.col(1).width = 1000
        worksheet.col(2).width = 8000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 4000
        worksheet.col(7).width = 4000
        worksheet.col(8).width = 4000
        worksheet.col(9).width = 8000
        worksheet.col(10).width = 8000
        worksheet.col(11).width = 5000
        worksheet.col(12).width = 2000
        worksheet.col(13).width = 5000
        worksheet.col(14).width = 3000

        worksheet.write(0, 2, 'Sales Person', style_header)
        worksheet.write(0, 3, 'Analytic Account', style_header)
        worksheet.write(0, 4, 'Date of Invoice', style_header)
        worksheet.write(0, 5, 'Date Delivery', style_header)
        worksheet.write(0, 6, 'Date Paid', style_header)
        worksheet.write(0, 7, 'Due Date', style_header)
        worksheet.write(0, 8, 'Invoice Number', style_header)
        worksheet.write(0, 9, 'Customer Name', style_header)
        worksheet.write(0, 10, 'Description', style_header)
        worksheet.write(0, 11, 'Item Code', style_header)
        worksheet.write(0, 12, 'Quantity', style_header)
        worksheet.write(0, 13, 'Amount of Invoice', style_header)
        worksheet.write(0, 14, 'Amount Paid', style_header)

        n = 1
        i = 1
        custom_value = {}
        for rec in invoices:
            invoices = []
            for line in rec.invoice_line_ids:
                product = {}
                product['account_analytic_id'] = line.account_analytic_id.name
                product['name'] = line.name
                product['product_id'] = line.product_id.name
                product['quantity'] = line.quantity
                invoices.append(product)

            custom_value['invoices'] = invoices
            custom_value['user_id'] = rec.user_id.name
            custom_value['date_invoice'] = rec.date_invoice
            custom_value['last_date_paid'] = rec.last_date_paid
            custom_value['date_due'] = rec.date_due
            custom_value['move_name'] = rec.move_name
            custom_value['partner_id'] = rec.partner_id.name
            custom_value['amount_total'] = rec.amount_total
            custom_value['total_amount_paid'] = rec.total_amount_paid

            for product in custom_value['invoices']:
                worksheet.write(n, 1, i, style)
                worksheet.write(n, 2, custom_value['user_id'], style)
                worksheet.write(n, 3, product['account_analytic_id'], style)
                worksheet.write(n, 4, custom_value['date_invoice'], style)
                worksheet.write(n, 6, custom_value['last_date_paid'], style)
                worksheet.write(n, 7, custom_value['date_due'], style)
                worksheet.write(n, 8, custom_value['move_name'], style)
                worksheet.write(n, 9, custom_value['partner_id'], style)
                worksheet.write(n, 10, product['name'], style)
                worksheet.write(n, 11, product['product_id'], style)
                worksheet.write(n, 12, product['quantity'], style)
                worksheet.write(n, 13, custom_value['amount_total'], style)
                worksheet.write(
                    n, 14, custom_value['total_amount_paid'], style)

                n += 1
                i += 1

        # fp = StringIO()
        fp = BytesIO()
        workbook.save(fp)
        record_id = self.env['invoice.report.out'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename},)
        fp.close()

        return {'view_mode': 'form',
                'res_id': record_id.id,
                'res_model': 'invoice.report.out',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
                }


class invoiceReportOut(models.Model):
    _name = "invoice.report.out"

    excel_file = fields.Binary('excel file', readonly=True)
    file_name = fields.Char('Excel File', size=64)
