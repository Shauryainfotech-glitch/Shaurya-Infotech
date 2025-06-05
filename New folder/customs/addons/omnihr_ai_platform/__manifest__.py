{
    'name': 'OmniHR AI Intelligence Platform',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Advanced Multi-AI HR Management System with OpenAI, Claude & Gemini Integration',
    'description': '''
    Revolutionary HR Management System powered by multiple AI providers:
    • Multi-AI Provider Integration (OpenAI, Claude, Gemini)
    • Intelligent Recruitment & Candidate Assessment
    • Predictive Performance Analytics
    • Real-time Employee Sentiment Analysis
    • Advanced HR Chatbot with Consensus Intelligence
    • Automated HR Workflows & Decision Making
    ''',
    'author': 'OmniHR Development Team',
    'website': 'https://omnihr.ai',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'hr_recruitment',
        'hr_holidays',
        'hr_attendance',
        'mail',
        'web',
        'portal',
    ],
    'external_dependencies': {
        'python': [
            'requests',
        ]
    },
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/ai_provider_data.xml',
        'data/ai_config_data.xml',
        
        # Views
        'views/menu_views.xml',
        'views/hr_ai_config_views.xml',
        'views/hr_multi_ai_provider_views.xml',
        'views/hr_employee_intelligence_views.xml',
        'views/hr_recruitment_ai_views.xml',
        'views/hr_performance_analytics_views.xml',
        'views/hr_ai_chat_views.xml',
        'views/hr_ai_dashboard_views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'omnihr_ai_platform/static/src/css/ai_dashboard.css',
            'omnihr_ai_platform/static/src/css/ai_chat.css',
            'omnihr_ai_platform/static/src/css/ai_interface.css',
            'omnihr_ai_platform/static/src/js/ai_dashboard.js',
            'omnihr_ai_platform/static/src/js/ai_chat.js',
            'omnihr_ai_platform/static/src/js/recruitment_ai.js',
            'omnihr_ai_platform/static/src/js/analytics_charts.js',
        ],
        'web.assets_frontend': [
            'omnihr_ai_platform/static/src/css/ai_interface.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'price': 999.99,
    'currency': 'USD',
    'support': 'support@omnihr.ai',
} 