from . import models
from . import wizards
from . import controllers

def post_init_hook(cr, registry):
    """Post-installation hook to initialize AI services and default settings"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Create default AI service configurations
    ai_service_obj = env['purchase.ai.service']
    
    # Create default AI settings
    ai_settings_obj = env['purchase.ai.settings']
    if not ai_settings_obj.search([]):
        ai_settings_obj.create({
            'name': 'Default AI Settings',
            'risk_threshold_high': 0.7,
            'auto_approve_low_risk': True,
            'max_vendor_suggestions': 5,
            'enable_response_caching': True,
            'cache_expiry_hours': 24,
        })
    
    # Initialize AI processing queues
    queue_obj = env['ai.processing.queue']
    
    # Create default vendor scoring weights
    scoring_obj = env['vendor.scoring.weights']
    if not scoring_obj.search([]):
        scoring_obj.create({
            'name': 'Default Scoring Weights',
            'price_competitiveness': 0.25,
            'quality_history': 0.25,
            'delivery_reliability': 0.20,
            'relationship_score': 0.15,
            'compliance_rating': 0.15,
        })

def uninstall_hook(cr, registry):
    """Cleanup hook to remove AI-related data on uninstall"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clear AI cache
    env['ai.cache'].search([]).unlink()
    
    # Clear processing queues
    env['ai.processing.queue'].search([]).unlink() 