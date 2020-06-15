# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPublicCategoryStyle(models.Model):
    _name = 'product.public.category.style'

    name = fields.Char(string='Style Name', required=True)
    html_class = fields.Char(string='HTML Classes')


class product_public_category(models.Model):
    _inherit = 'product.public.category'

    website_size_x = fields.Integer('Size X', default=1)
    website_size_y = fields.Integer('Size Y', default=1)
    website_style_ids = fields.Many2many('product.public.category.style', string='Styles')
