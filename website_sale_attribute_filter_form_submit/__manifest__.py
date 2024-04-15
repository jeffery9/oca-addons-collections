# Copyright 2021 Studio73 - Miguel Gandia
# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website manual attribute filters",
    "version": "16.0.1.0.0",
    "category": "E-Commerce",
    "summary": "Allow to apply manually the filters on the e-commerce",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "templates/website_sale.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_attribute_filter_form_submit/static/src/js/website_sale.js"
        ],
    },
    "author": "Studio73, Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/e-commerce",
    "installable": True,
}
