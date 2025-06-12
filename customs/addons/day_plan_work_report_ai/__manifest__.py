{
    "name": "Day Plan & Work Report with AI Analysis",
    "version": "18.0.1.0.1",
    "summary": "Daily planning, work reporting, and AI productivity insights",
    "category": "Productivity",
    "author": "Viresh Dhasal / AVGC",
    "website": "https://www.avgc.com",
    "license": "LGPL-3",
    "depends": ["base", "mail", "hr", "web"],
    "data": [
        # Data files
        "data/sequence.xml",
        "data/ai_analysis_data.xml",

        # Security
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",

        # Views
        "views/day_plan_views.xml",
        "views/day_plan_task_views.xml",
        "views/work_report_views.xml",
        "views/ai_analysis_views.xml",
        "views/dashboard_views.xml",
        "views/menu_views.xml",

        # Wizards
        "wizards/report_generator_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "day_plan_work_report_ai/static/src/js/dashboard.js",
            "day_plan_work_report_ai/static/src/xml/templates.xml",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
    "description": """
    Day Plan & Work Report with AI Analysis
    ======================================

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
    """
}