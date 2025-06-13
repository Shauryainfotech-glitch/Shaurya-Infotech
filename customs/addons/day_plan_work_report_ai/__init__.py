import logging

_logger = logging.getLogger(__name__)

from . import models

# Import report if the module exists
try:
    from . import report
except ImportError:
    _logger.debug("report directory not found, skipping import")

# Import wizard if the module exists
try:
    from . import wizard
except ImportError:
    _logger.debug("wizard directory not found, skipping import")


def post_init_hook(env):
    """Post-init hook to perform actions after module installation.

    This function is called when the module is installed or upgraded.

    Args:
        env: The Odoo environment to interact with the database
    """
    try:
        # Ensure dashboard data exists
        _logger.info("Running post-init hook for day_plan_work_report_ai module")

        # Create default dashboard records if needed
        dashboard_model = env['day.plan.dashboard.clean']
        if not dashboard_model.search([]):
            dashboard_model.create({
                'name': 'Default Dashboard'
            })
            _logger.info("Created default dashboard record")

        # You can add more initialization code here if needed
        _logger.info("Post-init hook for day_plan_work_report_ai module executed successfully")

    except Exception as e:
        _logger.error("Error in post_init_hook: %s", str(e))
        # Don't raise the error to avoid installation failure
        pass


def _uninstall_hook(env):
    """Uninstall hook to clean up when module is uninstalled.

    Args:
        env: The Odoo environment to interact with the database
    """
    try:
        _logger.info("Running uninstall hook for day_plan_work_report_ai module")
        # Add cleanup code here if needed
        _logger.info("Uninstall hook completed successfully")
    except Exception as e:
        _logger.error("Error in uninstall hook: %s", str(e))
        pass