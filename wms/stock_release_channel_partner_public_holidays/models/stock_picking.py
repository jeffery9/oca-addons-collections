# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _find_release_channel_possible_candidate(self):
        """Filter channels: make sure shipment date is not a public holiday of Partner
        :return: release channels
        """
        channels = super()._find_release_channel_possible_candidate()
        channels = channels.filter_release_channel(self.partner_id)
        return channels
