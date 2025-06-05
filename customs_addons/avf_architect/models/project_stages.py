# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ArchitectProjectStage(models.Model):
    _name = 'architect.project.stage'
    _description = 'Project Stage'
    _order = 'sequence'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    fold = fields.Boolean(string='Folded in Kanban')
    active = fields.Boolean(default=True)
    
    # Progress tracking
    progress = fields.Float(string='Progress (%)', 
                          help="Progress percentage for this stage")
    
    # Stage Requirements
    requirements = fields.Html(string='Stage Requirements',
                             help="Requirements to complete this stage")
    deliverables = fields.Html(string='Expected Deliverables',
                             help="Expected deliverables for this stage")
    
    # Approvals
    requires_approval = fields.Boolean(string='Requires Approval')
    approval_user_ids = fields.Many2many('res.users', string='Approvers')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True
    )
    # Stage Type
    stage_type = fields.Selection([
        ('concept', 'Concept Design'),
        ('preliminary', 'Preliminary Design'),
        ('detailed', 'Detailed Design'),
        ('documentation', 'Documentation'),
        ('approval', 'Approval'),
        ('tender', 'Tender'),
        ('construction', 'Construction'),
        ('completion', 'Completion')
    ], string='Stage Type')
    
    # Checklists
    checklist_template_ids = fields.One2many('architect.stage.checklist.template', 
                                           'stage_id', string='Checklist Templates')
    
    # Time Management
    expected_duration = fields.Integer(string='Expected Duration (Days)',
                                     help="Expected duration for this stage")
    
    # Dependencies
    previous_stage_id = fields.Many2one('architect.project.stage', string='Previous Stage')
    next_stage_id = fields.Many2one('architect.project.stage', string='Next Stage')
    
    # UI/UX
    color = fields.Integer(string='Color Index')
    icon = fields.Char(string='Icon', help="FontAwesome icon name")
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Stage name must be unique!")
    ]


class ArchitectStageChecklistTemplate(models.Model):
    _name = 'architect.stage.checklist.template'
    _description = 'Stage Checklist Template'
    _order = 'sequence'

    name = fields.Char(string='Item Name', required=True)
    stage_id = fields.Many2one('architect.project.stage', string='Stage', 
                              required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    
    description = fields.Text(string='Description')
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
    
    # Item Type
    item_type = fields.Selection([
        ('document', 'Document Required'),
        ('approval', 'Approval Required'),
        ('task', 'Task to Complete'),
        ('milestone', 'Milestone'),
        ('review', 'Review Required')
    ], string='Item Type', required=True)
    
    # Responsibility
    responsible_role = fields.Selection([
        ('manager', 'Project Manager'),
        ('architect', 'Architect'),
        ('engineer', 'Engineer'),
        ('consultant', 'Consultant'),
        ('client', 'Client'),
        ('team', 'Team Member')
    ], string='Responsible Role')
    
    # Verification
    verification_method = fields.Selection([
        ('document', 'Document Upload'),
        ('signature', 'Digital Signature'),
        ('checklist', 'Checklist'),
        ('approval', 'Approval Flow')
    ], string='Verification Method')
    
    # Dependencies
    dependent_item_ids = fields.Many2many('architect.stage.checklist.template', 
                                        'checklist_dependency_rel',
                                        'item_id', 'dependent_item_id',
                                        string='Dependent Items')
    
    # Instructions
    instructions = fields.Html(string='Instructions')
    
    # Templates and References
    document_template = fields.Binary(string='Document Template')
    template_filename = fields.Char(string='Template Filename')
    reference_documents = fields.Text(string='Reference Documents')


class ArchitectProjectChecklist(models.Model):
    _name = 'architect.project.checklist'
    _description = 'Project Stage Checklist'
    _order = 'sequence'

    name = fields.Char(string='Item Name', required=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    stage_id = fields.Many2one('architect.project.stage', string='Stage', required=True)
    template_id = fields.Many2one('architect.stage.checklist.template', string='Template')
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Status
    completed = fields.Boolean(string='Completed')
    completion_date = fields.Datetime(string='Completion Date')
    completed_by = fields.Many2one('res.users', string='Completed By')
    
    # Verification
    verified = fields.Boolean(string='Verified')
    verified_by = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Datetime(string='Verification Date')
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Notes
    notes = fields.Text(string='Notes')
    internal_notes = fields.Text(string='Internal Notes')
    
    @api.onchange('completed')
    def _onchange_completed(self):
        if self.completed:
            self.completion_date = fields.Datetime.now()
            self.completed_by = self.env.user.id
        else:
            self.completion_date = False
            self.completed_by = False
            self.verified = False
            self.verified_by = False
            self.verification_date = False
    
    def action_verify(self):
        self.write({
            'verified': True,
            'verified_by': self.env.user.id,
            'verification_date': fields.Datetime.now()
        })
