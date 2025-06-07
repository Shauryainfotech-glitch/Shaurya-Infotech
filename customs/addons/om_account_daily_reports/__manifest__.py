# -*- coding: utf-8 -*-
{
    'name': 'Daily Reports',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Daily Financial Reports - Bank Book, Cash Book, Day Book',
    'description': """
        This module provides daily financial reports including:
        - Bank Book
        - Cash Book  
        - Day Book
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['account'],
    'data': [
        # Security files
        'security/ir.model.access.csv',

        # Wizard views FIRST - These define the actions
        'wizard/bankbook.xml',
        'wizard/cashbook.xml',
        'wizard/daybook.xml',

        # Menu file AFTER wizards - This uses the actions
        'views/om_daily_reports.xml',

        # Report templates
        'report/report_bankbook.xml',
        'report/report_cashbook.xml',
        'report/report_daybook.xml',
        'report/reports.xml',

    ],
    'application': True,  # This is crucial - makes it appear as main app
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'icon': '/om_account_daily_reports/static/description/icon.png',  # Optional app icon
}