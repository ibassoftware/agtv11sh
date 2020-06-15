# -*- coding: utf-8 -*-
{
    'name': "ibas_agt",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly

    'depends': ['base','account','stock','sale','stock_landed_costs', 'report_xlsx', 'purchase', 'sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/stock_wizard.xml',
        'views/sale_order_line.xml',
        'views/account_invoice.xml',
        'views/landed_cost.xml',
        'views/stock_age.xml',
        'views/purchase_order.xml',
        'report/report_sales_agt.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}