# -*- coding: utf-8 -*-
{
    'name': "Stock Account Disable Autopost",

    'summary': """
        Option to not automatically post journal entries generated from stock moves""",

    'description': """
        Option to not automatically post journal entries generated from stock moves
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '11.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','stock_account'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}