# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Partner Invoicing Mode",
    "version": "16.0.1.0.1",
    "summary": "Base module for handling multiple partner invoicing mode",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-invoicing",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account", "queue_job", "sale"],
    "data": [
        "data/queue_job_data.xml",
        "views/res_partner.xml",
    ],
}
