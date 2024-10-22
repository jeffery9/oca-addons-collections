# Copyright 2017 Vauxoo (https://www.vauxoo.com) info@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestProductNameSearch(TransactionCase):
    """Test for:
    - Assign a configuration customer for product.
    - Test product name_search
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env.ref("base.res_partner_1")
        cls.customer = cls.env.ref("base.res_partner_2")
        cls.product = (
            cls.env["product.product"]
            .create({"name": "Name_product", "default_code": "code_product"})
            .with_context(**{"partner_id": cls.customer.id})
        )
        cls.supplierinfo = cls.env["product.supplierinfo"]
        cls.customerinfo = cls.env["product.customerinfo"]
        cls.customerinfo_dict = {
            "product_code": "code_test",
            "product_name": "Name_test",
            "partner_id": cls.customer.id,
            "product_tmpl_id": cls.product.product_tmpl_id.id,
        }

    def test_10_find_product_customer_code(self):
        """Assign a product_customerinfo to the product and then search it
        using name_search
        """
        self.assertFalse(self.product.customer_ids)

        self.customerinfo.create(self.customerinfo_dict)
        self.assertTrue(self.product.customer_ids)

        # Search by product customer code
        product_names = self.product.name_search(name="code_test")
        self.assertEqual(len(product_names), 1)
        self.assertEqual(self.product.id, product_names[0][0])
        self.assertEqual("[code_test] Name_test", product_names[0][1])

        # Search by product default code with the customer used in
        # configuration customer
        product_names = self.product.name_search(name="code_product")
        self.assertEqual(len(product_names), 1)
        self.assertEqual(self.product.id, product_names[0][0])
        self.assertEqual("[code_test] Name_test", product_names[0][1])

        # Search by product default code with a different customer used in
        # configuration customer
        product_names = self.product.with_context(
            partner_id=self.supplier.id
        ).name_search(name="code_product")
        self.assertEqual(len(product_names), 1)
        self.assertEqual(self.product.id, product_names[0][0])
        self.assertEqual("[code_product] Name_product", product_names[0][1])

        # Create a product_1 with default_code similar to customer_code of
        # product, then name_search must find two products
        self.product_1 = (
            self.env["product.product"]
            .create({"name": "Name_test_1", "default_code": "code_test_1"})
            .with_context(**{"partner_id": self.customer.id})
        )

        self.assertFalse(self.product_1.customer_ids)

        # Search by product customer code
        product_names = self.product.name_search(name="code_test")
        self.assertEqual(len(product_names), 2)
        product_names = product_names[0] + product_names[1]
        self.assertIn(self.product.id, product_names)
        self.assertIn(self.product_1.id, product_names)
        self.assertIn("[code_test] Name_test", product_names)
        self.assertIn("[code_test_1] Name_test_1", product_names)
