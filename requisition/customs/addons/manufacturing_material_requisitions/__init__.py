from . import models
from . import controllers
from . import wizards
from . import reports

def post_init_hook(cr, registry):
    """Post-installation hook to set up initial data and configurations"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Basic setup - can be expanded later
    pass

def uninstall_hook(cr, registry):
    """Clean up hook when module is uninstalled"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clean up any scheduled jobs
    crons = env['ir.cron'].search([
        ('model_id.model', 'like', 'manufacturing.material.requisition%')
    ])
    crons.unlink() 