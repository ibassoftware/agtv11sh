# -*- coding: utf-8 -*-
{
    'name': "Account Expense Disable Autopost",

    'summary': """
        Option to not automatically post journal entries generated from expense report""",

    'description': """
        Option to not automatically post journal entries generated from expense report
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '11.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'views/hr_expense_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}