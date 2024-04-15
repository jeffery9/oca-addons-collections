import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-server-ux",
    description="Meta package for oca-server-ux Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-announcement>=16.0dev,<16.1dev',
        'odoo-addon-barcode_action>=16.0dev,<16.1dev',
        'odoo-addon-base_archive_security>=16.0dev,<16.1dev',
        'odoo-addon-base_binary_url_import>=16.0dev,<16.1dev',
        'odoo-addon-base_cancel_confirm>=16.0dev,<16.1dev',
        'odoo-addon-base_custom_filter>=16.0dev,<16.1dev',
        'odoo-addon-base_export_manager>=16.0dev,<16.1dev',
        'odoo-addon-base_import_security_group>=16.0dev,<16.1dev',
        'odoo-addon-base_menu_visibility_restriction>=16.0dev,<16.1dev',
        'odoo-addon-base_optional_quick_create>=16.0dev,<16.1dev',
        'odoo-addon-base_revision>=16.0dev,<16.1dev',
        'odoo-addon-base_search_custom_field_filter>=16.0dev,<16.1dev',
        'odoo-addon-base_substate>=16.0dev,<16.1dev',
        'odoo-addon-base_technical_features>=16.0dev,<16.1dev',
        'odoo-addon-base_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-base_tier_validation_definition_server_action>=16.0dev,<16.1dev',
        'odoo-addon-base_tier_validation_formula>=16.0dev,<16.1dev',
        'odoo-addon-base_tier_validation_forward>=16.0dev,<16.1dev',
        'odoo-addon-base_tier_validation_server_action>=16.0dev,<16.1dev',
        'odoo-addon-base_tier_validation_waiting>=16.0dev,<16.1dev',
        'odoo-addon-base_user_locale>=16.0dev,<16.1dev',
        'odoo-addon-date_range>=16.0dev,<16.1dev',
        'odoo-addon-date_range_account>=16.0dev,<16.1dev',
        'odoo-addon-filter_multi_user>=16.0dev,<16.1dev',
        'odoo-addon-multi_step_wizard>=16.0dev,<16.1dev',
        'odoo-addon-sequence_reset_period>=16.0dev,<16.1dev',
        'odoo-addon-server_action_mass_edit>=16.0dev,<16.1dev',
        'odoo-addon-template_content_swapper>=16.0dev,<16.1dev',
        'odoo-addon-test_base_binary_url_import>=16.0dev,<16.1dev',
        'odoo-addon-user_all_groups>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
