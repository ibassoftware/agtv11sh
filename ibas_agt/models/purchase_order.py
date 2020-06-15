# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class IBASPO(models.Model):
    _inherit = 'purchase.order'

    customer_id = fields.Many2one('res.partner', string='PO For Customer')