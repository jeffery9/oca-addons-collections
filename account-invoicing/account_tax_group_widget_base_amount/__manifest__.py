# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Tax Group Widget Base Amount",
    "summary": "Adds base amount to tax group widget",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoicing",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu"],
    "license": "AGPL-3",
    "depends": ["account"],
    "assets": {
        "web.assets_backend": [
            "account_tax_group_widget_base_amount/static/src/xml/tax_group.xml",
        ],
    },
}
