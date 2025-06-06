from odoo import models, fields, api

class MrpEstimationVersion(models.Model):
    _name = 'mrp.estimation.version'
    _description = 'Estimation Version Control'
    _order = 'creation_date desc'

    parent_estimation_id = fields.Many2one(
        'mrp.estimation',
        string='Original Estimation',
        required=True,
        ondelete='cascade'
    )
    
    version_number = fields.Float(string='Version Number', required=True)
    version_notes = fields.Text(string='Change Notes')
    created_by = fields.Many2one('res.users', string='Created By', required=True)
    creation_date = fields.Datetime(string='Creation Date', required=True)
    is_active_version = fields.Boolean(string='Active Version', default=False)
