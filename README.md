
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/account-invoicing&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/account-invoicing/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/account-invoicing/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/account-invoicing/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/account-invoicing/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/account-invoicing/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/account-invoicing)
[![Translation Status](https://translation.odoo-community.org/widgets/account-invoicing-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/account-invoicing-17-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# account-invoicing

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_global_discount](account_global_discount/) | 17.0.1.0.0 |  | Account Global Discount
[account_invoice_block_payment](account_invoice_block_payment/) | 17.0.1.0.0 |  | Module to block payment of invoices
[account_invoice_blocking](account_invoice_blocking/) | 17.0.1.0.2 |  | Set a blocking (No Follow-up) flag on invoices
[account_invoice_crm_tag](account_invoice_crm_tag/) | 17.0.1.0.0 |  | Account Invoice CRM Tag
[account_invoice_customer_no_autofollow](account_invoice_customer_no_autofollow/) | 17.0.1.0.0 |  | Do not add customer as follower in Invoices
[account_invoice_date_due](account_invoice_date_due/) | 17.0.1.0.0 | [![luisg123v](https://github.com/luisg123v.png?size=30px)](https://github.com/luisg123v) [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Update Invoice's Due Date
[account_invoice_fixed_discount](account_invoice_fixed_discount/) | 17.0.1.1.0 |  | Allows to apply fixed amount discounts in invoices.
[account_invoice_pricelist](account_invoice_pricelist/) | 17.0.1.0.1 |  | Add partner pricelist on invoices
[account_invoice_refund_link](account_invoice_refund_link/) | 17.0.1.0.1 |  | Show links between refunds and their originator invoices.
[account_invoice_section_sale_order](account_invoice_section_sale_order/) | 17.0.2.1.0 |  | For invoices targetting multiple sale order addsections with sale order name.
[account_invoice_show_currency_rate](account_invoice_show_currency_rate/) | 17.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Show currency rate in invoices.
[account_invoice_subscription_per_contact](account_invoice_subscription_per_contact/) | 17.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Account Invoice Subscription per contact
[account_invoice_transmit_method](account_invoice_transmit_method/) | 17.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Configure invoice transmit method (email, post, portal, ...)
[account_invoice_warn_message](account_invoice_warn_message/) | 17.0.1.0.0 |  | Add a popup warning on invoice to ensure warning is populated
[account_manual_currency](account_manual_currency/) | 17.0.1.0.0 |  | Allows to manual currency of Accounting
[account_move_cancel_confirm](account_move_cancel_confirm/) | 17.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Account Move Cancel Confirm
[account_move_tier_validation](account_move_tier_validation/) | 17.0.1.0.1 |  | Extends the functionality of Account Moves to support a tier validation process.
[partner_invoicing_mode](partner_invoicing_mode/) | 17.0.1.0.0 |  | Base module for handling multiple partner invoicing mode
[portal_account_personal_data_only](portal_account_personal_data_only/) | 17.0.1.0.0 |  | Portal Accounting Personal Data Only
[product_form_account_move_line_link](product_form_account_move_line_link/) | 17.0.1.0.0 |  | Adds a button on product forms to access Journal Items
[purchase_stock_picking_return_invoicing](purchase_stock_picking_return_invoicing/) | 17.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![MiquelRForgeFlow](https://github.com/MiquelRForgeFlow.png?size=30px)](https://github.com/MiquelRForgeFlow) | Add an option to refund returned pickings
[sale_invoicing_date_selection](sale_invoicing_date_selection/) | 17.0.1.0.1 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Set date invoice when you create invoices
[sale_order_invoicing_grouping_criteria](sale_order_invoicing_grouping_criteria/) | 17.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Sales order invoicing grouping criteria
[sale_order_invoicing_qty_percentage](sale_order_invoicing_qty_percentage/) | 17.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | Sales order invoicing by percentage of the quantity
[sale_timesheet_invoice_description](sale_timesheet_invoice_description/) | 17.0.1.0.1 |  | Add timesheet details in invoice line
[stock_picking_invoicing](stock_picking_invoicing/) | 17.0.1.0.0 |  | Stock Picking Invoicing

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
