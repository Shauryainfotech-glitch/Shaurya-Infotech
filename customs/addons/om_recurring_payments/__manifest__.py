{
    'name': 'Odoo 18 Recurring Payment',
    'author': 'Odoo Mates',
    'category': 'Accounting',
    'version': '1.0.0',
    'description': """Odoo 18 Recurring Payment, Recurring Payment In Odoo, Odoo 18 Accounting""",
    'summary': 'Use recurring payments to handle periodically repeated payments',
    'sequence': 11,
    'website': 'https://www.odoomates.tech',
    'depends': ['account'],
    'license': 'LGPL-3',
    'data': [
        'data/sequence.xml',                # Sequence configuration for recurring payments
        'data/recurring_cron.xml',          # Cron jobs to handle the recurring payments
        'security/ir.model.access.csv',     # Access rights for the models
        'views/recurring_template_view.xml',# Views for recurring templates
        'views/recurring_payment_view.xml', # Views for recurring payments
        'views/recurring_menu.xml',         # Menu definition for the app
    ],
    'images': ['static/description/banner.png'],  # App banner
    'installable': True,                        # Ensure the module is installable
    'application': True,                        # This is an application, should show in Apps menu
    'auto_install': False,                      # Only install when the dependencies are met
}
