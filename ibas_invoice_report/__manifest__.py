# -*- coding: utf-8 -*-
##############################################################################
#
#    Invoice Summary Report
#    module: ibas_invoice_report
#
##############################################################################
{
    'name': 'ibas_invoice_report',
    'summary': 'Invoice Summary Report',
    'description': """
    Invoice Report
""",
    'author': 'Joven Lawrence Gersaniba',
    'category': 'Uncategorized',
    'version': '0.1',
    # 'website' : '',
    'depends': ['account_invoicing'],
    # 'images': ['static/description/banner.jpg'],
    'data': [
        # 'wizard/print_purchase_order_summary_view.xml',
        'wizard/invoice_xls_wiz.xml',
        # 'report/order_summary_report_view.xml',
        # 'report/report_menu.xml',
    ],
}
