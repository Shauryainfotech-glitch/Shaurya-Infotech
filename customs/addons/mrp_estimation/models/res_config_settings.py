from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    estimation_sequence_prefix = fields.Char(
        string='Estimation Sequence Prefix',
        config_parameter='mrp_estimation.sequence_prefix',
        default='EST'
    )
    
    auto_markup_enabled = fields.Boolean(
        string='Enable Auto Markup',
        config_parameter='mrp_estimation.auto_markup',
        default=False
    )
    
    approval_required = fields.Boolean(
        string='Require Approval Workflow',
        config_parameter='mrp_estimation.approval_required',
        default=True
    )
    
    version_increment = fields.Float(
        string='Version Increment Value',
        config_parameter='mrp_estimation.version_increment',
        default=0.1
    )
    
    default_material_markup = fields.Float(
        string='Default Material Markup (%)',
        config_parameter='mrp_estimation.default_material_markup',
        default=10.0
    )
    
    default_cost_markup = fields.Float(
        string='Default Cost Markup (%)',
        config_parameter='mrp_estimation.default_cost_markup',
        default=15.0
    )
