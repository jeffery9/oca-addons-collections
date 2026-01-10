# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "l10n_dk.account_tag_Goodwill_licenses_etc",
            "l10n_dk.account_tag_Payroll_related_liabilities",
            "l10n_dk.account_tag_administration_costs",
            "l10n_dk.account_tag_bank_loans",
            "l10n_dk.account_tag_cars_equipment_costs",
            "l10n_dk.account_tag_credit_institutions",
            "l10n_dk.account_tag_depreciation",
            "l10n_dk.account_tag_direct_costs",
            "l10n_dk.account_tag_equity_corporations",
            "l10n_dk.account_tag_equity_individual_enterprises",
            "l10n_dk.account_tag_extraordinary_expenses",
            "l10n_dk.account_tag_extraordinary_income",
            "l10n_dk.account_tag_financial_expenses",
            "l10n_dk.account_tag_financial_income",
            "l10n_dk.account_tag_inventories",
            "l10n_dk.account_tag_land_buildings",
            "l10n_dk.account_tag_liquidity",
            "l10n_dk.account_tag_other_current_liabilities",
            "l10n_dk.account_tag_other_equipment_tools_inventory",
            "l10n_dk.account_tag_other_receivables",
            "l10n_dk.account_tag_payable",
            "l10n_dk.account_tag_prepayments",
            "l10n_dk.account_tag_prepayments_from_customers",
            "l10n_dk.account_tag_receivable",
            "l10n_dk.account_tag_revenue",
            "l10n_dk.account_tag_rooms_costs",
            "l10n_dk.account_tag_sales_promotions_costs",
            "l10n_dk.account_tag_staff_costs",
            "l10n_dk.account_tag_vat_taxes",
            "l10n_dk.account_tag_work_in_progress",
        ],
    )
