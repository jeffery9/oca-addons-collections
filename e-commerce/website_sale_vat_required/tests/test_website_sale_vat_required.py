# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import odoo.tests
from odoo.tests.common import HttpCase


@odoo.tests.tagged("post_install", "-at_install")
class TestWebsiteSaleVatRequired(HttpCase):
    def test_website_sale_vat_required(self):
        self.start_tour("/shop", "website_sale_vat_required_tour")
