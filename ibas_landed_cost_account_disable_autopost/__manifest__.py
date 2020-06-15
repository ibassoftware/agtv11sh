# -*- coding: utf-8 -*-
{
    'name': "Landed Cost Account Disable Autopost",

    'summary': """
        Option to not automatically post journal entries generated from landed cost""",

    'description': """
        Option to not automatically post journal entries generated from landed cost
    """,

    'author': "IBAS",
    'website': "https://ibasuite.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '11.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','stock_landed_costs'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'views/stock_landed_cost_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
# # -*- RCS -*-