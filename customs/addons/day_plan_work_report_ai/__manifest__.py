{
    "name": "Day Plan & Work Report with AI Analysis",
    "version": "18.0.1.0.1",
    "summary": "Daily planning, work reporting, and AI productivity insights",
    "category": "Productivity",
    "author": "Viresh Dhasal / AVGC",
    "website": "https://www.avgc.com",
    "license": "LGPL-3",
    "depends": ["base", "mail", "hr", "board", "web"],
    "data": [
        # Security
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",

        # Data
        "data/sequence.xml",
        "data/ai_analysis_data.xml",

        # Views
        "views/day_plan_views.xml",
        "views/day_plan_task_views.xml",
        "views/work_report_views.xml",
        "views/ai_analysis_views.xml",
        "views/dashboard_views.xml",
        "views/dashboard_templates.xml",
        "views/dashboard_actions.xml",
        "views/dashboard_menu.xml",
        "views/wizard_views.xml",

        # Reports
        "report/dashboard_report.xml",
        "report/dashboard_report_templates.xml"
    ],
    "assets": {
        "web.assets_backend": [
            # Chart.js library
            "https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js",

            # Dashboard JavaScript
            "day_plan_work_report_ai/static/src/js/dashboard.js",

            # Dashboard CSS
            "day_plan_work_report_ai/static/src/css/dashboard.css",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
    "auto_install": False,
    "description": """
Day Plan & Work Report with AI Analysis
======================================

A comprehensive productivity management system with AI-powered insights.

Key Features:
-------------
* Daily planning with task management
* End-of-day work reporting
* AI-powered productivity analysis
* Interactive dashboard with charts
* Task tracking and completion metrics
* Productivity scoring and analytics

Technical Features:
------------------
* Chart.js integration for data visualization
* OWL components for modern UI
* Responsive dashboard design
* Real-time data updates
* PDF report generation
""",
}