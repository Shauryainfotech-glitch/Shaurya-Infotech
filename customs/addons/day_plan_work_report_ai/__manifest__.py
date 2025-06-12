{
    'name': 'Day Plan Work Report AI',
    'version': '16.0.1.0.0',
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
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'web',
        'mail',
        'calendar',
        'hr',
        'project',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/day_plan_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',

        # Actions
        'data/dashboard_actions.xml',

        # Reports
        'reports/dashboard_reports.xml',

        # Data
        'data/day_plan_data.xml',
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

            # XML Templates
            'day_plan_work_report_ai/static/src/guaranteed_chart_dashboard.xml',
            'day_plan_work_report_ai/static/src/day_plan_templates.xml',
            'day_plan_work_report_ai/static/src/client_action_templates.xml',

            # CSS Styles
            'day_plan_work_report_ai/static/src/css/dashboard_styles.css',
        ],
        'web.assets_common': [
            # Common templates that need to be available across all views
            'day_plan_work_report_ai/static/src/common_templates.xml',
        ],
    },
    'demo': [
        'demo/day_plan_demo.xml',
    ],
    'qweb': [
        # Legacy qweb templates (if any)
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'post_init_hook': '_post_init_hook',
    'uninstall_hook': '_uninstall_hook',
}