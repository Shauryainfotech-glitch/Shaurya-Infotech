
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ArchitectProjectStage(models.Model):
    _name = 'architect.project.stage'
    _description = 'Project Stages for Architect Projects'
    _order = 'sequence, name'

    name = fields.Char(string='Stage Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Stage properties
    stage_type = fields.Selection([
        ('planning', 'Planning'),
        ('design', 'Design'),
        ('approval', 'Approval'),
        ('construction', 'Construction'),
        ('completion', 'Completion')
    ], string='Stage Type', required=True)
    
    # Status indicators
    is_start_stage = fields.Boolean(string='Start Stage')
    is_end_stage = fields.Boolean(string='End Stage')
    is_milestone = fields.Boolean(string='Milestone Stage')
    
    # Workflow
    next_stage_ids = fields.Many2many('architect.project.stage', 
                                    'project_stage_next_rel', 'stage_id', 'next_stage_id',
                                    string='Next Possible Stages')
    
    # Requirements
    required_documents = fields.Text(string='Required Documents')
    required_approvals = fields.Text(string='Required Approvals')
    deliverables = fields.Text(string='Stage Deliverables')
    
    # Time estimation
    estimated_duration = fields.Integer(string='Estimated Duration (Days)')
    
    # Colors and display
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    
    # Related projects
    project_ids = fields.One2many('project.project', 'stage_id', string='Projects in this Stage')
    project_count = fields.Integer(string='Project Count', compute='_compute_project_count')

    @api.depends('project_ids')
    def _compute_project_count(self):
        for stage in self:
            stage.project_count = len(stage.project_ids)

class ProjectProjectStageExtension(models.Model):
    _inherit = 'project.project'
    
    stage_id = fields.Many2one('architect.project.stage', string='Project Stage')
    stage_progress = fields.Float(string='Stage Progress %')
    stage_start_date = fields.Date(string='Stage Start Date')
    stage_notes = fields.Text(string='Stage Notes')
    
    def action_move_to_next_stage(self):
        """Move project to next stage"""
        self.ensure_one()
        if self.stage_id and self.stage_id.next_stage_ids:
            # If only one next stage, move automatically
            if len(self.stage_id.next_stage_ids) == 1:
                self.stage_id = self.stage_id.next_stage_ids[0]
                self.stage_start_date = fields.Date.today()
                self.stage_progress = 0.0
            else:
                # Open wizard to select next stage
                return {
                    'name': _('Select Next Stage'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'architect.project.stage.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_project_id': self.id,
                        'default_current_stage_id': self.stage_id.id,
                    },
                }
