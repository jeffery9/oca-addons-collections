# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Hr Expense Analytic Tag",
    "version": "16.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["hr_expense", "account_analytic_tag"],
    "installable": True,
    "auto_install": True,
    "data": [
        "views/hr_expense_view.xml",
    ],
    "maintainers": ["victoralmau"],
}
