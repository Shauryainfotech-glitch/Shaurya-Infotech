{
    'name': 'Manufacturing Estimation & Costing',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Advanced Manufacturing Estimation, Costing & Quote Management',
    'description': """
    Manufacturing Estimation & Costing Module
    =========================================
    
    This module provides comprehensive manufacturing estimation and costing capabilities:
    
    Key Features:
    * Detailed product manufacturing estimation
    * Material cost breakdown and analysis
    * Operation and labor cost calculation
    * Multi-level approval workflow
    * Version control for estimations
    * Integration with Sales, Manufacturing & Inventory
    * Advanced cost markup and pricing strategies
    * Real-time manufacturing cost tracking
    * Comprehensive reporting and analytics
    
    Perfect for manufacturing companies that need precise cost estimation and quote management.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'sale ',
        'mrp',
        'stock',
        'account',
        'hr',
        'mail',
        'portal',
    ],
    'data': [
        # Security
        'security/estimation_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/estimation_sequence.xml',
        'data/estimation_data.xml',
        
        # Views
        'views/estimation_views.xml',
        'views/estimation_line_views.xml',
        'views/estimation_cost_views.xml',
        'views/estimation_version_views.xml',
        'views/mrp_costing_views.xml',
        'views/estimation_menus.xml',
        
        # Reports
        'reports/estimation_reports.xml',   
        'reports/estimation_report_views.xml',
        'reports/estimation_templates.xml',
        
        # Wizards
        'wizard/estimation_wizard_views.xml',
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
        'python': ['xlsxwriter'],
    },
}
