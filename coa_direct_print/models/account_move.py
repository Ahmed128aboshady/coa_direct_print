# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _coa_direct_print_url(self, report_key):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/coa_direct_print/print/account.move/%s/%s' % (self.id, report_key),
            'target': 'new',
        }

    def action_coa_print_invoice(self):
        """Direct print of this invoice."""
        self.ensure_one()
        if self.state != 'posted':
            raise UserError(_("Only posted invoices can be printed."))
        return self._coa_direct_print_url('invoice')

    def action_coa_print_statement(self):
        """Direct print of the customer's statement."""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("This document has no customer set."))
        return self._coa_direct_print_url('statement')
