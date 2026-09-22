# -*- coding: utf-8 -*-
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_coa_print_statement(self):
        """Direct print of this partner's statement."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/coa_direct_print/print/res.partner/%s/statement' % self.id,
            'target': 'new',
        }
