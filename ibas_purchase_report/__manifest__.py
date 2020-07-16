# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase Order Summary  Report
#    module: ibas_purchase_report
#
##############################################################################
{
    'name': 'ibas_purchase_report',
    'summary': 'Puchase Order Summary Report',
    'description': """
    Puchase Order Summary Report Report
""",
    'author': 'Joven Lawrence Gersaniba',
    'category': 'Uncategorized',
    'version': '0.1',
    # 'website' : '',
    'depends': ['purchase'],
    # 'images': ['static/description/banner.jpg'],
    'data': [
        # 'wizard/print_purchase_order_summary_view.xml',
        'wizard/purchase_xls_wiz.xml',
        # 'report/order_summary_report_view.xml',
        # 'report/report_menu.xml',
    ],
}
