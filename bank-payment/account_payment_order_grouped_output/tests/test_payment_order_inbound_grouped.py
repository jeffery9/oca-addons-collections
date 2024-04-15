# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import tagged

from odoo.addons.account_payment_order.tests.test_payment_order_inbound import (
    TestPaymentOrderInboundBase,
)


@tagged("post_install", "-at_install")
class TestPaymentOrderInbound(TestPaymentOrderInboundBase):
    def test_grouped_output(self):
        self.inbound_mode.generate_move = True
        self.inbound_mode.post_move = True
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        grouped_moves = self.inbound_order.grouped_move_ids
        self.assertFalse(grouped_moves)
        # Add now a second line with different partner
        self.inbound_order.action_uploaded_cancel()
        self.inbound_order.cancel2draft()
        old_partner = self.partner
        self.partner = self.env["res.partner"].create({"name": "Test Partner 2"})
        invoice2 = self._create_customer_invoice()
        self.partner = old_partner
        invoice2.action_post()
        self.env["account.invoice.payment.line.multi"].with_context(
            active_model="account.move", active_ids=invoice2.ids
        ).create({}).run()
        self.inbound_order.draft2open()
        self.inbound_order.open2generated()
        self.inbound_order.generated2uploaded()
        grouped_moves = self.inbound_order.grouped_move_ids
        self.assertTrue(grouped_moves)
        self.assertTrue(grouped_moves.line_ids[0].reconciled)
