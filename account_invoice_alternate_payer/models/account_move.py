# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import _, api, fields, models
from odoo.tools import float_is_zero


class AccountMove(models.Model):

    _inherit = "account.move"

    alternate_payer_id = fields.Many2one(
        "res.partner",
        string="Alternate Payer",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="If set, this will be the partner that we expect to pay or to "
        "be paid by. If not set, the payor is by default the "
        "commercial",
    )

    @api.depends("commercial_partner_id", "alternate_payer_id")
    def _compute_bank_partner_id(self):
        super_moves = self.filtered(
            lambda r: not r.alternate_payer_id or not r.is_outbound()
        )
        for move in self - super_moves:
            if move.is_outbound() and move.alternate_payer_id:
                move.bank_partner_id = move.alternate_payer_id
        return super(
            AccountMove,
            super_moves,
        )._compute_bank_partner_id()

    @api.onchange("alternate_payer_id")
    def _onchange_alternate_payer_id(self):
        return self._onchange_partner_id()

    @contextmanager
    def _sync_dynamic_line(
        self,
        existing_key_fname,
        needed_vals_fname,
        needed_dirty_fname,
        line_type,
        container,
    ):
        records_with_alternate_player = container.get("records").filtered(
            lambda x: x.alternate_payer_id
        )
        with super()._sync_dynamic_line(
            existing_key_fname,
            needed_vals_fname,
            needed_dirty_fname,
            line_type,
            container,
        ):
            if line_type == "payment_term" and records_with_alternate_player:
                for invoice in container.get("records").filtered(
                    lambda x: x.alternate_payer_id
                ):
                    payment_term_lines = invoice.line_ids.filtered(
                        lambda x: x.display_type == "payment_term"
                    )
                    payment_term_lines.write(
                        {
                            "partner_id": invoice.alternate_payer_id.id,
                        }
                    )
            yield

    def _compute_payments_widget_to_reconcile_info(self):
        super_moves = self.filtered(lambda r: not r.alternate_payer_id)
        for move in self - super_moves:
            move.invoice_outstanding_credits_debits_widget = False
            move.invoice_has_outstanding = False
            if (
                move.state != "posted"
                or move.payment_state != "not_paid"
                or not move.is_invoice(include_receipts=True)
            ):
                continue
            pay_term_line_ids = move.line_ids.filtered(
                lambda line: line.account_id.account_type
                in ("asset_receivable", "liability_payable")
            )

            domain = [
                ("account_id", "in", pay_term_line_ids.mapped("account_id").ids),
                "|",
                ("move_id.state", "=", "posted"),
                "&",
                ("move_id.state", "=", "draft"),
                ("partner_id", "=", move.alternate_payer_id.id),
                ("reconciled", "=", False),
                "|",
                ("amount_residual", "!=", 0.0),
                ("amount_residual_currency", "!=", 0.0),
            ]

            if move.is_inbound():
                domain.extend([("credit", ">", 0), ("debit", "=", 0)])
                type_payment = _("Outstanding credits")
            else:
                domain.extend([("credit", "=", 0), ("debit", ">", 0)])
                type_payment = _("Outstanding debits")
            info = {"title": "", "outstanding": True, "content": [], "move_id": move.id}
            lines = self.env["account.move.line"].search(domain)
            currency_id = move.currency_id
            for line in lines:
                # get the outstanding residual value in invoice currency
                if line.currency_id and line.currency_id == move.currency_id:
                    amount_to_show = abs(line.amount_residual_currency)
                else:
                    currency = line.company_id.currency_id
                    amount_to_show = currency._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date or fields.Date.today(),
                    )
                if float_is_zero(
                    amount_to_show, precision_rounding=move.currency_id.rounding
                ):
                    continue
                info["content"].append(
                    {
                        "journal_name": line.ref or line.move_id.name,
                        "amount": amount_to_show,
                        "currency": currency_id.symbol,
                        "id": line.id,
                        "position": currency_id.position,
                        "digits": [69, move.currency_id.decimal_places],
                        "payment_date": fields.Date.to_string(line.date),
                    }
                )
            info["title"] = type_payment
            move.invoice_outstanding_credits_debits_widget = info
            move.invoice_has_outstanding = True
        return super(
            AccountMove, super_moves
        )._compute_payments_widget_to_reconcile_info()


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def write(self, values):
        # CHECK ME: this change to commercial partner when find difference between main partner
        # https://github.com/odoo/odoo/blob/16.0/addons/account/models/account_move.py#L3431
        if "partner_id" in values and len(values.keys()) == 1:
            lines_to_skip = self.filtered(
                lambda x: x.move_id.alternate_payer_id
                and x.display_type == "payment_term"
                and x.partner_id == x.move_id.alternate_payer_id
            )
            return super(AccountMoveLine, self - lines_to_skip).write(values)
        return super().write(values)
