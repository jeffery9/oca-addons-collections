# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Set to False so as not to change the behaviour of the website with new things.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_tag SET visible_on_ecommerce = FALSE
        WHERE visible_on_ecommerce IS DISTINCT FROM FALSE
        """,
    )
    if openupgrade.column_exists(env.cr, "ir_attachment", "product_downloadable"):
        # due to website_sale_digital
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE product_document
            SET attached_on = 'sale_order'
            FROM ir_attachment ir
            WHERE product_document.ir_attachment_id = ir.id
              AND ir.product_downloadable
            """,
        )
