# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request

# Report references (change here if you want other layouts)
REPORT_SO        = 'sale.report_saleorder'
REPORT_INVOICE   = 'account.account_invoices'
REPORT_STATEMENT = 'coa_direct_print.action_report_partner_statement'
REPORT_PAYMENT   = 'coa_direct_print.action_report_payment_receipt'

ALLOWED_KEYS   = ('so', 'invoice', 'statement', 'receipt')
ALLOWED_MODELS = ('sale.order', 'account.move', 'res.partner', 'account.payment')

# print.js technique: fetch the PDF as a blob, load it in a hidden iframe,
# then trigger the print dialog. Much more reliable on Chrome/Edge than
# calling print() on a visible iframe pointing to a network URL.
PRINT_PAGE = Markup("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>%(title)s</title>
<style>
    html, body { margin:0; padding:0; height:100%%; font-family: Arial, sans-serif; }
    #coa-toolbar {
        height:44px; background:#1f2937; color:#fff;
        display:flex; align-items:center; gap:12px; padding:0 14px;
        direction:rtl;
    }
    #coa-print-btn {
        background:#10b981; color:#fff; border:none; border-radius:6px;
        padding:8px 22px; font-size:15px; font-weight:bold; cursor:pointer;
    }
    #coa-print-btn:hover { background:#059669; }
    #coa-status { font-size:13px; opacity:.85; }
    #coa-preview { width:100%%; height:calc(100%% - 44px); border:none; display:block; }
</style>
</head>
<body>
<div id="coa-toolbar">
    <button id="coa-print-btn" type="button">&#128424; &#1591;&#1576;&#1575;&#1593;&#1577; / Print</button>
    <span id="coa-status">&#1580;&#1575;&#1585;&#1610; &#1578;&#1580;&#1607;&#1610;&#1586; &#1575;&#1604;&#1591;&#1576;&#1575;&#1593;&#1577;...</span>
</div>
<iframe id="coa-preview" title="preview"></iframe>
<script>
(function () {
    "use strict";
    var pdfUrl = "%(pdf_url)s";
    var status = document.getElementById('coa-status');
    var previewFrame = document.getElementById('coa-preview');
    var hiddenFrame = null;
    var blobUrl = null;

    function setStatus(msg) { status.textContent = msg; }

    function doPrint() {
        if (!hiddenFrame || !hiddenFrame.contentWindow) {
            window.print();
            return;
        }
        try {
            hiddenFrame.contentWindow.focus();
            hiddenFrame.contentWindow.print();
        } catch (e) {
            try { window.print(); } catch (e2) { /* ignore */ }
        }
    }

    document.getElementById('coa-print-btn').addEventListener('click', doPrint);

    fetch(pdfUrl, { credentials: 'same-origin' })
        .then(function (resp) {
            if (!resp.ok) { throw new Error('HTTP ' + resp.status); }
            return resp.blob();
        })
        .then(function (blob) {
            var pdfBlob = new Blob([blob], { type: 'application/pdf' });
            blobUrl = URL.createObjectURL(pdfBlob);

            // Visible preview for the user
            previewFrame.src = blobUrl;

            // Hidden frame used for the actual printing (print.js style)
            hiddenFrame = document.createElement('iframe');
            hiddenFrame.style.position = 'fixed';
            hiddenFrame.style.right = '0';
            hiddenFrame.style.bottom = '0';
            hiddenFrame.style.width = '1px';
            hiddenFrame.style.height = '1px';
            hiddenFrame.style.border = '0';
            hiddenFrame.setAttribute('aria-hidden', 'true');
            hiddenFrame.onload = function () {
                setStatus('&#1580;&#1575;&#1607;&#1586; \u2713');
                status.innerHTML = '&#1580;&#1575;&#1607;&#1586; \u2713';
                setTimeout(doPrint, 500);
            };
            hiddenFrame.src = blobUrl;
            document.body.appendChild(hiddenFrame);
        })
        .catch(function (err) {
            setStatus('Preview error: ' + err.message);
            // Last resort: open the PDF directly
            previewFrame.src = pdfUrl;
        });
})();
</script>
</body>
</html>""")


class CoaDirectPrint(http.Controller):

    # ------------------------------------------------------------------
    # Resolution & security
    # ------------------------------------------------------------------
    def _resolve(self, model, res_id, report_key):
        """Validate access on the SOURCE record, then return
        (report_ref, res_ids, filename) rendered with sudo scope
        limited to that record's data."""
        if model not in ALLOWED_MODELS or report_key not in ALLOWED_KEYS:
            return None
        record = request.env[model].browse(res_id)
        if not record.exists():
            return None
        try:
            record.check_access('read')
        except AccessError:
            return None

        record = record.sudo()

        if model == 'sale.order':
            if report_key == 'so':
                return REPORT_SO, record.ids, '%s.pdf' % record.name
            if report_key == 'invoice':
                invoices = record.invoice_ids.filtered(
                    lambda m: m.move_type in ('out_invoice', 'out_refund')
                    and m.state == 'posted')
                if not invoices:
                    return None
                return (REPORT_INVOICE, invoices.ids,
                        '%s_invoices.pdf' % record.name)
            if report_key == 'statement':
                partner = record.partner_id.commercial_partner_id
                return (REPORT_STATEMENT, partner.ids,
                        'statement_%s.pdf' % (partner.ref or partner.id))

        elif model == 'account.move':
            if report_key == 'invoice':
                if record.state != 'posted':
                    return None
                return REPORT_INVOICE, record.ids, '%s.pdf' % (
                    (record.name or 'invoice').replace('/', '_'))
            if report_key == 'statement':
                partner = record.partner_id.commercial_partner_id
                if not partner:
                    return None
                return (REPORT_STATEMENT, partner.ids,
                        'statement_%s.pdf' % (partner.ref or partner.id))

        elif model == 'res.partner':
            if report_key == 'statement':
                partner = record.commercial_partner_id
                return (REPORT_STATEMENT, partner.ids,
                        'statement_%s.pdf' % (partner.ref or partner.id))

        elif model == 'account.payment':
            if report_key == 'receipt':
                if record.state not in ('in_process', 'paid'):
                    return None
                filename = 'receipt_%s.pdf' % (
                    (record.name or str(record.id)).replace('/', '_'))
                return REPORT_PAYMENT, record.ids, filename

        return None

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------
    @http.route('/coa_direct_print/print/<string:model>/<int:res_id>/<string:report_key>',
                type='http', auth='user')
    def print_page(self, model, res_id, report_key, **kwargs):
        resolved = self._resolve(model, res_id, report_key)
        if not resolved:
            return request.not_found()
        html = PRINT_PAGE % {
            'title': _("Direct Print"),
            'pdf_url': '/coa_direct_print/pdf/%s/%s/%s' % (model, res_id, report_key),
        }
        return request.make_response(
            html, headers=[('Content-Type', 'text/html; charset=utf-8')])

    @http.route('/coa_direct_print/pdf/<string:model>/<int:res_id>/<string:report_key>',
                type='http', auth='user')
    def print_pdf(self, model, res_id, report_key, **kwargs):
        resolved = self._resolve(model, res_id, report_key)
        if not resolved:
            return request.not_found()
        report_ref, res_ids, filename = resolved
        pdf_content, _dummy = request.env['ir.actions.report'].sudo(
        )._render_qweb_pdf(report_ref, res_ids=res_ids)
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', 'inline; filename="%s"' % filename),
        ]
        return request.make_response(pdf_content, headers=headers)
