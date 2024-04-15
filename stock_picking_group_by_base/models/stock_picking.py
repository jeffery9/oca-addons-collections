# Copyright 2016-2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019-2020 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.model
    def _get_index_for_grouping_fields(self):
        """
        This tuple is intended to be overriden in order to add fields
        used in groupings
        """
        return [
            "partner_id",
            "location_id",
            "location_dest_id",
            "picking_type_id",
        ]

    @api.model
    def _get_index_for_grouping_condition(self):
        return """
            WHERE printed is False
            AND state in ('draft', 'confirmed', 'waiting', 'partially_available', 'assigned')
        """

    @api.model
    def _create_index_for_grouping(self):
        # create index for the domain expressed into the
        # stock_move._assign_picking_group_domain method
        index_name = "stock_picking_groupby_key_index"
        self.env.cr.execute(
            "DROP INDEX IF EXISTS %(index_name)s", dict(index_name=AsIs(index_name))
        )

        self.env.cr.execute(
            """
                CREATE INDEX %(index_name)s
                ON %(table_name)s %(fields)s
                %(where)s
            """,
            dict(
                index_name=AsIs(index_name),
                table_name=AsIs(self._table),
                fields=tuple(
                    [AsIs(field) for field in self._get_index_for_grouping_fields()]
                ),
                where=AsIs(self._get_index_for_grouping_condition()),
            ),
        )

    def init(self):
        """
        This has to be called in every overriding module
        """
        self._create_index_for_grouping()
