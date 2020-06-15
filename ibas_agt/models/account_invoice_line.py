# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    default_sales = fields.Many2one('sale.order.line',compute='_compute_default_sales', string='Default SO Line')
    order_reference = fields.Char(string='Order Reference') 
    customer_id = fields.Many2one('res.partner', string='Customer')
    
    
    @api.depends('sale_line_ids')
    def _compute_default_sales(self):
        for rec in self:
            if len(rec.sale_line_ids) > 0:
                rec.default_sales = rec.sale_line_ids[0].id
                