# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
import datetime
_logger = logging.getLogger(__name__)


class IBASPO(models.Model):
    _inherit = 'purchase.order'

    customer_id = fields.Many2one('res.partner', string='PO For Customer')

    order_status = fields.Selection([('open', 'Open'), ('partial', 'Partial'), (
        'close', 'Closed')], compute='_compute_order_status')

    remarks_status = fields.Selection(
        [('new', 'New'), ('overdue', 'Overdue')], default='new', compute='_compute_remarks_status')

    order_store = fields.Selection(
        related='order_status', string='Order Store', store="True")
    remarks_store = fields.Selection(
        related='remarks_status', string='Remarks Store', store="True")

    date_due = fields.Date(string='Due Date')

    @api.onchange('payment_term_id', 'date_order')
    def _onchange_payment_term_date(self):
        date_order = self.date_order
        if not date_order:
            date_order = fields.Date.context_today(self)
        if self.payment_term_id:
            pterm = self.payment_term_id
            pterm_list = pterm.with_context(currency_id=self.company_id.currency_id.id).compute(
                value=1, date_ref=date_order)[0]
            self.date_due = max(line[0] for line in pterm_list)
        elif self.date_due and (date_order > self.date_due):
            self.date_due = date_order

    # @api.depends('invoice_ids')
    # def _compute_date_due(self):
    #    for rec in self:
    #        if rec.invoice_ids:
    #            rec.date_due = rec.invoice_ids[0].date_due
    #        else:
    #            rec.date_due = False

    @api.depends('order_line.qty_received')
    def _compute_order_status(self):
        for rec in self:
            stock_pick = self.env['stock.picking'].search(
                [('purchase_id', '=', rec.id)])

            if rec.order_line:
                for line in rec.order_line:
                    if line.qty_received == 0:
                        rec.order_status = 'open'

            if stock_pick:
                for pick in stock_pick:
                    if pick.state == 'done':
                        for line in rec.order_line:
                            if line.product_qty != line.qty_received:
                                rec.order_status = 'partial'

            if rec.order_line:
                prod_qty = 0
                qty_received = 0
                for line in rec.order_line:
                    if line.qty_received >= 1:
                        prod_qty += line.product_qty
                        qty_received += line.qty_received

                if prod_qty == qty_received and line.qty_received >= 1:
                    rec.order_status = 'close'

    @api.depends('date_due')
    def _compute_remarks_status(self):
        for rec in self:
            if rec.date_due and rec.date_due < fields.Datetime.now():
                rec.remarks_status = 'overdue'
            else:
                rec.remarks_status = 'new'
