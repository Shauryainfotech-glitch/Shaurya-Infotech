import logging
_logger = logging.getLogger(__name__)

from . import models
from . import report

# Import wizard if the module exists
try:
    from . import wizard  # Changed from 'wizards' to 'wizard' to match directory name
except ImportError:
    # If wizard directory doesn't exist, we can safely ignore it
    _logger.debug("wizard directory not found, skipping import")

def post_init_hook(env):
    """Post-init hook to perform actions after module installation.

    This function is called when the module is installed or upgraded.

    Args:
        env: The Odoo environment to interact with the database
    """
    # You can add initialization code here if needed
    # For example, setting up default configurations
    _logger.info("Post-init hook for day_plan_work_report_ai module executed successfully")
