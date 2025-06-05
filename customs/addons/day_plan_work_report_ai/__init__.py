import logging

_logger = logging.getLogger(__name__)

from . import models
from . import report

# Import wizards if the module exists
try:
    from . import wizards
except ImportError:
    _logger.debug("wizards.py not found, skipping import")

def post_init_hook(cr, registry):
    # Placeholder for post-init hook logic
    _logger.info("post_init_hook called for day_plan_work_report_ai module")