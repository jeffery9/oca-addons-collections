# Copyright 2017 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    removal_priority = fields.Integer(
        default=10,
        help="This priority applies when removing stock and incoming dates are equal.",
    )
