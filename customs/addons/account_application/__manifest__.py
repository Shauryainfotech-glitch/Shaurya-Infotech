# __manifest__.py for the main module

{
    'name': 'OM Account Accountant',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Enterprise-grade accounting features for Odoo 18',
    'description': """
        This module provides advanced accounting features for Odoo 18 including:
        - Financial Reports
        - Asset Management
        - Budget Management
        - Bank Statement Import
        - Customer Follow-ups
        - Recurring Payments
    """,
    'author': 'YourCompany',
    'website': 'https://yourcompany.com',
    'depends': [
        'account',  # Odoo's core accounting module
        'account_payment',  # Payment functionality
        'mail',  # Email integration for follow-ups
        'web',  # Web module for views
    ],
    'data': [
        # Submodule data files
        'financial_reports/views/financial_report_views.xml',
        'financial_reports/report/financial_reports.xml',
        'financial_reports/wizard/financial_report_wizard.xml',

        'asset_management/views/account_asset_views.xml',
        'asset_management/data/asset_data.xml',

        'budget_management/views/account_budget_views.xml',
        'budget_management/data/budget_data.xml',

        'bank_statement_import/data/bank_statement_data.xml',

        'customer_followups/views/account_followup_views.xml',
        'customer_followups/data/followup_data.xml',

        'recurring_payments/views/recurring_payment_views.xml',
        'recurring_payments/data/recurring_payment_data.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
