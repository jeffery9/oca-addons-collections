# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from collections import Counter

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import Form
from odoo.tools import html2plaintext

from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

_logger = logging.getLogger(__name__)


class Rma(models.Model):
    _name = "rma"
    _description = "RMA"
    _order = "date desc, priority"
    _inherit = ["mail.thread", "portal.mixin", "mail.activity.mixin"]

    def _domain_location_id(self):
        # this is done with sudo, intercompany rules are not applied by default so we
        # add company in domain explicitly to avoid multi-company rule error when
        # the user will try to choose a location
        rma_loc = (
            self.env["stock.warehouse"]
            .search([("company_id", "in", self.env.companies.ids)])
            .mapped("rma_loc_id")
        )
        return [("id", "child_of", rma_loc.ids)]

    # General fields
    sent = fields.Boolean()
    name = fields.Char(
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    origin = fields.Char(
        string="Source Document",
        help="Reference of the document that generated this RMA.",
    )
    date = fields.Datetime(
        default=fields.Datetime.now,
        index=True,
        required=True,
    )
    deadline = fields.Date()
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        index=True,
        tracking=True,
    )
    team_id = fields.Many2one(
        comodel_name="rma.team",
        string="RMA team",
        index=True,
        compute="_compute_team_id",
        store=True,
    )
    tag_ids = fields.Many2many(comodel_name="rma.tag", string="Tags")
    finalization_id = fields.Many2one(
        string="Finalization Reason",
        comodel_name="rma.finalization",
        copy=False,
        domain=(
            "['|', ('company_id', '=', False), ('company_id', '='," " company_id)]"
        ),
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        string="Customer",
        comodel_name="res.partner",
        index=True,
        tracking=True,
    )
    partner_shipping_id = fields.Many2one(
        string="Shipping Address",
        comodel_name="res.partner",
        help="Shipping address for current RMA.",
        compute="_compute_partner_shipping_id",
        store=True,
        readonly=False,
    )
    partner_invoice_id = fields.Many2one(
        string="Invoice Address",
        comodel_name="res.partner",
        domain=(
            "['|', ('company_id', '=', False), ('company_id', '='," " company_id)]"
        ),
        help="Refund address for current RMA.",
        compute="_compute_partner_invoice_id",
        store=True,
        readonly=False,
    )
    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="partner_id.commercial_partner_id",
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Origin Delivery",
        domain=(
            "["
            "    ('state', '=', 'done'),"
            "    ('picking_type_id.code', '=', 'outgoing'),"
            "    ('partner_id', 'child_of', commercial_partner_id),"
            "]"
        ),
    )
    move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Origin move",
        domain=(
            "["
            "    ('picking_id', '=', picking_id),"
            "    ('picking_id', '!=', False)"
            "]"
        ),
        compute="_compute_move_id",
        store=True,
        readonly=False,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("type", "in", ["consu", "product"])],
        compute="_compute_product_id",
        store=True,
        readonly=False,
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
        digits="Product Unit of Measure",
        compute="_compute_product_uom_qty",
        store=True,
        readonly=False,
    )
    product_uom = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        required=True,
        default=lambda self: self.env.ref("uom.product_uom_unit").id,
        compute="_compute_product_uom",
        store=True,
        readonly=False,
    )
    procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement group",
    )
    priority = fields.Selection(
        selection=PROCUREMENT_PRIORITIES,
        default="1",
    )
    operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Requested operation",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("received", "Received"),
            ("waiting_return", "Waiting for return"),
            ("waiting_replacement", "Waiting for replacement"),
            ("refunded", "Refunded"),
            ("returned", "Returned"),
            ("replaced", "Replaced"),
            ("finished", "Finished"),
            ("locked", "Locked"),
            ("cancelled", "Canceled"),
        ],
        default="draft",
        copy=False,
        tracking=True,
    )
    description = fields.Html()
    # Reception fields
    location_id = fields.Many2one(
        comodel_name="stock.location",
        domain=_domain_location_id,
        compute="_compute_location_id",
        store=True,
        readonly=False,
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        compute="_compute_warehouse_id",
        store=True,
    )
    reception_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Reception move",
        copy=False,
    )
    # Refund fields
    refund_id = fields.Many2one(
        comodel_name="account.move",
        copy=False,
    )
    refund_line_id = fields.Many2one(
        comodel_name="account.move.line",
        copy=False,
    )
    can_be_refunded = fields.Boolean(compute="_compute_can_be_refunded")
    # Delivery fields
    delivery_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="rma_id",
        string="Delivery reservation",
        copy=False,
    )
    delivery_picking_count = fields.Integer(
        string="Delivery count",
        compute="_compute_delivery_picking_count",
    )
    delivered_qty = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_delivered_qty",
        store=True,
    )
    can_be_returned = fields.Boolean(
        compute="_compute_can_be_returned",
    )
    can_be_replaced = fields.Boolean(
        compute="_compute_can_be_replaced",
    )
    can_be_locked = fields.Boolean(
        compute="_compute_can_be_locked",
    )
    can_be_finished = fields.Boolean(
        compute="_compute_can_be_finished",
    )
    remaining_qty = fields.Float(
        string="Remaining delivered qty",
        digits="Product Unit of Measure",
        compute="_compute_remaining_qty",
    )
    uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id", string="Category UoM"
    )
    # Split fields
    can_be_split = fields.Boolean(
        compute="_compute_can_be_split",
    )
    origin_split_rma_id = fields.Many2one(
        comodel_name="rma",
        string="Extracted from",
        copy=False,
    )

    def _compute_delivery_picking_count(self):
        # It is enough to count the moves to know how many pickings
        # there are because there will be a unique move linked to the
        # same picking and the same rma.
        rma_data = self.env["stock.move"].read_group(
            [("rma_id", "in", self.ids)],
            ["rma_id", "picking_id"],
            ["rma_id", "picking_id"],
            lazy=False,
        )
        mapped_data = Counter(map(lambda r: r["rma_id"][0], rma_data))
        for record in self:
            record.delivery_picking_count = mapped_data.get(record.id, 0)

    @api.depends(
        "delivery_move_ids",
        "delivery_move_ids.state",
        "delivery_move_ids.scrapped",
        "delivery_move_ids.product_uom_qty",
        "delivery_move_ids.quantity",
        "delivery_move_ids.product_uom",
        "product_uom",
    )
    def _compute_delivered_qty(self):
        """Compute 'delivered_qty' and 'delivered_qty_done' fields.

        delivered_qty: represents the quantity delivery or to be
        delivery. For each move in delivery_move_ids the quantity done
        is taken, if it is empty the reserved quantity is taken,
        otherwise the initial demand is taken.

        delivered_qty_done: represents the quantity delivered and done.
        For each 'done' move in delivery_move_ids the quantity done is
        taken. This field is used to control when the RMA cam be set
        to 'delivered' state.
        """
        for record in self:
            delivered_qty = 0.0
            for move in record.delivery_move_ids.filtered(
                lambda r: r.state != "cancel" and not r.scrapped
            ):
                if move.quantity:
                    quantity = move.product_uom._compute_quantity(
                        move.quantity, record.product_uom
                    )
                    delivered_qty += quantity
                elif move.product_uom_qty:
                    delivered_qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, record.product_uom
                    )
            record.delivered_qty = delivered_qty

    @api.depends("product_uom_qty", "delivered_qty")
    def _compute_remaining_qty(self):
        """Compute 'remaining_qty' and 'remaining_qty_to_done' fields.

        remaining_qty: is used to set a default quantity of replacing
        or returning of product to the customer.

        remaining_qty_to_done: the aim of this field to control when the
        RMA cam be set to 'delivered' state. An RMA with
        remaining_qty_to_done <= 0 can be set to 'delivery'. It is used
        in stock.move._action_done method of stock.move and
        rma.extract_quantity.
        """
        for r in self:
            r.remaining_qty = r.product_uom_qty - r.delivered_qty

    @api.depends(
        "state",
    )
    def _compute_can_be_refunded(self):
        """Compute 'can_be_refunded'. This field controls the visibility
        of 'Refund' button in the rma form view and determinates if
        an rma can be refunded. It is used in rma.action_refund method.
        """
        for record in self:
            record.can_be_refunded = record.state == "received"

    @api.depends("remaining_qty", "state")
    def _compute_can_be_returned(self):
        """Compute 'can_be_returned'. This field controls the visibility
        of the 'Return to customer' button in the rma form
        view and determinates if an rma can be returned to the customer.
        This field is used in:
        rma._compute_can_be_split
        rma._ensure_can_be_returned.
        """
        for r in self:
            r.can_be_returned = (
                r.state in ["received", "waiting_return"] and r.remaining_qty > 0
            )

    @api.depends("state")
    def _compute_can_be_replaced(self):
        """Compute 'can_be_replaced'. This field controls the visibility
        of 'Replace' button in the rma form
        view and determinates if an rma can be replaced.
        This field is used in:
        rma._compute_can_be_split
        rma._ensure_can_be_replaced.
        """
        for r in self:
            r.can_be_replaced = r.state in [
                "received",
                "waiting_replacement",
                "replaced",
            ]

    @api.depends("state", "remaining_qty")
    def _compute_can_be_finished(self):
        for rma in self:
            rma.can_be_finished = (
                rma.state in {"received", "waiting_replacement", "waiting_return"}
                and rma.remaining_qty > 0
            )

    @api.depends("product_uom_qty", "state", "remaining_qty")
    def _compute_can_be_split(self):
        """Compute 'can_be_split'. This field controls the
        visibility of 'Split' button in the rma form view and
        determinates if an rma can be split.
        This field is used in:
        rma._ensure_can_be_split
        """
        for r in self:
            if r.product_uom_qty > 1 and (
                (r.state == "waiting_return" and r.remaining_qty > 0)
                or (r.state == "waiting_replacement" and r.remaining_qty_to_done > 0)
            ):
                r.can_be_split = True
            else:
                r.can_be_split = False

    @api.depends("state")
    def _compute_can_be_locked(self):
        for r in self:
            r.can_be_locked = r.remaining_qty > 0 and r.state in [
                "received",
                "waiting_return",
                "waiting_replacement",
            ]

    @api.depends("location_id")
    def _compute_warehouse_id(self):
        for record in self.filtered("location_id"):
            record.warehouse_id = self.env["stock.warehouse"].search(
                [("rma_loc_id", "parent_of", record.location_id.id)], limit=1
            )

    @api.depends("user_id")
    def _compute_team_id(self):
        self.team_id = False
        for record in self.filtered("user_id"):
            record.team_id = (
                self.env["rma.team"]
                .sudo()
                .search(
                    [
                        "|",
                        ("user_id", "=", record.user_id.id),
                        ("member_ids", "=", record.user_id.id),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "child_of", record.company_id.ids),
                    ],
                    limit=1,
                )
            )

    @api.depends("partner_id")
    def _compute_partner_shipping_id(self):
        self.partner_shipping_id = False
        for record in self.filtered("partner_id"):
            address = record.partner_id.address_get(["delivery"])
            record.partner_shipping_id = address.get("delivery", False)

    @api.depends("partner_id")
    def _compute_partner_invoice_id(self):
        self.partner_invoice_id = False
        for record in self.filtered("partner_id"):
            address = record.partner_id.address_get(["invoice"])
            record.partner_invoice_id = address.get("invoice", False)

    @api.depends("picking_id")
    def _compute_move_id(self):
        """Empty move on picking change, but selecting the move in it if it's single."""
        self.move_id = False
        for record in self.filtered("picking_id"):
            if len(record.picking_id.move_ids) == 1:
                record.move_id = record.picking_id.move_ids.id

    @api.depends("move_id")
    def _compute_product_id(self):
        self.product_id = False
        for record in self.filtered("move_id"):
            record.product_id = record.move_id.product_id.id

    @api.depends("move_id")
    def _compute_product_uom_qty(self):
        self.product_uom_qty = False
        for record in self.filtered("move_id"):
            record.product_uom_qty = record.move_id.product_uom_qty

    @api.depends("move_id", "product_id")
    def _compute_product_uom(self):
        for record in self:
            if record.move_id:
                record.product_uom = record.move_id.product_uom.id
            elif record.product_id:
                record.product_uom = record.product_id.uom_id
            else:
                record.product_uom = False

    @api.depends("picking_id", "product_id", "company_id")
    def _compute_location_id(self):
        for record in self:
            if record.picking_id:
                warehouse = record.picking_id.picking_type_id.warehouse_id
                record.location_id = warehouse.rma_loc_id.id
            elif not record.location_id:
                company = record.company_id or self.env.company
                warehouse = self.env["stock.warehouse"].search(
                    [("company_id", "=", company.id)], limit=1
                )
                record.location_id = warehouse.rma_loc_id.id

    def _compute_access_url(self):
        for record in self:
            record.access_url = f"/my/rmas/{record.id}"

    # Constrains methods (@api.constrains)
    @api.constrains(
        "state",
        "partner_id",
        "partner_shipping_id",
        "partner_invoice_id",
        "product_id",
    )
    def _check_required_after_draft(self):
        """Check that RMAs are being created or edited with the
        necessary fields filled out. Only applies to 'Draft' and
        'Cancelled' states.
        """
        rma = self.filtered(lambda r: r.state not in ["draft", "cancelled"])
        rma._ensure_required_fields()

    # CRUD methods (ORM overrides)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                ir_sequence = self.env["ir.sequence"]
                if "company_id" in vals:
                    ir_sequence = ir_sequence.with_company(vals["company_id"])
                vals["name"] = ir_sequence.next_by_code("rma")
            # Assign a default team_id which will be the first in the sequence
            if not vals.get("team_id"):
                vals["team_id"] = self.env["rma.team"].search([], limit=1).id
        rmas = super().create(vals_list)
        # Send acknowledge when the RMA is created from the portal and the
        # company has the proper setting active. This context is set by the
        # `rma_sale` module.
        if self.env.context.get("from_portal"):
            rmas._send_draft_email()
        return rmas

    def copy(self, default=None):
        team = super().copy(default)
        for follower in self.message_follower_ids:
            team.message_subscribe(
                partner_ids=follower.partner_id.ids,
                subtype_ids=follower.subtype_ids.ids,
            )
        return team

    def unlink(self):
        if self.filtered(lambda r: r.state != "draft"):
            raise ValidationError(
                _("You cannot delete RMAs that are not in draft state")
            )
        return super().unlink()

    def _send_draft_email(self):
        """Send customer notifications they place the RMA from the portal"""
        for rma in self.filtered("company_id.send_rma_draft_confirmation"):
            rma.with_context(
                force_send=True,
                mark_rma_as_sent=True,
            ).message_post_with_source(
                rma.company_id.rma_mail_draft_confirmation_template_id.get_external_id()[
                    rma.company_id.rma_mail_draft_confirmation_template_id.id
                ],
                subtype_xmlid="rma.mt_rma_notification",
            )

    def _send_confirmation_email(self):
        """Auto send notifications"""
        for rma in self.filtered(lambda p: p.company_id.send_rma_confirmation):
            rma.with_context(
                force_send=True,
                mark_rma_as_sent=True,
            ).message_post_with_source(
                rma.company_id.rma_mail_confirmation_template_id.get_external_id()[
                    rma.company_id.rma_mail_confirmation_template_id.id
                ],
                subtype_xmlid="rma.mt_rma_notification",
            )

    def _send_receipt_confirmation_email(self):
        """Send customer notifications when the products are received"""
        for rma in self.filtered("company_id.send_rma_receipt_confirmation"):
            rma.with_context(
                force_send=True,
                mark_rma_as_sent=True,
            ).message_post_with_source(
                rma.company_id.rma_mail_receipt_confirmation_template_id.get_external_id()[
                    rma.company_id.rma_mail_receipt_confirmation_template_id.id
                ],
                subtype_xmlid="rma.mt_rma_notification",
            )

    # Action methods
    def action_rma_send(self):
        self.ensure_one()
        template = self.env.ref("rma.mail_template_rma_notification", False)
        template = self.company_id.rma_mail_confirmation_template_id or template
        form = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = {
            "default_model": "rma",
            "default_subtype_id": self.env.ref("rma.mt_rma_notification").id,
            "default_res_id": self.ids[0],
            "default_use_template": bool(template),
            "default_template_id": template and template.id or False,
            "default_composition_mode": "comment",
            "mark_rma_as_sent": True,
            "model_description": "RMA",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(form.id, "form")],
            "view_id": form.id,
            "target": "new",
            "context": ctx,
        }

    def _add_message_subscribe_partner(self):
        if self.partner_id and self.partner_id not in self.message_partner_ids:
            self.message_subscribe([self.partner_id.id])

    def action_confirm(self):
        """Invoked when 'Confirm' button in rma form view is clicked."""
        self.ensure_one()
        self._ensure_required_fields()
        if self.state == "draft":
            if self.picking_id:
                reception_move = self._create_receptions_from_picking()
            else:
                reception_move = self._create_receptions_from_product()
            reception_move.picked = True
            self.write({"reception_move_id": reception_move.id, "state": "confirmed"})
            self._add_message_subscribe_partner()
            self._send_confirmation_email()

    def action_refund(self):
        """Invoked when 'Refund' button in rma form view is clicked
        and 'rma_refund_action_server' server action is run.
        """
        group_dict = {}
        for record in self.filtered("can_be_refunded"):
            key = (record.partner_invoice_id.id, record.company_id.id)
            group_dict.setdefault(key, self.env["rma"])
            group_dict[key] |= record
        for rmas in group_dict.values():
            origin = ", ".join(rmas.mapped("name"))
            refund_vals = rmas[0]._prepare_refund_vals(origin)
            for rma in rmas:
                refund_vals["invoice_line_ids"].append(
                    (0, 0, rma._prepare_refund_line_vals())
                )
            refund = self.env["account.move"].sudo().create(refund_vals)
            refund.with_user(self.env.uid).message_post_with_source(
                "mail.message_origin_link",
                render_values={"self": refund, "origin": rmas},
                subtype_id=self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_note"),
            )
            for line in refund.invoice_line_ids:
                line.rma_id.write(
                    {
                        "refund_line_id": line.id,
                        "refund_id": refund.id,
                        "state": "refunded",
                    }
                )

    def action_replace(self):
        """Invoked when 'Replace' button in rma form view is clicked."""
        self.ensure_one()
        self._ensure_can_be_replaced()
        # Force active_id to avoid issues when coming from smart buttons
        # in other models
        action = (
            self.env.ref("rma.rma_delivery_wizard_action")
            .sudo()
            .with_context(active_id=self.id)
            .read()[0]
        )
        action["name"] = "Replace product(s)"
        action["context"] = dict(self.env.context)
        action["context"].update(
            active_id=self.id,
            active_ids=self.ids,
            rma_delivery_type="replace",
        )
        return action

    def action_return(self):
        """Invoked when 'Return to customer' button in rma form
        view is clicked.
        """
        self.ensure_one()
        self._ensure_can_be_returned()
        # Force active_id to avoid issues when coming from smart buttons
        # in other models
        action = (
            self.env.ref("rma.rma_delivery_wizard_action")
            .sudo()
            .with_context(active_id=self.id)
            .read()[0]
        )
        action["context"] = dict(self.env.context)
        action["context"].update(
            active_id=self.id,
            active_ids=self.ids,
            rma_delivery_type="return",
        )
        return action

    def action_split(self):
        """Invoked when 'Split' button in rma form view is clicked."""
        self.ensure_one()
        self._ensure_can_be_split()
        # Force active_id to avoid issues when coming from smart buttons
        # in other models
        action = (
            self.env.ref("rma.rma_split_wizard_action")
            .sudo()
            .with_context(active_id=self.id)
            .read()[0]
        )
        action["context"] = dict(self.env.context)
        action["context"].update(active_id=self.id, active_ids=self.ids)
        return action

    def action_finish(self):
        """Invoked when a user wants to manually finalize the RMA"""
        self.ensure_one()
        self._ensure_can_be_returned()
        # Force active_id to avoid issues when coming from smart buttons
        # in other models
        action = (
            self.env.ref("rma.rma_finalization_wizard_action")
            .sudo()
            .with_context(active_id=self.id)
            .read()[0]
        )
        action["context"] = dict(self.env.context)
        action["context"].update(active_id=self.id, active_ids=self.ids)
        return action

    def action_cancel(self):
        """Invoked when 'Cancel' button in rma form view is clicked."""
        self.mapped("reception_move_id")._action_cancel()
        self.write({"state": "cancelled"})

    def action_draft(self):
        cancelled_rma = self.filtered(lambda r: r.state == "cancelled")
        cancelled_rma.write({"state": "draft"})

    def action_lock(self):
        """Invoked when 'Lock' button in rma form view is clicked."""
        self.filtered("can_be_locked").write({"state": "locked"})

    def action_unlock(self):
        """Invoked when 'Unlock' button in rma form view is clicked."""
        locked_rma = self.filtered(lambda r: r.state == "locked")
        locked_rma.write({"state": "received"})

    def action_preview(self):
        """Invoked when 'Preview' button in rma form view is clicked."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": self.get_portal_url(),
        }

    def action_view_receipt(self):
        """Invoked when 'Receipt' smart button in rma form view is clicked."""
        self.ensure_one()
        # Force active_id to avoid issues when coming from smart buttons
        # in other models
        action = (
            self.env.ref("stock.action_picking_tree_all")
            .sudo()
            .with_context(active_id=self.id)
            .read()[0]
        )
        action.update(
            res_id=self.reception_move_id.picking_id.id,
            view_mode="form",
            view_id=False,
            views=False,
        )
        return action

    def action_view_refund(self):
        """Invoked when 'Refund' smart button in rma form view is clicked."""
        self.ensure_one()
        return {
            "name": _("Refund"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.move",
            "views": [(self.env.ref("account.view_move_form").id, "form")],
            "res_id": self.refund_id.id,
        }

    def action_view_delivery(self):
        """Invoked when 'Delivery' smart button in rma form view is clicked."""
        action = (
            self.env.ref("stock.action_picking_tree_all")
            .sudo()
            .with_context(active_id=self.id)
            .read()[0]
        )
        picking = self.delivery_move_ids.mapped("picking_id")
        if len(picking) > 1:
            action["domain"] = [("id", "in", picking.ids)]
        elif picking:
            action.update(
                res_id=picking.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        return action

    # Validation business methods
    def _ensure_required_fields(self):
        """This method is used to ensure the following fields are not empty:
        [
            'partner_id', 'partner_invoice_id', 'partner_shipping_id',
            'product_id', 'location_id'
        ]

        This method is intended to be called on confirm RMA action and is
        invoked by:
        rma._check_required_after_draft
        rma.action_confirm
        """
        required = [
            "partner_id",
            "partner_shipping_id",
            "partner_invoice_id",
            "product_id",
            "location_id",
        ]
        for record in self:
            desc = ""
            for field in filter(lambda item: not record[item], required):
                field_record = (
                    self.env["ir.model.fields"]
                    .sudo()
                    .search(
                        [
                            ("model_id.model", "=", record._name),
                            ("name", "=", field),
                        ]
                    )
                )
                desc += f"\n{field_record.field_description}"
            if desc:
                raise ValidationError(_("Required field(s):%s") % desc)

    def _ensure_can_be_returned(self):
        """This method is intended to be invoked after user click on
        'Replace' or 'Return to customer' button (before the delivery wizard
        is launched) and after confirm the wizard.

        This method is invoked by:
        rma.action_replace
        rma.action_return
        rma.create_replace
        rma.create_return
        """
        if len(self) == 1:
            if not self.can_be_returned:
                raise ValidationError(_("This RMA cannot perform a return."))
        elif not self.filtered("can_be_returned"):
            raise ValidationError(_("None of the selected RMAs can perform a return."))

    def _ensure_can_be_replaced(self):
        """This method is intended to be invoked after user click on
        'Replace' button (before the delivery wizard
        is launched) and after confirm the wizard.

        This method is invoked by:
        rma.action_replace
        rma.create_replace
        """
        if len(self) == 1:
            if not self.can_be_replaced:
                raise ValidationError(_("This RMA cannot perform a replacement."))
        elif not self.filtered("can_be_replaced"):
            raise ValidationError(
                _("None of the selected RMAs can perform a replacement.")
            )

    def _ensure_can_be_split(self):
        """intended to be called before launch and after save the split wizard.
        invoked by:
        rma.action_split
        rma.extract_quantity
        """
        self.ensure_one()
        if not self.can_be_split:
            raise ValidationError(_("This RMA cannot be split."))

    def _ensure_qty_to_return(self, qty=None, uom=None):
        """This method is intended to be invoked after confirm the wizard.
        invoked by: rma.create_return
        """
        if qty and uom:
            if uom != self.product_uom:
                qty = uom._compute_quantity(qty, self.product_uom)
            if qty > self.remaining_qty:
                raise ValidationError(
                    _("The quantity to return is greater than " "remaining quantity.")
                )

    def _ensure_qty_to_extract(self, qty, uom):
        """This method is intended to be invoked after confirm the wizard.
        invoked by: rma.extract_quantity
        """
        to_split_uom_qty = qty
        if uom != self.product_uom:
            to_split_uom_qty = uom._compute_quantity(qty, self.product_uom)
        if to_split_uom_qty > self.remaining_qty:
            raise ValidationError(
                _(
                    "Quantity to extract cannot be greater than remaining"
                    " delivery quantity (%(remaining_qty)s %(product_uom)s)"
                )
                % (
                    {
                        "remaining_qty": self.remaining_qty,
                        "product_uom": self.product_uom.name,
                    }
                )
            )

    # Reception business methods
    def _create_receptions_from_picking(self):
        self.ensure_one()
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=self.picking_id.ids,
                active_id=self.picking_id.id,
                active_model="stock.picking",
            )
        )
        return_wizard = stock_return_picking_form.save()
        if self.location_id:
            return_wizard.location_id = self.location_id
        return_wizard.product_return_moves.filtered(
            lambda r: r.move_id != self.move_id
        ).unlink()
        return_line = return_wizard.product_return_moves
        return_line.update(
            {
                "quantity": self.product_uom_qty,
                # The to_refund field is now True by default, which isn't right in the
                # RMA creation context
                "to_refund": False,
            }
        )
        # set_rma_picking_type is to override the copy() method of stock
        # picking and change the default picking type to rma picking type.
        picking_action = return_wizard.with_context(
            set_rma_picking_type=True
        ).create_returns()
        picking_id = picking_action["res_id"]
        picking = self.env["stock.picking"].browse(picking_id)
        picking.origin = f"{self.name} ({picking.origin})"
        move = picking.move_ids
        move.priority = self.priority
        return move

    def _create_receptions_from_product(self):
        self.ensure_one()
        picking = self.env["stock.picking"].create(self._prepare_picking_vals())
        picking.action_confirm()
        picking.action_assign()
        picking.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": picking, "origin": self},
            subtype_id=self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_note"),
        )
        return picking.move_ids

    def _prepare_picking_vals(self):
        return {
            "picking_type_id": self.warehouse_id.rma_in_type_id.id,
            "origin": self.name,
            "partner_id": self.partner_shipping_id.id,
            "location_id": self.partner_shipping_id.property_stock_customer.id,
            "location_dest_id": self.location_id.id,
            "move_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": self.product_id.id,
                        # same text as origin move or product text in partner lang
                        "name": self.move_id.name
                        or self.product_id.with_context(
                            lang=self.partner_id.lang or "en_US"
                        ).display_name,
                        "location_id": (
                            self.partner_shipping_id.property_stock_customer.id
                        ),
                        "location_dest_id": self.location_id.id,
                        "product_uom_qty": self.product_uom_qty,
                    },
                )
            ],
        }

    # Extract business methods
    def extract_quantity(self, qty, uom):
        self.ensure_one()
        self._ensure_can_be_split()
        self._ensure_qty_to_extract(qty, uom)
        self.product_uom_qty -= uom._compute_quantity(qty, self.product_uom)
        if self.remaining_qty <= 0:
            if self.state == "waiting_return":
                self.state = "returned"
            elif self.state == "waiting_replacement":
                self.state = "replaced"
        extracted_rma = self.copy(
            {
                "origin": self.name,
                "product_uom_qty": qty,
                "product_uom": uom.id,
                "state": "received",
                "reception_move_id": self.reception_move_id.id,
                "origin_split_rma_id": self.id,
            }
        )
        extracted_rma.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": extracted_rma, "origin": self},
            subtype_id=self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_note"),
        )
        self.message_post(
            body=_(
                'Split: <a href="#" data-oe-model="rma" '
                'data-oe-id="%(id)d">%(name)s</a> has been created.'
            )
            % ({"id": extracted_rma.id, "name": extracted_rma.name})
        )
        return extracted_rma

    # Refund business methods
    def _prepare_refund_vals(self, origin=False):
        """Hook method for preparing the refund Form.

        This method could be override in order to add new custom field
        values in the refund creation.

        invoked by:
        rma.action_refund
        """
        self.ensure_one()
        return {
            "move_type": "out_refund",
            "company_id": self.company_id.id,
            "partner_id": self.partner_invoice_id.id,
            "invoice_payment_term_id": False,
            "invoice_origin": origin,
            "invoice_line_ids": [],
        }

    def _prepare_refund_line_vals(self):
        """Hook method for preparing a refund line Form.

        This method could be override in order to add new custom field
        values in the refund line creation.

        invoked by:
        rma.action_refund
        """
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "quantity": self.product_uom_qty,
            "product_uom_id": self.product_uom.id,
            "price_unit": self.product_id.lst_price,
            "rma_id": self.id,
        }

    # Returning business methods
    def create_return(self, scheduled_date, qty=None, uom=None):
        """Intended to be invoked by the delivery wizard"""
        group_returns = self.env.company.rma_return_grouping
        if "rma_return_grouping" in self.env.context:
            group_returns = self.env.context.get("rma_return_grouping")
        self._ensure_can_be_returned()
        self._ensure_qty_to_return(qty, uom)
        group_dict = {}
        rmas_to_return = self.filtered("can_be_returned")
        for record in rmas_to_return:
            key = (
                record.partner_shipping_id.id,
                record.company_id.id,
                record.warehouse_id,
            )
            group_dict.setdefault(key, self.env["rma"])
            group_dict[key] |= record
        if group_returns:
            grouped_rmas = group_dict.values()
        else:
            grouped_rmas = rmas_to_return
        for rmas in grouped_rmas:
            origin = ", ".join(rmas.mapped("name"))
            picking_vals = rmas[0]._prepare_returning_picking_vals(origin)
            for rma in rmas:
                picking_vals["move_ids"].append(
                    (0, 0, rma._prepare_returning_move_vals(scheduled_date, qty, uom))
                )
            picking = self.env["stock.picking"].create(picking_vals)
            for rma in rmas:
                rma.message_post(
                    body=_(
                        'Return: <a href="#" data-oe-model="stock.picking" '
                        'data-oe-id="%(id)d">%(name)s</a> has been created.'
                    )
                    % ({"id": picking.id, "name": picking.name})
                )
            picking.action_confirm()
            picking.action_assign()
            picking.message_post_with_source(
                "mail.message_origin_link",
                render_values={"self": picking, "origin": rmas},
                subtype_id=self.env["ir.model.data"]._xmlid_to_res_id("mail.mt_note"),
            )
        rmas_to_return.write({"state": "waiting_return"})

    def _prepare_returning_picking_vals(self, origin=None):
        self.ensure_one()
        return {
            "picking_type_id": self.warehouse_id.rma_out_type_id.id,
            "location_id": self.location_id.id,
            "location_dest_id": self.reception_move_id.location_id.id,
            "origin": origin or self.name,
            "partner_id": self.partner_shipping_id.id,
            "company_id": self.company_id.id,
            "move_ids": [],
        }

    def _prepare_returning_move_vals(self, scheduled_date, quantity=None, uom=None):
        self.ensure_one()
        return {
            "product_id": self.product_id.id,
            "name": self.product_id.with_context(
                lang=self.partner_shipping_id.lang or "en_US"
            ).display_name,
            "product_uom_qty": quantity or self.product_uom_qty,
            "product_uom": uom and uom.id or self.product_uom.id,
            "location_id": self.location_id.id,
            "location_dest_id": self.reception_move_id.location_id.id,
            "date": scheduled_date,
            "rma_id": self.id,
            "move_orig_ids": [(4, self.reception_move_id.id)],
            "company_id": self.company_id.id,
        }

    # Replacing business methods
    def create_replace(self, scheduled_date, warehouse, product, qty, uom):
        """Intended to be invoked by the delivery wizard"""
        self.ensure_one()
        self._ensure_can_be_replaced()
        moves_before = self.delivery_move_ids
        self._action_launch_stock_rule(scheduled_date, warehouse, product, qty, uom)
        new_moves = self.delivery_move_ids - moves_before
        body = ""
        # The product replacement could explode into several moves like in the case of
        # MRP BoM Kits
        for new_move in new_moves:
            body += (
                _(
                    'Replacement: Move <a href="#" data-oe-model="stock.move"'
                    ' data-oe-id="%(move_id)d">%(move_name)s</a> (Picking <a'
                    ' href="#" data-oe-model="stock.picking"'
                    ' data-oe-id="%(picking_id)d"> %(picking_name)s</a>) has'
                    " been created."
                )
                % (
                    {
                        "move_id": new_move.id,
                        "move_name": new_move.display_name,
                        "picking_id": new_move.picking_id.id,
                        "picking_name": new_move.picking_id.name,
                    }
                )
                + "\n"
            )
        self.message_post(
            body=body
            or _(
                "Replacement:<br/>"
                'Product <a href="#" data-oe-model="product.product" '
                'data-oe-id="%(id)d">%(name)s</a><br/>'
                "Quantity %(qty)s %(uom)s<br/>"
                "This replacement did not create a new move, but one of "
                "the previously created moves was updated with this data."
            )
            % (
                {
                    "id": product.id,
                    "name": product.display_name,
                    "qty": qty,
                    "uom": uom.name,
                }
            )
        )
        if self.state != "waiting_replacement":
            self.state = "waiting_replacement"

    def _action_launch_stock_rule(
        self,
        scheduled_date,
        warehouse,
        product,
        qty,
        uom,
    ):
        """Creates a delivery picking and launch stock rule. It is invoked by:
        rma.create_replace
        """
        self.ensure_one()
        if self.product_id.type not in ("consu", "product"):
            return
        if not self.procurement_group_id:
            self.procurement_group_id = (
                self.env["procurement.group"]
                .create(
                    {
                        "name": self.name,
                        "move_type": "direct",
                        "partner_id": self.partner_shipping_id.id,
                    }
                )
                .id
            )
        values = self._prepare_procurement_values(
            self.procurement_group_id, scheduled_date, warehouse
        )
        procurement = self.env["procurement.group"].Procurement(
            product,
            qty,
            uom,
            self.partner_shipping_id.property_stock_customer,
            self.product_id.display_name,
            self.procurement_group_id.name,
            self.company_id,
            values,
        )
        self.env["procurement.group"].run([procurement])
        return True

    def _prepare_procurement_values(
        self,
        group_id,
        scheduled_date,
        warehouse,
    ):
        self.ensure_one()
        return {
            "company_id": self.company_id,
            "group_id": group_id,
            "date_planned": scheduled_date,
            "warehouse_id": warehouse,
            "partner_id": self.partner_shipping_id.id,
            "rma_id": self.id,
            "priority": self.priority,
        }

    # Mail business methods
    def _creation_subtype(self):
        if self.state in ("draft"):
            return self.env.ref("rma.mt_rma_draft")
        else:
            return super()._creation_subtype()

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "state" in init_values:
            if self.state == "draft":
                return self.env.ref("rma.mt_rma_draft")
            elif self.state == "confirmed":
                return self.env.ref("rma.mt_rma_notification")
        return super()._track_subtype(init_values)

    def message_new(self, msg_dict, custom_values=None):
        """Extract the needed values from an incoming rma emails data-set
        to be used to create an RMA.
        """
        if custom_values is None:
            custom_values = {}
        subject = msg_dict.get("subject", "")
        body = html2plaintext(msg_dict.get("body", ""))
        desc = _(
            "<b>E-mail subject:</b> %(subject)s<br/><br/><b>E-mail"
            " body:</b><br/>%(body)s"
        ) % ({"subject": subject, "body": body})
        defaults = {
            "description": desc,
            "name": _("New"),
            "origin": _("Incoming e-mail"),
        }
        if msg_dict.get("author_id"):
            partner = self.env["res.partner"].browse(msg_dict.get("author_id"))
            defaults.update(
                partner_id=partner.id,
                partner_invoice_id=partner.address_get(["invoice"]).get(
                    "invoice", False
                ),
            )
        if msg_dict.get("priority"):
            defaults["priority"] = msg_dict.get("priority")
        defaults.update(custom_values)
        rma = super().message_new(msg_dict, custom_values=defaults)
        if rma.user_id and rma.user_id.partner_id not in rma.message_partner_ids:
            rma.message_subscribe([rma.user_id.partner_id.id])
        return rma

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        """Set 'sent' field to True when an email is sent from rma form
        view. This field (sent) is used to set the appropriate style to the
        'Send by Email' button in the rma form view.
        """
        if self.env.context.get("mark_rma_as_sent"):
            self.write({"sent": True})
        # mail_post_autofollow=True to include email recipient contacts as
        # RMA followers
        self_with_context = self.with_context(mail_post_autofollow=True)
        return super(Rma, self_with_context).message_post(**kwargs)

    def _message_get_suggested_recipients(self):
        recipients = super()._message_get_suggested_recipients()
        try:
            for record in self.filtered("partner_id"):
                record._message_add_suggested_recipient(
                    recipients, partner=record.partner_id, reason=_("Customer")
                )
        except AccessError as e:  # no read access rights
            _logger.debug(e)
        return recipients

    # Reporting business methods
    def _get_report_base_filename(self):
        self.ensure_one()
        return "RMA Report - %s" % self.name

    # Other business methods

    def update_received_state_on_reception(self):
        """Invoked by:
        [stock.move]._action_done
        Here we can attach methods to trigger when the customer products
        are received on the RMA location, such as automatic notifications
        """
        self.write({"state": "received"})
        self._send_receipt_confirmation_email()

    def update_received_state(self):
        """Invoked by:
        [stock.move].unlink
        [stock.move]._action_cancel
        """
        rma = self.filtered(lambda r: r.delivered_qty == 0)
        if rma:
            rma.write({"state": "received"})

    def update_replaced_state(self):
        """Invoked by:
        [stock.move]._action_done
        [stock.move].unlink
        [stock.move]._action_cancel
        """
        rma = self.filtered(
            lambda r: (r.state == "waiting_replacement" and 0 >= r.remaining_qty)
        )
        if rma:
            rma.write({"state": "replaced"})

    def update_returned_state(self):
        """Invoked by [stock.move]._action_done"""
        rma = self.filtered(
            lambda r: (r.state == "waiting_return" and r.remaining_qty <= 0)
        )
        if rma:
            rma.write({"state": "returned"})