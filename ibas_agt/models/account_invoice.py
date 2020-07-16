# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    _inherit = 'account.invoice'

    total_amount_paid = fields.Float(
        string='Total Amount Paid', compute='_compute_total_paid')

    last_date_paid = fields.Date(
        string='Last Date Paid', compute='_compute_last_date_paid')

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
