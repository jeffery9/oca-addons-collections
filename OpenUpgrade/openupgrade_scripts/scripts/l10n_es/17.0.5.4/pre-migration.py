# Copyright 2025 Tecnativa - Carlos Roca
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _pre_create_and_fill_l10n_es_is_simplified(env):
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_move ADD COLUMN l10n_es_is_simplified BOOL DEFAULT false",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_move ALTER COLUMN l10n_es_is_simplified DROP DEFAULT",
    )
    # The field is filled with the first part of the compute without considering the
    # partner_simplified part, as this record is created during the installation.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET l10n_es_is_simplified = (
            partner_id IS NULL
            AND move_type IN ('in_receipt', 'out_receipt')
        )
        """,
    )


def _xml_id_renaming_account_tax_tamplate(env):
    # In 17.0 the tax template xml_id of Intra-Community (Goods) is changed. With
    # this method the xml_id is set correctly.
    imds = env["ir.model.data"].search(
        [
            ("module", "=", "account"),
            ("model", "=", "account.tax"),
            ("name", "=like", "%_account_tax_template_s_iva0_ic"),
        ]
    )
    for imd in imds:
        imd.name = imd.name.replace(
            "account_tax_template_s_iva0_ic", "account_tax_template_s_iva0_g_i"
        )


def _remove_xml_id_account_fiscal_position(env):
    # In 17.0 account.fiscal.position.tax and account.fiscal.position.account don't have
    # xml_id. With this method they are removed.
    for company in env["res.company"].search([]):
        openupgrade.logged_query(
            env.cr,
            f"""
            DELETE FROM ir_model_data
            WHERE module='l10n_es'
            AND model IN (
                'account.fiscal.position.tax', 'account.fiscal.position.account'
            ) AND name LIKE '{company.id}_%'
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    _pre_create_and_fill_l10n_es_is_simplified(env)
    _xml_id_renaming_account_tax_tamplate(env)
    _remove_xml_id_account_fiscal_position(env)
