# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from datetime import date

_logger = logging.getLogger(__name__)

class IBASStockMove(models.Model):
    _inherit = 'stock.move'

    price_before_lc = fields.Float(compute='_compute_price_before_lc', string='Unit Price before LC', store= True)
    # value_before_lc = fields.Float(compute='_compute_price_before_lc', string='Value before LC', store= True)
    value_after_lc = fields.Float(compute='_compute_price_before_lc', string='Value after LC', store= True)
    analytic_id = fields.Many2one('account.analytic.account', compute='_compute_price_before_lc', string='Analytic Account', store= True)
    stock_age = fields.Integer(compute='_compute_stock_age', string='Stock Age in Days')
    supplier_name = fields.Char(compute='_compute_supplier_name', string='Supplier', store=True)
    customer_name = fields.Char(compute='_compute_supplier_name', string='Customer')
    
    @api.depends('purchase_line_id')
    def _compute_supplier_name(self):
        for rec in self:
            rec.supplier_name = rec.purchase_line_id.partner_id.name
            rec.original_currency = rec.purchase_line_id.currency_id.name
            rec.original_currency_amount = rec.purchase_line_id.price_unit
            rec.customer_name = rec.purchase_line_id.order_id.customer_id.name   

    original_currency = fields.Char(compute='_compute_supplier_name', string='Original Currency')
    original_currency_amount = fields.Float(compute='_compute_supplier_name', string='OC Amount')
    
    @api.depends('date')
    def _compute_stock_age(self):
        for rec in self:
            elapsed_delta = date.today() - fields.Datetime.from_string(rec.date).date()
            rec.stock_age = elapsed_delta.days
    
    
    @api.depends('landed_cost_value', 'value', 'quantity_done')
    def _compute_price_before_lc(self):
        for rec in self:
            if rec.purchase_line_id:
                rec.analytic_id = rec.purchase_line_id.account_analytic_id.id
            else:
                rec.analytic_id = rec.analytic_account_id.id
            if rec.landed_cost_value > 0:
                # rec.price_before_lc = (rec.value - rec.landed_cost_value) / rec.quantity_done
                # rec.price_before_lc = rec.value / rec.quantity_done
                # rec.value_before_lc = rec.value - rec.landed_cost_value
                if rec.quantity_done > 0:
                    rec.price_before_lc = rec.value / rec.quantity_done
                rec.value_after_lc = rec.value + rec.landed_cost_value
    
    # @api.onchange('value')
    # def _onchange_value(self):
    #     for rec in self:
    #         if rec.sale_line_id != False:
    #             rec.sale_line_id.compute_tc()
            
    

