{
    'name': 'AVGC Tender Management',
    'version': '17.0.1.0.0',
    'category': 'Procurement',
    'summary': 'Comprehensive Enterprise Tender Management Platform',
    'description': """
        AVGC TENDER PRO - Enterprise-grade tender management system
        
        Features:
        * Complete tender lifecycle management
        * Multi-AI integration for document analysis
        * GeM Bid 14-stage lifecycle management
        * Advanced vendor management
        * Document management with version control
        * RBAC system with granular permissions
        * Automated workflows and approvals
        * Real-time analytics and reporting
        * Blockchain-enhanced security
        * External system integrations
    """,
    'author': 'AVGC Solutions',
    'website': 'https://avgcsolutions.com',
    'depends': [
        'base',
        'mail',
        'document',
        'project',
        'account',
        'hr',
        'website',
        'portal',
        'web',
    ],
    'data': [
        'security/tender_security.xml',
        'security/ir.model.access.csv',
        'data/tender_categories.xml',
        'data/tender_stages.xml',
        'data/gem_bid_stages.xml',
        'data/task_templates.xml',
        'data/firm_data.xml',
        'views/tender_views.xml',
        'views/vendor_views.xml',
        'views/gem_bid_views.xml',
        'views/document_views.xml',
        'views/analytics_views.xml',
        'views/ocr_views.xml',
        'views/finance_views.xml',
        'views/task_views.xml',
        'views/firm_views.xml',
        'views/settings_views.xml',
        'views/menu_views.xml',
        'wizards/ai_analysis_wizard.xml',
        'wizards/tender_processing_wizard.xml',
        'reports/tender_reports.xml',
    ],
    'demo': [
        'demo/tender_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'avgc_tender_management/static/src/js/tender_dashboard.js',
            'avgc_tender_management/static/src/css/tender_style.css',
        ],
        'web.assets_frontend': [
            'avgc_tender_management/static/src/js/portal_tender.js',
        ],
    },
    'demo': [
        'demo/tender_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}