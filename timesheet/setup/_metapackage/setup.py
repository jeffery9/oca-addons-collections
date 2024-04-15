import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-timesheet",
    description="Meta package for oca-timesheet Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-crm_timesheet>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_cost_history>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_begin_end>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_employee_analytic_tag>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_name_customer>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_report>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_sheet>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_sheet_autodraft>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_sheet_policy_project_manager>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_task_domain>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_task_required>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_task_stage>=16.0dev,<16.1dev',
        'odoo-addon-hr_timesheet_time_type>=16.0dev,<16.1dev',
        'odoo-addon-project_task_analytic_propagation>=16.0dev,<16.1dev',
        'odoo-addon-project_task_stage_allow_timesheet>=16.0dev,<16.1dev',
        'odoo-addon-sale_timesheet_line_exclude>=16.0dev,<16.1dev',
        'odoo-addon-sale_timesheet_rounded>=16.0dev,<16.1dev',
        'odoo-addon-sale_timesheet_task_exclude>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
