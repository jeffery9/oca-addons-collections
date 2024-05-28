# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Fiscal Position Autodetect optional VIES",
    "version": "17.0.1.0.0",
    "category": "Accounting & Finance",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["victoralmau"],
    "website": "https://github.com/OCA/account-fiscal-rule",
    "depends": [
        "account",
        "base_vat",
    ],
    "data": ["views/account_fiscal_position_view.xml"],
    "external_dependencies": {},
    "application": True,
}
