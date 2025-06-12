from . import models
from . import wizards
from . import hooks

def post_init_hook(cr, registry):
    """Post-installation hook"""
    from . import hooks
    hooks.post_init_hook(cr, registry)