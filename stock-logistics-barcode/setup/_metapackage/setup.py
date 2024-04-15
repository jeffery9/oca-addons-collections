import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-logistics-barcode",
    description="Meta package for oca-stock-logistics-barcode Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-barcodes_generator_abstract>=16.0dev,<16.1dev',
        'odoo-addon-barcodes_generator_location>=16.0dev,<16.1dev',
        'odoo-addon-barcodes_generator_package>=16.0dev,<16.1dev',
        'odoo-addon-barcodes_generator_product>=16.0dev,<16.1dev',
        'odoo-addon-product_barcode_constraint_per_company>=16.0dev,<16.1dev',
        'odoo-addon-product_multi_barcode>=16.0dev,<16.1dev',
        'odoo-addon-product_multi_barcode_constraint_per_company>=16.0dev,<16.1dev',
        'odoo-addon-product_multi_barcode_stock_menu>=16.0dev,<16.1dev',
        'odoo-addon-product_packaging_multi_barcode>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
