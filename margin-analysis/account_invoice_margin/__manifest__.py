# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Margin",
    "summary": "Show margin in invoices",
    "version": "16.0.1.0.1",
    "category": "Account",
    "website": "https://github.com/OCA/margin-analysis",
    "author": "Tecnativa, " "GRAP, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["sergio-teruel"],
    "application": False,
    "installable": True,
    "depends": ["account"],
    "data": [
        "security/account_invoice_margin_security.xml",
        "views/account_invoice_margin_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
