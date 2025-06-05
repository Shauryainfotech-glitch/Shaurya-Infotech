
# -*- coding: utf-8 -*-
{
    'name': 'AVF Creative Architect ERP',
    'version': '18.0.1.0.0',
    'category': 'Project Management',
    'summary': 'Complete AI-Enabled Architectural ERP for Government Consultancy Projects',
    'description': """
        Advanced Architectural ERP Module for AVF Creative Firm
        =====================================================
        
        Core Features:
        * Government Project Management
        * AI-Powered Design Assistance
        * Blueprint & Drawing Management
        * Regulatory Compliance Tracking
        * Advanced Financial Management
        * Team Collaboration Tools
        * Client Portal Integration
        * Real-time Progress Tracking
        * Document Management System
        * Automated Reporting
        
        DPR & Survey Management:
        * DPR (Detailed Project Report) Creation
        * SSR/DSR Survey Report Integration
        * State/Department Specific Guidelines
        * AI-Enhanced DPR Generation
        * Survey Data Analysis & Recommendations
        * Compliance Checklist Automation
        
        FCA & Ecotourism Compliance:
        * Forest Conservation Act (FCA) Compliance
        * PARIVESH Portal Integration
        * Biodiversity Impact Assessment
        * Ecotourism Design Optimization
        * Compensatory Afforestation Planning
        * Community Engagement Strategies
        * Carbon Footprint Analysis
        * Wildlife-Friendly Design Features
        
        Rate Schedule & Estimation:
        * DSR (District Schedule of Rates)
        * SSR (State Schedule of Rates)
        * Government-Compliant Estimates
        * Rate Analysis & Validation
        * Market Rate Comparison
        * Approval Workflow Management
        * Audit-Ready Documentation
        * GST & Statutory Compliance
    """,
    'author': 'AVF Creative Solutions',
    'website': 'https://avfcreative.com',
    'depends': [
        'base',
        'project',
        'hr',
        'account',
        'sale',
        'purchase',
        'stock',
        'mail',
        'calendar',
        'hr_timesheet',
        'document',
        'website',
        'portal',
        'website_sale',  # Added for Odoo 18 ecommerce features
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/project_stages.xml',
        'data/compliance_types.xml',
        'data/document_categories.xml',
        'data/financial_categories.xml',
        'data/rate_schedule_data.xml',
        'views/menus.xml',
        'views/drawing_management_views.xml',
        'views/survey_management_views.xml',
        'views/ai_assistant_views.xml',
        'views/project_stages_views.xml',
        'views/team_collaboration_views.xml',
        'views/client_portal_views.xml',
        'views/document_management_views.xml',
        'views/financial_tracking_views.xml',
        'views/project_views.xml',
        'views/dpr_views.xml',
        'views/compliance_views.xml',
        'views/rate_schedule_views.xml',
        'views/drawing_views.xml',
        'views/survey_views.xml',
        'views/dashboard_views.xml',
        'views/portal_templates.xml',
        'reports/dpr_report.xml',
        'reports/compliance_report.xml',
        'reports/estimation_report.xml',
        'wizard/ai_assistant_views.xml',
        'wizard/dpr_generator_views.xml',
        'wizard/compliance_checker_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            ('include', 'web._assets_helpers'),  # Include Odoo 18 helpers
            'avf_architect/static/src/scss/architect_style.scss',  # Updated to SCSS
            'avf_architect/static/src/components/**/*.js',  # New component structure
            'avf_architect/static/src/components/**/*.xml',  # Component templates
            'avf_architect/static/src/components/**/*.scss',  # Component styles
        ],
        'web.assets_frontend': [
            'avf_architect/static/src/scss/portal_style.scss',
            'avf_architect/static/src/js/portal_dashboard.js',
            'avf_architect/static/src/components/portal/**/*.js',
            'avf_architect/static/src/components/portal/**/*.xml',
        ],
    },
    'demo': [
        'demo/demo_projects.xml',
        'demo/demo_compliance.xml',
        'demo/demo_rates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
