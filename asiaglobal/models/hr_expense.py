from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from werkzeug import url_encode


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = 'hr.expense.sheet.register.payment.wizard'

    def _get_payment_value(self):
        """ Hook for extension """
        return {
            'payment_date': self.payment_date,
            'memo': self.communication
        }

    @api.multi
    def expense_post_payment(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)

        # Create payment and post it
        payment = self.env['account.payment'].create(self._get_payment_vals())
        payment.post()

        # expense update
        expense_sheet.update(self._get_payment_value())

        # Log the payment in the chatter
        body = (_("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") %
                (payment.amount, payment.currency_id.symbol, url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, expense_sheet.name))
        expense_sheet.message_post(body=body)

        # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
        account_move_lines_to_reconcile = self.env['account.move.line']
        for line in payment.move_line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id.internal_type == 'payable' and not line.reconciled:
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()

        return {'type': 'ir.actions.act_window_close'}


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    state = fields.Selection([('draft', 'For Approval'),
                              ('check', 'Checking'),
                              ('submit', 'For Head Approval'),
                              ('approve', 'Approved'),
                              ('post', 'Posted'),
                              ('done', 'Paid'),
                              ('cancel', 'Refused')],
                             string='Status', index=True, readonly=True,
                             track_visibility='onchange', copy=False, default='draft',
                             required=True, help='Expense Report State')

    approving_manager_id = fields.Many2one(
        'hr.employee',
        string='Approving Manager',
    )

    checked_by_id = fields.Many2one(
        'hr.employee',
        string='Checked by:',
    )
    expense_type = fields.Selection([('reimbursement', 'REIMBURSEMENT'), (
        'travel_abroad', 'TRAVEL ABROAD'), ('liquidation', 'LIQUIDATION')], string="Expense")
    amount_of_cash = fields.Float(string="Amount of Cash Advance")

    expense_line_ids = fields.One2many(
        states={'done': [('readonly', True)], 'post': [('readonly', True)]})

    payment_date = fields.Date(string='Payment Date')
    memo = fields.Char(string='Memo')

    remarks = fields.Char(string="Remarks")

    @api.multi
    def for_approve(self):
        self.write({'state': 'check'})

    @api.multi
    def for_checking(self):
        self.write({'state': 'submit'})
        
    @api.multi
    def reset_expense_sheets(self):
        self.mapped('expense_line_ids').write({'is_refused': False})
        return self.write({'state': 'draft'})

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    unit_amount = fields.Float(digits=dp.get_precision('Sale Product Price'))
