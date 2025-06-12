import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Initialize default data after module installation"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    try:
        # Create default AI prompt templates if they don't exist
        template_model = env['ai.prompt.template']
        if not template_model.search([('is_default', '=', True)]):
            _logger.info("Creating default AI prompt templates...")
            # Templates will be created via data files

        _logger.info("Post-installation hook completed successfully")
    except Exception as e:
        _logger.error("Error in post-installation hook: %s", str(e))