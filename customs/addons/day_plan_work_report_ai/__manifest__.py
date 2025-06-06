# -*- coding: utf-8 -*-
{
    'name': 'Day Plan & Work Report with AI Analysis',
    'version': '18.0.1.0.1',
    'summary': 'Daily planning, work reporting, and AI productivity insights',
    'category': 'Productivity',
    'author': 'Viresh Dashal / AVGC',
    'website': 'https://www.avgc.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'hr',
        'board',
        'web',
        'resource'
    ],
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',

        # Data
        'data/sequence.xml',
        'data/ai_analysis_data.xml',

        # Views
        'views/day_plan_views.xml',
        'views/day_plan_task_views.xml',
        'views/work_report_views.xml',
        'views/ai_analysis_views.xml',
        'views/dashboard_templates.xml',
        'views/dashboard_views.xml',
        'views/dynamic_dashboard_views.xml',
        'views/dashboard_actions.xml',
        'views/dashboard_menu.xml',
        'views/wizard_views.xml',
        'views/enhanced_dashboard_views.xml',

        # Reports
        'report/dashboard_report.xml',
        'report/dashboard_report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Include legacy web client JS files to ensure 'web.AbstractView' is available
            'web/static/src/js/views/abstract_view.js',
            'web/static/src/js/views/list/list_view.js',
            'web/static/src/js/views/form/form_view.js',
            'web/static/src/js/views/kanban/kanban_view.js',
            'web/static/src/js/views/search/search_view.js',
            'web/static/src/js/views/control_panel.js',
            'web/static/src/js/views/basic/basic_view.js',
            # Custom addon JS files
            'day_plan_work_report_ai/static/src/js/dashboard.js',
            'day_plan_work_report_ai/static/src/views/day_plan_calendar/day_plan_calendar.js',
            'day_plan_work_report_ai/static/src/views/day_plan_calendar/day_plan_calendar.xml',
            'day_plan_work_report_ai/static/src/dashboard_client_action.js',
            'day_plan_work_report_ai/static/src/new_dashboard_client_action.js',
        ],
        'web.assets_frontend': [
            # Add frontend assets if needed
        ]
    },
    # 'external_dependencies': {
    #     'python': ['requests', 'openai'],  # Add AI library dependencies when needed
    # },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'description': """
Day Plan & Work Report with AI Analysis
========================================

A comprehensive productivity management system with AI-powered insights.

Key Features:
-------------
* Daily planning with task management
* End-of-day work reporting
* AI-powered productivity analysis
* Multiple AI provider support (OpenAI, Anthropic, Google)
* Comprehensive analysis types (daily, weekly, monthly)
* Intelligent prompt engineering
* Actionable metrics generation

This module helps teams and individuals track their daily activities,
analyze productivity patterns, and receive AI-generated insights to
improve work efficiency and goal achievement.
    """,
}