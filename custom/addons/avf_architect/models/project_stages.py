# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AvfProjectStage(models.Model):
    _name = 'avf.project.stage'
    _description = 'Project Stages for Architectural Projects'
    _order = 'sequence, name'

    name = fields.Char(string='Stage Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string='Color Index', default=0)
    fold = fields.Boolean(string='Folded in Kanban')

    # Stage type
    stage_type = fields.Selection([
        ('initiation', 'Project Initiation'),
        ('planning', 'Planning & Design'),
        ('development', 'Development'),
        ('execution', 'Execution'),
        ('monitoring', 'Monitoring'),
        ('closure', 'Project Closure')
    ], string='Stage Type', required=True, default='planning')

    # Requirements and deliverables
    required_documents = fields.Text(string='Required Documents')
    deliverables = fields.Text(string='Stage Deliverables')

    # Workflow automation
    auto_progress = fields.Boolean(string='Auto Progress', 
                                 help='Automatically move to next stage when conditions are met')
    progress_conditions = fields.Text(string='Progress Conditions')

    @api.constrains('sequence')
    def _check_sequence(self):
        for record in self:
            if record.sequence < 0:
                raise ValidationError(_('Sequence must be a positive number.'))


class ProjectProjectStageExtension(models.Model):
    _inherit = 'project.project'
    
    stage_id = fields.Many2one('avf.project.stage', string='Project Stage')
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
                    'res_model': 'avf.project.stage.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_project_id': self.id,
                        'default_current_stage_id': self.stage_id.id,
                    },
                }