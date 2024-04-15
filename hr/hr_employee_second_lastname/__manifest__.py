# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Employee First Name and Two Last Names",
    "version": "17.0.1.0.0",
    "author": "Vauxoo, Odoo Community Association (OCA)",
    "maintainers": ["luisg123v"],
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "summary": "Split Name in First Name, Father's Last Name and Mother's Last Name",
    "depends": ["hr_employee_firstname"],
    "data": ["views/hr_views.xml"],
    "post_init_hook": "post_init_hook",
    "demo": [],
    "test": [],
    "installable": True,
}
