# -*- coding: utf-8 -*-
{
    'name': "AGT Website",

    'summary': """
        AGT Website""",

    'description': """AGT Website""",

    'author': "IBAS",
    'website': "https://ibasuite.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Theme',
    'version': '11.0.1',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'data/homepage_data.xml',
        'views/assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}