# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import exceptions

from .common import ReleaseChannelCase


class TestReleaseChannel(ReleaseChannelCase):
    def _test_assign_channels(self, expected):
        move = self._create_single_move(self.product1, 10)
        move.picking_id.priority = "1"
        move2 = self._create_single_move(self.product2, 10)
        (move + move2).picking_id.assign_release_channel()
        self.assertEqual(move.picking_id.release_channel_id, expected)
        self.assertEqual(move2.picking_id.release_channel_id, self.default_channel)

    def test_assign_channel_domain(self):
        channel = self._create_channel(
            name="Test Domain",
            sequence=1,
            rule_domain=[("priority", "=", "1")],
        )
        self._test_assign_channels(channel)

    def test_assign_channel_code(self):
        channel = self._create_channel(
            name="Test Code",
            sequence=1,
            code="pickings = pickings.filtered(lambda p: p.priority == '1')",
        )
        self._test_assign_channels(channel)

    def test_assign_channel_domain_and_code(self):
        channel = self._create_channel(
            name="Test Code",
            sequence=1,
            rule_domain=[("priority", "=", "1")],
            code="pickings = pickings.filtered(lambda p: p.priority == '1')",
        )
        self._test_assign_channels(channel)

    def test_invalid_code(self):
        with self.assertRaises(exceptions.ValidationError):
            self._create_channel(
                name="Test Code",
                sequence=1,
                code="pickings = pickings.filtered(",
            )

    def test_default_sequence(self):
        channel = self._create_channel(name="Test1")
        self.assertEqual(channel.sequence, 0)
        channel2 = self._create_channel(name="Test2")
        self.assertEqual(channel2.sequence, 10)
        channel3 = self._create_channel(name="Test3")
        self.assertEqual(channel3.sequence, 20)

    def test_is_manual_assignment(self):
        # Manual Assignment
        self.default_channel.is_manual_assignment = True
        move = self._create_single_move(self.product1, 10)
        move.picking_id.assign_release_channel()
        self.assertEqual(move.picking_id.release_channel_id.id, False)
        # Automatic Assignment
        self.default_channel.is_manual_assignment = False
        move = self._create_single_move(self.product1, 10)
        move.picking_id.assign_release_channel()
        self.assertEqual(move.picking_id.release_channel_id.id, self.default_channel.id)
