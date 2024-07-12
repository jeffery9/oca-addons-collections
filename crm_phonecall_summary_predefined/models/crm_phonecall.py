# Copyright 2016 Antiun Ingeniería S.L. - Jairo Llopis
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CRMPhonecall(models.Model):
    """Added number and summary in the phonecall."""

    _inherit = "crm.phonecall"

    name = fields.Char(
        related="summary_id.name",
        store=True,
        required=False,
        readonly=True,
    )
    summary_id = fields.Many2one(
        comodel_name="crm.phonecall.summary",
        string="Summary",
        required=True,
        ondelete="restrict",
    )

    def get_values_schedule_another_phonecall(self, vals):
        res = super().get_values_schedule_another_phonecall(vals)
        res.update({"summary_id": vals.get("summary_id")})
        return res


class CRMPhonecallSummary(models.Model):
    """Added phonecall summary feature."""

    _name = "crm.phonecall.summary"
    _description = "Crm Phonecall Summary"
    _sql_constraints = [
        ("name_unique", "UNIQUE (name)", "Name must be unique"),
    ]

    name = fields.Char(required=True)
    phonecall_ids = fields.One2many(
        comodel_name="crm.phonecall",
        inverse_name="summary_id",
        string="Phonecalls",
        help="Phonecalls with this summary.",
    )
