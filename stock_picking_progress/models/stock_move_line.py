# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    progress = fields.Float(
        compute="_compute_progress", store=True, group_operator="avg"
    )

    @api.depends(
        "qty_done",
        "product_uom_id",
        "reserved_qty",
        "state",
    )
    def _compute_progress(self):
        for record in self:
            if record.state == "done":
                record.progress = 100
                continue
            rounding = record.product_uom_id.rounding
            if float_is_zero(record.reserved_qty, precision_rounding=rounding):
                record.progress = 100
            else:
                record.progress = (record.qty_done / record.reserved_qty) * 100
