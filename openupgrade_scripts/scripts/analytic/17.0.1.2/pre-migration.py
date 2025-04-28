# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Hunki enterprises - Holger Brunn
# Copyright 2024,2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _fill_config_parameter_analytic_project_plan(env):
    """If the system parameter is already set (because we have pre-filled according our
    needs), we don't touch it.

    If not, we check if there's already an existing ir.model.data entry for projects
    according standard data (also pre-filled externally).

    Finally, if not found, we will put the next available ID, as regular ORM update
    process will load the record "analytic.analytic_plan_projects", and creates the
    record that belongs to the "Projects" plan.
    """
    if env["ir.config_parameter"].get_param("analytic.project_plan", False):
        return
    imd = env["ir.model.data"].search(
        [("module", "=", "analytic"), ("name", "=", "analytic_plan_projects")]
    )
    plan_id = imd.res_id
    if not plan_id:
        env.cr.execute("SELECT last_value + 1 FROM account_analytic_plan_id_seq;")
        plan_id = env.cr.fetchone()[0]
    env["ir.config_parameter"].set_param("analytic.project_plan", str(plan_id))


def _analytic_applicability_fill_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_analytic_applicability
        ADD COLUMN IF NOT EXISTS company_id INTEGER;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_config_parameter_analytic_project_plan(env)
    _analytic_applicability_fill_company_id(env)
    # Drop triagram index on name column of account.analytic.account
    # to avoid error when loading registry, it will be recreated
    openupgrade.logged_query(
        env.cr,
        """
        DROP INDEX IF EXISTS account_analytic_account_name_index;
        """,
    )
    # Save company_id field of analytic plans for modules reinstating this
    # to pick up
    openupgrade.copy_columns(
        env.cr, {"account_analytic_plan": [("company_id", None, None)]}
    )
