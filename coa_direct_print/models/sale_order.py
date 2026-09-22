# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _coa_direct_print_url(self, report_key):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/coa_direct_print/print/sale.order/%s/%s' % (self.id, report_key),
            'target': 'new',
        }

    def action_coa_print_order(self):
        """Direct print of the Quotation / Sale Order PDF."""
        return self._coa_direct_print_url('so')

    def action_coa_print_invoice(self):
        """Direct print of all posted customer invoices of this SO."""
        self.ensure_one()
        invoices = self.sudo().invoice_ids.filtered(
            lambda m: m.move_type in ('out_invoice', 'out_refund')
            and m.state == 'posted'
        )
        if not invoices:
            raise UserError(_(
                "There is no posted invoice on this Sale Order to print yet."
            ))
        return self._coa_direct_print_url('invoice')

    def action_coa_print_statement(self):
        """Direct print of the customer's statement (receivable ledger)."""
        return self._coa_direct_print_url('statement')
