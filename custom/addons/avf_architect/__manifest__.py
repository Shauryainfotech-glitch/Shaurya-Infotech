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
        'mail',
        'calendar',
        'hr_timesheet',
        'portal',
        'web',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/project_stages.xml',
        'data/project_stage_migration.xml',
        'views/menus.xml',
        'views/project_views.xml',
        'views/team_collaboration_views.xml',
        'views/drawing_management_views.xml',
        'views/survey_management_views.xml',
        'views/ai_assistant_views.xml',
        'views/project_stages_views.xml',
        'views/client_portal_views.xml',
        'views/document_management_views.xml',
        'views/financial_tracking_views.xml',
        'views/dpr_management_views.xml',
        'reports/dpr_report.xml',
        'reports/compliance_report.xml',
        'reports/estimation_report.xml',
        'views/compliance_views.xml',
        'views/rate_schedule_views.xml',
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