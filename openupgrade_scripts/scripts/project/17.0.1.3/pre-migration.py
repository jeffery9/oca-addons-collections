# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _rename_fields(env):
    openupgrade.rename_fields(
        env,
        [
            ("project.task", "project_task", "planned_hours", "allocated_hours"),
            (
                "project.task.type",
                "project_task_type",
                "auto_validation_kanban_state",
                "auto_validation_state",
            ),
        ],
    )


def _convert_project_task_state(env):
    """Handle kanban_state, is_closed, etc to state conversion."""
    openupgrade.add_fields(
        env, [("state", "project.task", "project_task", "selection", False, "project")]
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task
        SET state = CASE
            WHEN kanban_state = 'done' THEN CASE
                WHEN is_closed THEN '1_done'
                ELSE '03_approved'
            END
            WHEN kanban_state = 'blocked' THEN CASE
                WHEN is_closed THEN '1_canceled'
                ELSE '02_changes_requested'
            END
            ELSE '01_in_progress'
        END
        WHERE kanban_state IN ('done', 'blocked', 'normal');
        """,
    )
    # Secnd pass for setting '04_waiting_normal' on tasks with "Blocked By" entries
    # that qualify
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task pt
        SET state = '04_waiting_normal'
        FROM task_dependencies_rel rel
        JOIN project_task dep ON dep.id = rel.depends_on_id
        WHERE rel.task_id = pt.id AND dep.state NOT IN ('1_done', '1_canceled')
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _rename_fields(env)
    _convert_project_task_state(env)
