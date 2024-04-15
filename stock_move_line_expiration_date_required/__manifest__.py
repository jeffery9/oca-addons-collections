# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
{
    "name": "Stock Move Line Expiration Date Required",
    "Summary": "Expiration date is required to enter manually on Move Lines.",
    "version": "16.0.1.0.2",
    "author": "Moduon, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["product_expiry"],
    "data": [
        "views/stock_move_view.xml",
        "views/stock_move_line_view.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
