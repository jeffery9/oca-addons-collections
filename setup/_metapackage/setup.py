import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-account-financial-tools",
    description="Meta package for oca-account-financial-tools Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_account_tag_code>=16.0dev,<16.1dev',
        'odoo-addon-account_asset_batch_compute>=16.0dev,<16.1dev',
        'odoo-addon-account_asset_management>=16.0dev,<16.1dev',
        'odoo-addon-account_cash_deposit>=16.0dev,<16.1dev',
        'odoo-addon-account_chart_update>=16.0dev,<16.1dev',
        'odoo-addon-account_chart_update_l10n_eu_oss_oca>=16.0dev,<16.1dev',
        'odoo-addon-account_fiscal_month>=16.0dev,<16.1dev',
        'odoo-addon-account_fiscal_position_vat_check>=16.0dev,<16.1dev',
        'odoo-addon-account_fiscal_year>=16.0dev,<16.1dev',
        'odoo-addon-account_fiscal_year_auto_create>=16.0dev,<16.1dev',
        'odoo-addon-account_invoice_constraint_chronology>=16.0dev,<16.1dev',
        'odoo-addon-account_journal_general_sequence>=16.0dev,<16.1dev',
        'odoo-addon-account_journal_lock_date>=16.0dev,<16.1dev',
        'odoo-addon-account_journal_restrict_mode>=16.0dev,<16.1dev',
        'odoo-addon-account_loan>=16.0dev,<16.1dev',
        'odoo-addon-account_lock_date_update>=16.0dev,<16.1dev',
        'odoo-addon-account_move_budget>=16.0dev,<16.1dev',
        'odoo-addon-account_move_fiscal_month>=16.0dev,<16.1dev',
        'odoo-addon-account_move_fiscal_year>=16.0dev,<16.1dev',
        'odoo-addon-account_move_line_check_number>=16.0dev,<16.1dev',
        'odoo-addon-account_move_line_purchase_info>=16.0dev,<16.1dev',
        'odoo-addon-account_move_line_sale_info>=16.0dev,<16.1dev',
        'odoo-addon-account_move_line_tax_editable>=16.0dev,<16.1dev',
        'odoo-addon-account_move_name_sequence>=16.0dev,<16.1dev',
        'odoo-addon-account_move_post_date_user>=16.0dev,<16.1dev',
        'odoo-addon-account_move_print>=16.0dev,<16.1dev',
        'odoo-addon-account_move_template>=16.0dev,<16.1dev',
        'odoo-addon-account_netting>=16.0dev,<16.1dev',
        'odoo-addon-account_partner_required>=16.0dev,<16.1dev',
        'odoo-addon-account_spread_cost_revenue>=16.0dev,<16.1dev',
        'odoo-addon-account_template_active>=16.0dev,<16.1dev',
        'odoo-addon-account_usability>=16.0dev,<16.1dev',
        'odoo-addon-base_vat_optional_vies>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
