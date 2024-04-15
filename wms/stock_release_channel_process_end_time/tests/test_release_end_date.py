# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import fields

from odoo.addons.stock_release_channel.tests.common import ChannelReleaseCase


class ReleaseChannelEndDateCase(ChannelReleaseCase):
    @freeze_time("2023-01-27")
    def test_channel_end_date(self):
        # Set the end time
        self.channel.process_end_time = 23.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        self.channel.action_wake_up()
        self.assertEqual(
            "2023-01-27 23:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )

    @freeze_time("2023-01-27 10:00:00")
    def test_channel_end_date_tomorrow(self):
        # Set the end time
        self.channel.process_end_time = 1.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        # Current time is 10:00:00
        self.channel.action_wake_up()
        self.assertEqual(
            "2023-01-28 01:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )

    @freeze_time("2023-01-27 10:00:00")
    def test_channel_end_date_manual(self):
        # Set the end time
        self.channel.process_end_time = 1.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        # Current time is 10:00:00
        self.channel.action_wake_up()
        self.assertEqual(
            "2023-01-28 01:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )

        # We force the end date
        self.channel.process_end_date = "2023-01-27 23:30:00"
        self.assertEqual(
            "2023-01-27 23:30:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )

    @freeze_time("2023-01-27 10:00:00")
    def test_channel_counter_release_ready(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "stock_release_channel_process_end_time.stock_release_use_channel_end_date",
            True,
        )
        # Remove existing jobs as some already exists to assign pickings to channel
        jobs_before = self.env["queue.job"].search([])
        jobs_before.unlink()
        # Set the end time
        self.channel.process_end_time = 23.0
        # Set picking scheduled date
        pickings = self.picking | self.picking2 | self.picking3
        pickings.write({"scheduled_date": fields.Datetime.now()})

        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Execute the picking channel assignations
        self.channel.with_context(queue_job__no_delay=True).action_wake_up()

        self.assertEqual(pickings, self.channel.picking_ids)
        # at this stage, the pickings are not ready to be released as the
        # qty available is not enough
        self.assertFalse(self.channel._get_pickings_to_release())

        self._update_qty_in_location(self.loc_bin1, self.product1, 100.0)
        self._update_qty_in_location(self.loc_bin1, self.product2, 100.0)

        self.assertEqual(pickings, self.channel._get_pickings_to_release())
        # if the scheduled date of one picking is changed to be on a time after the
        # process end date but on the same day, it should still be releasable
        pickings[0].scheduled_date = fields.Datetime.from_string("2023-01-27 23:30:00")
        self.assertEqual(pickings, self.channel._get_pickings_to_release())
        # if the scheduled date of one picking is changed to be on a date after the
        # process end date, it should not be releasable anymore
        pickings[0].scheduled_date = fields.Datetime.from_string("2023-01-28 00:00:00")
        self.assertEqual(pickings[1:], self.channel._get_pickings_to_release())

    @freeze_time("2023-01-27 10:00:00")
    def test_picking_scheduled_date(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "stock_release_channel_process_end_time.stock_release_use_channel_end_date",
            True,
        )
        # Remove existing jobs as some already exists to assign pickings to channel
        jobs_before = self.env["queue.job"].search([])
        jobs_before.unlink()
        # Set the end time
        self.channel.process_end_time = 23.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Execute the picking channel assignations
        self.channel.with_context(queue_job__no_delay=True).action_wake_up()
        for picking in self.channel.picking_ids:
            self.assertNotEqual(
                "2023-01-27 23:00:00", fields.Datetime.to_string(picking.scheduled_date)
            )
        for move in self.channel.picking_ids.move_ids:
            self.assertNotEqual(
                "2023-01-27 23:00:00", fields.Datetime.to_string(move.date)
            )
        self._update_qty_in_location(self.loc_bin1, self.product1, 100.0)
        self._update_qty_in_location(self.loc_bin1, self.product2, 100.0)
        self.channel.picking_ids.release_available_to_promise()
        moves = self.channel.picking_ids.move_ids
        moves |= moves.move_orig_ids
        # Check the scheduled date is corresponding to the one on channel
        for picking in moves.picking_id:
            self.assertEqual(
                "2023-01-27 23:00:00", fields.Datetime.to_string(picking.scheduled_date)
            )
        for move in moves:
            self.assertEqual(
                "2023-01-27 23:00:00", fields.Datetime.to_string(move.date)
            )

        # Assign picking to a new channel
        channel = self.env["stock.release.channel"].create(
            {
                "name": "Test Date",
                "process_end_time": 15,
                "state": "open",
            }
        )
        channel.action_sleep()
        channel.invalidate_recordset()
        channel.action_wake_up()
        self.picking.release_channel_id = channel.id
        moves = self.picking.move_ids
        moves |= moves.move_orig_ids
        for picking in moves.picking_id:
            self.assertEqual(
                "2023-01-27 15:00:00", fields.Datetime.to_string(picking.scheduled_date)
            )
        for move in moves:
            self.assertEqual(
                "2023-01-27 15:00:00", fields.Datetime.to_string(move.date)
            )

    @freeze_time("2023-01-27 10:00:00")
    def test_channel_end_date_as_move_date_deadline_on_moves_created_by_release(self):
        """
        Check that the process end date is set as the move date deadline on
        moves created by the release of a shipping (and also on the generated pick
        itself).
        """
        self.env["ir.config_parameter"].sudo().set_param(
            "stock_release_channel_process_end_time.stock_release_use_channel_end_date",
            True,
        )
        # Remove existing jobs as some already exists to assign pickings to channel
        jobs_before = self.env["queue.job"].search([])
        jobs_before.unlink()
        # Set the end time
        self.channel.process_end_time = 23.0
        channel = self.channel.with_context(queue_job__no_delay=True)
        # Asleep the release channel to void the process end date
        channel.action_sleep()
        new_pickings = channel.picking_ids.move_ids.move_orig_ids.picking_id
        self.assertFalse(new_pickings)
        channel.invalidate_recordset()
        channel.action_wake_up()
        self._update_qty_in_location(self.loc_bin1, self.product1, 100.0)
        self._update_qty_in_location(self.loc_bin1, self.product2, 100.0)
        pickings = channel.picking_ids
        pickings.env.invalidate_all()
        # release the pickings
        pickings.release_available_to_promise()
        # get the moves created by the release
        new_pickings = pickings.move_ids.move_orig_ids.picking_id
        self.assertTrue(new_pickings)
        # check that the picking schedule date is set to the process end date
        for picking in new_pickings:
            self.assertEqual(
                "2023-01-27 23:00:00",
                fields.Datetime.to_string(picking.move_ids[0].date_deadline),
            )

    def test_can_edit_time(self):
        user = self.env.ref("base.user_demo")
        group = self.env.ref("stock.group_stock_manager")
        user.groups_id -= group
        self.assertFalse(self.channel.with_user(user).process_end_time_can_edit)

        user.groups_id |= self.env.ref("stock.group_stock_manager")
        self.assertTrue(self.channel.with_user(user).process_end_time_can_edit)

    @freeze_time("2023-01-27")
    def test_channel_end_date_warehouse_timezone_asia(self):
        # Today is 2023-01-27 06:00 in Asia
        # Set a warehouse with an adress and a timezone on channel
        self.channel.warehouse_id = self.env.ref("stock.warehouse0")
        self.channel.warehouse_id.partner_id.tz = "Etc/GMT-6"
        # Set the end time - In UTC == 15:00
        self.channel.process_end_time = 21.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        self.channel.action_wake_up()
        # Local time is 2023-01-27 21:00
        self.assertEqual(
            "2023-01-27 15:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )
        # Set the end time - In UTC == 21:00
        self.channel.process_end_time = 3.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        self.channel.action_wake_up()
        # Local time is 2023-01-28 03:00
        self.assertEqual(
            "2023-01-27 21:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )

    @freeze_time("2023-01-27")
    def test_channel_end_date_warehouse_timezone_america(self):
        # Now is 2023-01-26 18:00 in America
        # Set a warehouse with an adress and a timezone on channel
        self.channel.warehouse_id = self.env.ref("stock.warehouse0")
        self.channel.warehouse_id.partner_id.tz = "Etc/GMT+6"
        # Set the end time - In UTC == 3:00 +1d
        self.channel.process_end_time = 21.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        self.channel.action_wake_up()
        # Local time is 2023-01-26 21:00
        self.assertEqual(
            "2023-01-27 03:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )
        # Set the end time - In UTC == 9:00
        self.channel.process_end_time = 3.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        self.channel.action_wake_up()
        # Local time is 2023-01-27 03:00
        self.assertEqual(
            "2023-01-27 09:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )

    @freeze_time("2023-01-27 11:00:00")
    def test_channel_end_date_warehouse_timezone_tomorrow(self):
        # Set a warehouse with an adress and a timezone on channel
        self.channel.warehouse_id = self.env.ref("stock.warehouse0")
        self.channel.warehouse_id.partner_id.tz = "Europe/Brussels"
        # Set the end time - In UTC == 22:00
        self.channel.process_end_time = 10.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        self.channel.action_wake_up()
        self.assertEqual(
            "2023-01-28 09:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )

    @freeze_time("2023-01-27")
    def test_channel_end_date_company_timezone(self):
        # Set a warehouse with an adress and a timezone on channel
        self.assertFalse(self.channel.warehouse_id)
        self.env.company.partner_id.tz = "Europe/Brussels"
        # Set the end time - In UTC == 22:00
        self.channel.process_end_time = 23.0
        # Asleep the release channel to void the process end date
        self.channel.action_sleep()
        self.channel.invalidate_recordset()
        # Wake up the channel to set the process end date
        self.channel.action_wake_up()
        self.assertEqual(
            "2023-01-27 22:00:00",
            fields.Datetime.to_string(self.channel.process_end_date),
        )
