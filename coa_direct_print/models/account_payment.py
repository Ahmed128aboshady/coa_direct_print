# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    coa_balance_before = fields.Monetary(
        string='الرصيد قبل الدفعة / Balance Before',
        compute='_compute_coa_balances',
        currency_field='currency_id',
    )
    coa_balance_after = fields.Monetary(
        string='الرصيد بعد الدفعة / Balance After',
        compute='_compute_coa_balances',
        currency_field='currency_id',
    )

    @api.depends(
        'partner_id', 'amount', 'payment_type',
        'state', 'move_id', 'company_id',
    )
    def _compute_coa_balances(self):
        AML = self.env['account.move.line']

        for payment in self:
            partner = payment.partner_id.commercial_partner_id
            company = payment.company_id

            if not partner or not company or payment.payment_type == 'transfer':
                payment.coa_balance_before = 0.0
                payment.coa_balance_after = 0.0
                continue

            if payment.payment_type == 'inbound':
                acc_types = ['asset_receivable']
            else:
                acc_types = ['liability_payable']

            domain = [
                ('partner_id', 'child_of', partner.id),
                ('account_id.account_type', 'in', acc_types),
                ('parent_state', '=', 'posted'),
                ('company_id', '=', company.id),
            ]
            all_lines = AML.search(domain)
            current_balance = sum(all_lines.mapped('balance'))

            if payment.state in ('in_process', 'paid') and payment.move_id:
                pay_lines = all_lines.filtered(
                    lambda l, m=payment.move_id: l.move_id == m)
                pay_effect = sum(pay_lines.mapped('balance'))
                balance_after  = current_balance
                balance_before = current_balance - pay_effect
            else:
                balance_before = current_balance
                if payment.payment_type == 'inbound':
                    balance_after = current_balance - payment.amount
                else:
                    balance_after = current_balance + payment.amount

            payment.coa_balance_before = balance_before
            payment.coa_balance_after  = balance_after

    def action_coa_print_receipt(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/coa_direct_print.report_payment_receipt/%s?print=1' % self.id,
            'target': 'new',
        }

    def action_coa_print_statement(self):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        if not partner:
            raise UserError(_("This payment has no partner set."))
        return {
            'type': 'ir.actions.act_url',
            'url': '/report/html/coa_direct_print.report_partner_statement/%s?print=1' % partner.id,
            'target': 'new',
        }
