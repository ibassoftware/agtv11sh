# # -*- RCS -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = "Purchase Requisition"
    _inherit = ['material.purchase.requisition', 'mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    customer_id = fields.Many2one('res.partner', string='PR for Customer', track_visibility='always')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id.id)
    
    
    # OVERRIDE FUNCTION
    # ADD CURRENCY AND PR FOR CUSTOMER TO PURCHASE ORDER GENERATED
    @api.multi
    def create_picking_po(self):
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']

        for line in self.requisition_line_ids:
            if line.requisition_action == 'purchase_order':
                for vendor in line.vendor_id:
                    pur_order = purchase_order_obj.search([('requisition_po_id','=',self.id),('partner_id','=',vendor.id)])
                    if pur_order:
                        po_line_vals = {
                                        'product_id' : line.product_id.id,
                                        'product_qty': line.qty,
                                        'name' : line.description,
                                        'price_unit' : line.product_id.list_price,
                                        'date_planned' : datetime.now(),
                                        'product_uom' : line.uom_id.id,
                                        'order_id' : pur_order.id,
                        }
                        purchase_order_line = purchase_order_line_obj.create(po_line_vals)
                    else:
                        vals = {
                                'partner_id' : vendor.id,
                                'date_order' : datetime.now(),
                                'requisition_po_id' : self.id,
                                'state' : 'draft',
                                'picking_type_id' : self.internal_picking_id.id,
                                'customer_id': self.customer_id.id,
                                'currency_id': self.currency_id.id,
                                
                        }
                        purchase_order = purchase_order_obj.create(vals)
                        po_line_vals = {
                                        'product_id' : line.product_id.id,
                                        'product_qty': line.qty,
                                        'name' : line.description,
                                        'price_unit' : line.product_id.list_price,
                                        'date_planned' : datetime.now(),
                                        'product_uom' : line.uom_id.id,
                                        'order_id' : purchase_order.id,
                        }
                        purchase_order_line = purchase_order_line_obj.create(po_line_vals)
            else:
           
                for vendor in line.vendor_id:
                    stock_picking_obj = self.env['stock.picking']
                    stock_move_obj = self.env['stock.move']
                    stock_picking_type_obj = self.env['stock.picking.type']
                    picking_type_ids = stock_picking_type_obj.search([('code','=','internal')])
                    
                    #employee_id = self.env['hr.employee'].search('id','=',self.env.user.name)
                    pur_order = stock_picking_obj.search([('requisition_picking_id','=',self.id),('partner_id','=',vendor.id)])
                    if pur_order:
                        pic_line_val = {
                                        'name': line.product_id.name,
                                        'product_id' : line.product_id.id,
                                        'product_uom_qty' : line.qty,
                                        'picking_id' : stock_picking.id,
                                        'product_uom' : line.uom_id.id,
                                        'location_id': self.source_location_id.id,
                                        'location_dest_id' : self.destination_location_id.id,

                        }
                        stock_move = stock_move_obj.create(pic_line_val)

                    else:
                        pick_id = False
                        if picking_type_ids:
                            pick_id = picking_type_ids[0].id
                        else:
                            raise UserError(_('Picking Type internal Is not defined.\n Create  \
                                One internal picking. !!'))

                        val = {
                                'partner_id' : vendor.id,
                                'location_id'  : self.source_location_id.id,
                                'location_dest_id' : self.destination_location_id.id,
                                'picking_type_id' : pick_id,
                                'company_id': self.env.user.company_id.id,
                                'requisition_picking_id' : self.id,
				# 'material_requisition_id':self.job_order_id and self.job_order_id.id,
				# 'job_order_user_id':self.job_order_user_id and self.job_order_user_id.id,
				# 'construction_project_id':self.construction_project_id and self.construction_project_id.id,
				# 'analytic_account_id':self.account_analytic_id and self.account_analytic_id.id,
                        }
                        stock_picking = stock_picking_obj.create(val)
                        pic_line_val = {
                                        'partner_id' : vendor.id,
                                        'name': line.product_id.name,
                                        'product_id' : line.product_id.id,
                                        'product_uom_qty' : line.qty,
                                        'product_uom' : line.uom_id.id,
                                        'location_id': self.source_location_id.id,
                                        'location_dest_id' : self.destination_location_id.id,
                                        'picking_id' : stock_picking.id,


                        }
                        stock_move = stock_move_obj.create(pic_line_val)

        res = self.write({
                            'state':'po_created',
                        })
        return res
    
class RequisitionLine(models.Model):
    _inherit = "requisition.line"
    
    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(RequisitionLine, self).onchange_product_id()
        self.description = self.product_id.description_purchase or self.product_id.description_sale
        return result