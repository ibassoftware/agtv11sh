
# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class IBASSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    total_cost = fields.Float(compute='_compute_total_cost', string='Cost', store=True)
    gross_margin = fields.Float(compute='_compute_gross_margin', string='Gross Margin', store=True)
    invoice_number = fields.Char(compute='_compute_invoice_number', string='Invoice Number', store =True)
    team_name = fields.Char(compute='_compute_team_name', string='Team', store=True)
    invoice_status = fields.Char(compute='_compute_invoice_number', string='Invoice Status', store =True)
    
    @api.depends('amt_invoiced','qty_delivered')
    def _compute_team_name(self):
        for rec in self:
            if rec.order_id is not False:
                rec.team_name = rec.order_id.team_id.name

    
    @api.depends('amt_invoiced')
    def _compute_invoice_number(self):
        for rec in self:
            if len(rec.invoice_lines) > 0:
                rec.invoice_number = rec.invoice_lines[0].invoice_id.number
                rec.invoice_status = rec.invoice_lines[0].invoice_id.state
    
    @api.depends('price_subtotal','total_cost')
    def _compute_gross_margin(self):
        for rec in self:
            rec.gross_margin = rec.price_subtotal + rec.total_cost
    
    @api.depends('qty_delivered', 'move_ids.value')
    @api.multi
    def _compute_total_cost(self):
        for rec in self:
            total = 0
            for moves in rec.move_ids:
                total = total + moves.value
            
            rec.total_cost = total
    
    # @api.multi
    # def compute_tc(self):
    #     for rec in self:
    #         total = 0
    #         for moves in rec.move_ids:
    #             total = total + moves.value
            
    #         rec.total_cost = total
        