from . import models
from . import report

# Import wizards if the module exists
try:
    from . import wizards
except ImportError:
    # If wizards.py doesn't exist, we can safely ignore it
    import logging
    _logger = logging.getLogger(__name__)
    _logger.debug("wizards.py not found, skipping import")

def post_init_hook(env):
    """Post-init hook to perform actions after module installation.

    This function is called when the module is installed or upgraded.

    Args:
        env: The Odoo environment to interact with the database
    """
    # You can add initialization code here if needed
    # For example, setting up default configurations
    _logger = logging.getLogger(__name__)
    _logger.info("Post-init hook for day_plan_work_report_ai module executed successfully")
