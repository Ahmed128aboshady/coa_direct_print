# -*- coding: utf-8 -*-
from odoo import api, models


class PartnerStatementReport(models.AbstractModel):
    _name = 'report.coa_direct_print.report_partner_statement'
    _description = 'Partner Account Statement (Receivable + Payable)'

    @api.model
    def _get_report_values(self, docids, data=None):
        partners = self.env['res.partner'].browse(docids)
        statements = {}

        for partner in partners:
            # Determine which account types to include:
            #   customer  → asset_receivable
            #   supplier  → liability_payable
            #   both      → include both
            acc_types = []
            if partner.customer_rank > 0:
                acc_types.append('asset_receivable')
            if partner.supplier_rank > 0:
                acc_types.append('liability_payable')
            if not acc_types:
                # Fallback: show both if ranks are zero (e.g. just created)
                acc_types = ['asset_receivable', 'liability_payable']

            amls = self.env['account.move.line'].search([
                ('partner_id', 'child_of', partner.commercial_partner_id.id),
                ('account_id.account_type', 'in', acc_types),
                ('parent_state', '=', 'posted'),
                ('company_id', '=', self.env.company.id),
            ], order='date asc, id asc')

            lines = []
            balance = 0.0
            total_debit = 0.0
            total_credit = 0.0

            for aml in amls:
                balance      += aml.debit - aml.credit
                total_debit  += aml.debit
                total_credit += aml.credit
                lines.append({
                    'date':      aml.date,
                    'move_name': aml.move_id.name or '',
                    'label':     aml.name or aml.move_id.ref or '',
                    'due_date':  aml.date_maturity,
                    'debit':     aml.debit,
                    'credit':    aml.credit,
                    'balance':   balance,
                })

            statements[partner.id] = {
                'lines':        lines,
                'total_debit':  total_debit,
                'total_credit': total_credit,
                'balance':      balance,
                'acc_types':    acc_types,
            }

        return {
            'doc_ids':   docids,
            'doc_model': 'res.partner',
            'docs':      partners,
            'statements': statements,
            'company':   self.env.company,
            'currency':  self.env.company.currency_id,
        }
