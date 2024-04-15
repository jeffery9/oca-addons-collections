# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import timedelta

from freezegun import freeze_time

from odoo import fields

from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


class ReleaseChannelEndDateCase(ChannelReleaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.customer_anytime = cls.env["res.partner"].create(
            {"name": "Anytime", "delivery_time_preference": "anytime"}
        )
        cls.customer_working_days = cls.env["res.partner"].create(
            {"name": "Working Days", "delivery_time_preference": "workdays"}
        )
        cls.customer_time_window = cls.env["res.partner"].create(
            {
                "name": "Time Window",
                "delivery_time_preference": "time_windows",
                "delivery_time_window_ids": [
                    (
                        0,
                        0,
                        {
                            "time_window_start": 0.00,
                            "time_window_end": 23.99,
                            "time_window_weekday_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        cls.env.ref(
                                            "base_time_window.time_weekday_thursday"
                                        ).id,
                                        cls.env.ref(
                                            "base_time_window.time_weekday_saturday"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ],
            }
        )
        cls.product = cls.env.ref("product.product_product_9")
        cls.picking_type_delivery = cls.env.ref("stock.picking_type_out")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_customers = cls.env.ref("stock.stock_location_customers")
        cls.channel.respect_partner_delivery_time_windows = True

    def _assign_picking(self, picking):
        picking.release_channel_id = False
        picking.assign_release_channel()

    @freeze_time("2023-09-01")
    def test_assign_channel_anytime(self):
        today = fields.Date.today()
        self.channel.process_end_time = 0
        self.channel.process_end_date = today + timedelta(days=1)  # 2023-09-02
        # Anytime
        self.picking.partner_id = self.customer_anytime
        self._assign_picking(self.picking)
        self.assertEqual(self.channel, self.picking.release_channel_id)

    @freeze_time("2023-09-01")
    def test_assign_channel_workdays(self):
        # Workdays
        today = fields.Date.today()
        self.channel.process_end_time = 0
        self.channel.process_end_date = today + timedelta(days=1)  # 2023-09-02
        self.picking.partner_id = self.customer_working_days
        self._assign_picking(self.picking)
        self.assertNotEqual(self.channel, self.picking.release_channel_id)
        self.channel.process_end_date = today + timedelta(days=4)  # 2023-09-05
        self._assign_picking(self.picking)
        self.assertEqual(self.channel, self.picking.release_channel_id)

    @freeze_time("2023-09-01")
    def test_assign_channel_window(self):
        # Window
        today = fields.Date.today()
        self.picking.partner_id = self.customer_time_window
        self.channel.process_end_date = today  # Friday
        self._assign_picking(self.picking)
        self.assertNotEqual(self.channel, self.picking.release_channel_id)
        self.channel.process_end_date = today + timedelta(
            days=6
        )  # 2023-09-05: Thursday
        self._assign_picking(self.picking)
        self.assertEqual(self.channel, self.picking.release_channel_id)

    @freeze_time("2023-09-01")
    def test_assign_channel_no_respect_delivery_time_window(self):
        self.channel.respect_partner_delivery_time_windows = False
        fields.Date.today()
        self.picking.partner_id = self.customer_time_window
        self._assign_picking(self.picking)
        self.assertEqual(self.channel, self.picking.release_channel_id)
