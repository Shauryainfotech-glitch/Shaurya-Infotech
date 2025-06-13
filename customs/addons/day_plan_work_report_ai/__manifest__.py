{
    'name': 'Day Plan Work Report AI',
    'version': '18.0.1.0.0',  # ALTERNATIVE: For Odoo 18 format
    'category': 'Productivity',
    'summary': 'AI-powered day planning and work reporting with advanced dashboard',
    'description': """
        Day Plan Work Report AI
        =======================

        This module provides:
        * AI-powered day planning functionality
        * Advanced dashboard with multiple chart types
        * Real-time productivity analytics
        * Task management and reporting
        * Calendar integration
        * Performance metrics tracking

        Key Features:
        -------------
        * Daily planning with task management
        * End-of-day work reporting
        * AI-powered productivity analysis
        * Multiple AI provider support (OpenAI, Anthropic, Google)
        * Comprehensive analysis types (daily, weekly, monthly)
        * Intelligent prompt engineering
        * Actionable metrics generation

        AI Analysis Integration:
        -----------------------
        * Multiple AI Provider Support: Flexible integration with OpenAI (GPT-4),
          Anthropic (Claude), and Google (Gemini) APIs, with a mock provider for testing.
        * Comprehensive Analysis Types: Supports daily plan completion analysis,
          work report insights, weekly summaries, monthly reviews, and productivity trend detection.
        * Intelligent Prompt Engineering: Carefully crafted prompts extract meaningful
          insights from AI providers based on structured work data.
        * Actionable Metrics Generation: Produces productivity scores, efficiency ratings,
          wellbeing assessments, and personalized improvement suggestions.
    """,
    'author': 'Viresh Dhasal / AVGC',
    'website': 'https://www.avgc.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'calendar',
        'hr',
        'project',
        'board',
        'resource',
    ],
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',

        # Data
        'data/sequence.xml',
        'data/ai_analysis_data.xml',
        'data/day_plan_data.xml',

        # Views
        'views/day_plan_views.xml',
        'views/day_plan_task_views.xml',
        'views/work_report_views.xml',
        'views/ai_analysis_views.xml',
        'views/dashboard_templates.xml',
        'views/wizard_views.xml',
        'views/plan_creation_views.xml',
        'views/dashboard_views.xml',
        'views/dynamic_dashboard_views.xml',
        'views/enhanced_dashboard_views.xml',

        # Actions and Menus
        'views/dashboard_actions.xml',
        'views/dashboard_menu.xml',

        # Reports
        'report/dashboard_report.xml',
        'report/dashboard_report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # JavaScript Files
            'day_plan_work_report_ai/static/src/guaranteed_chart_dashboard.js',
            'day_plan_work_report_ai/static/src/new_dashboard_client_action.js',
            'day_plan_work_report_ai/static/src/components/dashboard_chart.js',
            'day_plan_work_report_ai/static/src/components/dashboard/productivity_dashboard.js',
            'day_plan_work_report_ai/static/src/components/dashboard/productivity_dashboard_action.js',

            # Calendar Components
            'day_plan_work_report_ai/static/src/views/day_plan_calendar/day_plan_calendar_view.js',
            'day_plan_work_report_ai/static/src/views/day_plan_calendar/day_plan_calendar_controller.js',
            'day_plan_work_report_ai/static/src/views/day_plan_calendar/day_plan_calendar_renderer.js',
            'day_plan_work_report_ai/static/src/views/day_plan_calendar/day_plan_calendar_model.js',

            # CSS Styles
            'day_plan_work_report_ai/static/src/css/dashboard_styles.css',
        ],
        'web.assets_common': [
            # XML Templates
            'day_plan_work_report_ai/static/src/guaranteed_chart_dashboard.xml',
            'day_plan_work_report_ai/static/src/day_plan_templates.xml',
            'day_plan_work_report_ai/static/src/client_action_templates.xml',
        ],
    },
    'demo': [
        'demo/day_plan_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': '_uninstall_hook',
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
}