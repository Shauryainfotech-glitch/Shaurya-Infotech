# -*- coding: utf-8 -*-
{
    'name': 'AI LLM Integration',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Integrate AI Large Language Models across all Odoo modules',
    'description': """
AI LLM Integration Module
=========================

This module provides comprehensive AI integration capabilities:
- Multiple LLM provider support (OpenAI, Anthropic, etc.)
- Context-aware AI assistance in all modules
- Automated content generation
- Intelligent data analysis
- Conversation history tracking
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        'security/ai_llm_security.xml',
        'security/ir.model.access.csv',
        'data/ai_llm_provider_data.xml',
        'views/ai_llm_provider_views.xml',
        'views/ai_llm_account_views.xml',
        'views/ai_llm_conversation_views.xml',
        'views/ai_llm_menus.xml',
        'wizard/ai_content_generator_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_llm_integration/static/src/js/ai_assistant_widget.js',
            'ai_llm_integration/static/src/xml/ai_assistant_templates.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
