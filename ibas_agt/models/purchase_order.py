# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
import datetime
_logger = logging.getLogger(__name__)


class IBASPO(models.Model):
    _inherit = 'purchase.order'

    customer_id = fields.Many2one('res.partner', string='PO For Customer')

    order_status = fields.Selection([('open', 'Open'), ('partial', 'Partial'), (
        'close', 'Closed')], default='open', compute='_compute_order_status')

    remarks_status = fields.Selection(
        [('new', 'New'), ('overdue', 'Overdue')], default='new', compute='_compute_remarks_status')

    order_store = fields.Selection(
        related='order_status', string='Order Store', store="True")
    remarks_store = fields.Selection(
        related='remarks_status', string='Remarks Store', store="True")

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

    @api.depends('date_planned')
    def _compute_remarks_status(self):
        for rec in self:
            if rec.date_planned and rec.date_planned < fields.Datetime.now():
                rec.remarks_status = 'overdue'
            else:
                rec.remarks_status = 'new'
