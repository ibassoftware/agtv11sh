# -*- coding: utf-8 -*-

from datetime import datetime
import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    _inherit = 'account.invoice'

    total_amount_paid = fields.Float(
        string='Total Amount Paid', compute='_compute_total_paid')

    last_date_paid = fields.Date(
        string='Last Date Paid', compute='_compute_last_date_paid')

    last_delivery_date = fields.Date(
        string='Last Delivery Date', compute='_compute_last_delivery_date')

    total_analytic_acc_debit = fields.Float(
        string='Total Analytic Account Debit', compute='_compute_aa_debit')

    @api.depends('move_id')
    def _compute_aa_debit(self):
        for rec in self:
            if rec.move_id:
                debit = 0
                for line in rec.move_id.line_ids:
                    if line.analytic_account_id:
                        debit += line.debit
                    else:
                        debit = 0
                rec.total_analytic_acc_debit = debit

            else:
                rec.total_analytic_acc_debit = 0

    @api.depends('invoice_line_ids')
    def _compute_last_delivery_date(self):
        for record in self:
            for line in record['invoice_line_ids']:
                dates = []
                if line.delivery_date:
                    dates.append(line.delivery_date)
                    record['last_delivery_date'] = max(dates)
                else:
                    record['last_delivery_date'] = False

    @api.depends('residual')
    def _compute_total_paid(self):

        for rec in self:
            amount = 0
            payment_ids = self.env['account.payment'].sudo().search(
                [('invoice_ids', '=', rec.id), ('state', '=', 'posted')])

            if payment_ids:
                for payment in payment_ids:
                    amount += payment.amount

            rec.total_amount_paid = amount

    @api.depends('residual')
    def _compute_last_date_paid(self):
        for rec in self:
            payment_ids = self.env['account.payment'].sudo().search(
                [('invoice_ids', '=', rec.id), ('state', '=', 'posted')])

            if payment_ids:
                rec.last_date_paid = payment_ids[0].payment_date
