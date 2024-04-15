# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    country_restriction_id = fields.Many2one(
        comodel_name="product.country.restriction",
        string="Country Restriction",
        default=lambda self: self._get_country_restriction_id(),
    )

    @api.model
    def _get_country_restriction_id(self):
        return self.env.company.country_restriction_id
