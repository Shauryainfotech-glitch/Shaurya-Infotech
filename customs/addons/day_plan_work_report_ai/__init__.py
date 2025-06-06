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
