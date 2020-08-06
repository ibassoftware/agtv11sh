from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class IbasAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _default_account_analytic(self):
        return self.env.ref('asiaglobal.analytic_account_undefined').id

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account', default=_default_account_analytic)
