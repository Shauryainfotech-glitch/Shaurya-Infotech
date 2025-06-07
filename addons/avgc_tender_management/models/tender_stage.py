from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TenderStage(models.Model):
    _name = 'avgc.tender.stage'
    _description = 'Tender Stage'
    _order = 'sequence, name'
    
    name = fields.Char('Stage Name', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
    fold = fields.Boolean('Folded in Kanban', default=False)
    
    # Stage properties
    is_initial = fields.Boolean('Initial Stage', default=False)
    is_final = fields.Boolean('Final Stage', default=False)
    is_cancelled = fields.Boolean('Cancelled Stage', default=False)
    
    # Automation
    auto_validation = fields.Boolean('Auto Validation', default=False)
    mail_template_id = fields.Many2one('mail.template', string='Email Template')
    
    # Requirements
    requirement_ids = fields.One2many('avgc.tender.stage.requirement', 'stage_id', string='Requirements')
    dependency_ids = fields.One2many('avgc.tender.stage.dependency', 'stage_id', string='Dependencies')


class TenderStageRequirement(models.Model):
    _name = 'avgc.tender.stage.requirement'
    _description = 'Tender Stage Requirement'
    
    stage_id = fields.Many2one('avgc.tender.stage', string='Stage', required=True, ondelete='cascade')
    name = fields.Char('Requirement', required=True)
    description = fields.Text('Description')
    is_mandatory = fields.Boolean('Mandatory', default=True)
    
    # Validation
    validation_type = fields.Selection([
        ('manual', 'Manual Check'),
        ('document', 'Document Required'),
        ('approval', 'Approval Required'),
        ('system', 'System Validation'),
    ], string='Validation Type', default='manual')
    
    document_type = fields.Char('Required Document Type')
    approver_group = fields.Many2one('res.groups', string='Approver Group')


class TenderStageDependency(models.Model):
    _name = 'avgc.tender.stage.dependency'
    _description = 'Tender Stage Dependency'
    
    stage_id = fields.Many2one('avgc.tender.stage', string='Stage', required=True, ondelete='cascade')
    depends_on_stage_id = fields.Many2one('avgc.tender.stage', string='Depends on Stage', required=True)
    dependency_type = fields.Selection([
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('blocking', 'Blocking'),
    ], string='Dependency Type', default='required')
    
    description = fields.Text('Description')
