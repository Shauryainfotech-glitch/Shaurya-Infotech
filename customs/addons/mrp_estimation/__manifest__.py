{
    'name': 'Manufacturing Estimation & Costing',
    'version': '18.0.1.1.0',
    'category': 'Manufacturing',
    'summary': 'Advanced Manufacturing Estimation, Costing & Quote Management',
    'description': """
    Manufacturing Estimation & Costing Module
    =========================================

    This module provides comprehensive manufacturing estimation and costing capabilities for Odoo 18:

    Key Features:
    * Detailed product manufacturing estimation with BOM integration
    * Material cost breakdown and analysis with supplier management
    * Operation and labor cost calculation with work center integration
    * Multi-level approval workflow with automated notifications
    * Version control for estimations with change tracking
    * Integration with Sales, Manufacturing & Inventory modules
    * Advanced cost markup and pricing strategies
    * Real-time manufacturing cost tracking and variance analysis
    * Comprehensive reporting and analytics dashboard
    * Customer portal access for estimation viewing and download
    * API endpoints for external system integration
    * Configurable settings and default values
    * Tag-based categorization and priority management
    * Automated expiration tracking and notifications

    Perfect for manufacturing companies that need precise cost estimation and efficient quote management.

    New in v1.1.0:
    * Enhanced Odoo 18 compatibility with modern view syntax
    * Improved kanban views for better visual management
    * Enhanced API with additional endpoints
    * Better performance optimization
    * Improved security with granular access rights
    * Enhanced portal experience
    * Additional configuration options
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'sale',
        'mrp',
        'stock',
        'account',
        'hr',
        'mail',
        'portal',
        'web',
    ],
    'data': [
        # Security
        'security/estimation_security.xml',
        'security/portal_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/estimation_sequence.xml',
        'data/costing_sequence.xml',

        # Views
        'views/estimation_menus.xml',
        'views/mrp_costing_views.xml',
        'views/res_config_settings_views.xml',
        'views/portal_templates.xml',

        # Reports
        'reports/report_estimation.xml',

        # Wizards
        'wizard/estimation_wizard_views.xml',

        # Data that depends on views/reports
        'data/estimation_data.xml',
    ],
    'demo': [
        'demo/estimation_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_estimation/static/src/css/estimation.css',
            'mrp_estimation/static/src/js/estimation_widget.js',
        ],
        'web.assets_frontend': [
            'mrp_estimation/static/src/css/portal.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [],
    },
    'price': 299.99,
    'currency': 'EUR',
    'live_test_url': 'https://demo.yourcompany.com',
    'support': 'support@yourcompany.com',
    'images': [
        'static/description/banner.png',
        'static/description/screenshot1.png',
        'static/description/screenshot2.png',
    ],
    'maintainers': ['your_github_username'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}