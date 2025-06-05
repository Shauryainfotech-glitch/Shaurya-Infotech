{
    'name': 'AI-Powered Purchase Management',
    'version': '18.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Ultra-Advanced AI-Powered Purchase Module with Vendor Intelligence, Risk Assessment, and Automated Decision Support',
    'description': """
        AI-Powered Purchase Management Module
        =====================================
        
        Ultra-advanced purchase management with:
        * Multi-provider AI integration (Claude, OpenAI, Gemini)
        * Intelligent vendor suggestion engine with detailed scoring
        * AI-powered risk assessment and compliance checking
        * Automated vendor creation pipeline with data enrichment
        * Interactive approval workflows with AI decision support
        * Multi-modal document analysis and contract review
        * Continuous learning and feedback loops
        * Advanced security, caching, and audit trails
        * Async job processing with priority queues
        * Real-time vendor scoring and performance tracking
    """,
    'author': 'OmniHR AI Platform',
    'website': 'https://omnihr.ai',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'purchase',
        'mail',
        'web',
        'queue_job',  # For async processing
        'document',   # For file handling
        'portal',     # For vendor portal access
    ],
    'external_dependencies': {
        'python': [
            'requests',
            'openai',
            'anthropic',
            'google-generativeai',
            'pandas',
            'numpy',
            'scikit-learn',
            'celery',
            'redis',
            'cryptography',
            'pillow',
            'PyPDF2',
            'python-magic',
        ]
    },
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequences.xml',
        'data/ai_settings_data.xml',
        'data/cron_jobs.xml',
        'views/ai_service_views.xml',
        'views/vendor_creation_views.xml',
        'views/vendor_suggestion_views.xml',
        'views/vendor_enrichment_views.xml',
        'views/ai_settings_views.xml',
        'views/risk_assessment_views.xml',
        'views/ai_analytics_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'purchase_ai/static/src/css/purchase_ai.css',
            'purchase_ai/static/src/js/purchase_ai.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
} 