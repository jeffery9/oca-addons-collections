# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "Purchase Advance Payment",
    "version": "17.0.1.1.0",
    "author": "Forgeflow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/purchase-workflow",
    "category": "Purchase",
    "maintainers": ["LoisRForgeFlow"],
    "license": "AGPL-3",
    "summary": "Allow to add advance payments on purchase orders",
    "depends": ["purchase"],
    "data": [
        "wizard/purchase_advance_payment_wizard_view.xml",
        "views/purchase_view.xml",
        "security/ir.model.access.csv",
        "views/account_payment_views.xml",
    ],
    "installable": True,
}
