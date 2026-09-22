# -*- coding: utf-8 -*-
{
    'name': 'COA Direct Print - SO, Invoices & Customer Statement',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'One-click direct printing for Sale Orders, Customer Invoices, and Customer Account Statements - no download step',
    'description': """
COA Direct Print
================
One-click print dialog - no download, no extra steps.
Adds direct print buttons to Sale Orders, Customer Invoices, and Partner forms.
Sales users can print invoices and statements without needing Accounting access.
Includes a custom QWeb Customer Statement (account statement with running balance).
Works on both Community and Enterprise editions.
PDF is streamed into a hidden iframe and the browser print dialog opens automatically.
    """,
    'author': 'Community of accountants (COA-Egypt)',
    'website': 'https://www.coa-egy.com',
    'support': 'info@coa-egy.com',
    'images': ['static/description/banner.png'],
    'depends': ['sale', 'account'],
    'data': [
        'report/partner_statement_report.xml',
        'report/partner_statement_templates.xml',
        'report/payment_receipt_report.xml',
        'report/payment_receipt_templates.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/res_partner_views.xml',
    ],
    'price': 49.00,
    'currency': 'USD',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
