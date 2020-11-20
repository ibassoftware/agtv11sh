from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    # NEW FIELDS
    jo_id = fields.Many2one('asiaglobal.job_order', string='Job Order')
    sale_source = fields.Selection([
        ('exhibit', 'Exhibit'),
        ('new', 'New Client'),
        ('referral', 'Referral'),
        ('saturation', 'Saturation'),
        ('old', 'Old Customer'),
        ('other', 'Others'),
    ], string='Source of Sale')

    # OVERRIDE
    validity_date = fields.Date(states={'draft': [('readonly', False)], 'manager_approval': [('readonly', False)], 'admin_approval': [
                                ('readonly', False)], 'approved': [('readonly', False)], 'sent': [('readonly', False)]},)
    confirmation_date = fields.Datetime(string='Confirmation Date', readonly=False, index=True,
                                        help="Date on which the sales order is confirmed.", oldname="date_confirm", copy=False)

    invoice_status = fields.Selection(selection_add=[('invoice', 'Invoiced')])

    @api.depends('state', 'order_line.invoice_status', 'invoice_ids')
    def _get_invoiced(self,):
        order = super(SaleOrder, self)._get_invoiced()

        if self.invoice_ids:
            invoice_status = 'invoice'

        elif self.confirmation_date:
            invoice_status = 'to invoice'

        else:
            invoice_status = 'no'

        self.update({
            'invoice_status': invoice_status
        })
        return order
    
    @api.multi
    def update_invoice_status(self):
        for record in self:
            record._get_invoiced()
        return True
    
    @api.multi
    def action_confirm(self):
        for sale in self:
            for line in sale.order_line:
                if line.product_id.sale_line_warn != 'no-message':
                    title = _("Warning for %s") % line.product_id.name
                    message = line.product_id.sale_line_warn_msg
                    raise UserError(_('Cannot confirm order! \n %s \n %s') %(title, message))
        result = super(SaleOrder, self).action_confirm()
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit = fields.Float(digits=dp.get_precision('Sale Product Price'))

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        vals = {}
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        name = product.default_code or ''
        if product.description_sale:
            name += '\n' + product.description_sale
        # If no description and item code
        if not name:
            name = product.name
        vals['name'] = name
        self.update(vals)
        return result
