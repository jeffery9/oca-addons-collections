# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader

from odoo.tests.common import TransactionCase

from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock.models.stock_move import StockMove


class TestExcludeLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .common import ResPartner

        cls.loader.update_registry((ResPartner,))

        cls.fake = cls.env["res.partner"].create({"name": "name"})
        cls.location_shop = cls.env.ref("stock.stock_location_stock")
        vals = {"location_id": cls.location_shop.id, "name": "Sub Location 1"}
        cls.sub_location_1 = cls.env["stock.location"].create(vals)
        cls.sub_location_1._parent_store_compute()
        cls.product = cls.env.ref("product.product_product_4")

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @classmethod
    def _create_stock_move(
        cls, quantity: float, location: Location, location_dest: Location
    ) -> StockMove:
        move = cls.env["stock.move"].create(
            {
                "name": "Move",
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "product_id": cls.product.id,
                "product_uom_qty": quantity,
                "product_uom": cls.product.uom_id.id,
            }
        )
        move._action_confirm()
        return move

    def _add_stock_to_product(self, product, location, qty):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        """
        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "inventory_quantity": qty,
            }
        )._apply_inventory()

    def test_exclude_location(self):
        # Add different levels of stock for product as :
        # Shop 0: 50.0
        # Sub Level (Shop 0 / Sub Location 1): 25.0
        # Query product stock availability normally and with excluded
        # location as Sub Location 1
        self._add_stock_to_product(self.product, self.location_shop, 50.0)
        self._add_stock_to_product(self.product, self.sub_location_1, 25.0)
        self.fake.stock_excluded_location_ids = self.sub_location_1
        qty = self.product.with_context(
            excluded_location_ids=self.fake.stock_excluded_location_ids
        ).qty_available
        self.assertEqual(50.0, qty)
        self.product.invalidate_recordset()
        qty = self.product.qty_available
        self.assertEqual(75.0, qty)

    def test_exclude_location_domain(self):
        # Add different levels of stock for product as :
        # Shop 0: 50.0
        # Sub Level (Shop 0 / Sub Location 1): 25.0
        # Query product stock availability normally and with excluded
        # location as Sub Location 1
        self._add_stock_to_product(self.product, self.location_shop, 50.0)
        self._add_stock_to_product(self.product, self.sub_location_1, 25.0)
        self.fake.stock_excluded_location_domain_char = (
            "[('location_id', 'not in', " + str(self.sub_location_1.ids) + ")]"
        )
        qty = self.product.with_context(
            excluded_location_domain=self.fake.stock_excluded_location_domain
        ).qty_available
        self.assertEqual(50.0, qty)
        self.product.invalidate_recordset()
        qty = self.product.qty_available
        self.assertEqual(75.0, qty)

    def test_exclude_location_domain_in(self):
        # Add different levels of stock for product as :
        # Shop 0: 50.0
        # Sub Level (Shop 0 / Sub Location 1): 25.0
        # Query product stock availability normally and with excluded
        # location as Supplier
        self._add_stock_to_product(self.product, self.location_shop, 50.0)
        self._add_stock_to_product(self.product, self.sub_location_1, 25.0)
        self._create_stock_move(
            30.0, self.env.ref("stock.stock_location_suppliers"), self.sub_location_1
        )
        self.product.invalidate_recordset()
        qty = self.product.with_context(
            excluded_location_domain=self.fake.stock_excluded_location_domain
        ).virtual_available
        self.assertEqual(105.0, qty)
        self.fake.stock_excluded_location_domain_char = (
            "[('location_id.usage', '!=', 'supplier')]"
        )
        self.product.invalidate_recordset()
        qty = self.product.with_context(
            excluded_location_domain=self.fake.stock_excluded_location_domain
        ).virtual_available
        self.assertEqual(75.0, qty)
