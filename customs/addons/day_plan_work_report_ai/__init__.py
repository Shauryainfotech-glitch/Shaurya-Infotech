from . import models
from . import wizards
from . import controllers
from . import report


def post_init_hook(env):
    """Post-installation hook for Odoo 18.0"""
    import logging
    _logger = logging.getLogger(__name__)

    try:
        _logger.info("Day Plan module post-installation hook completed")
    except Exception as e:
        _logger.error("Error in post-installation hook: %s", str(e))