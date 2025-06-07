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

    @api.model
    def _force_stage_ids(self):
        """Force specific IDs for stages to prevent FK constraint violations"""
        # This ensures that commonly referenced stage IDs exist
        stage_data = [
            (1, 'Initiation', 1, 'initiation'),
            (2, 'Planning', 2, 'planning'),
            (3, 'Design', 3, 'development'),
            (4, 'Approval', 4, 'monitoring'),
            (5, 'Execution', 5, 'execution'),
            (6, 'Completion', 6, 'closure'),
        ]
        
        for stage_id, name, sequence, stage_type in stage_data:
            existing = self.search([('id', '=', stage_id)])
            if not existing:
                # Use SQL to force the ID
                self.env.cr.execute("""
                    INSERT INTO avf_project_stage (id, name, sequence, stage_type, active, create_date, write_date, create_uid, write_uid)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        sequence = EXCLUDED.sequence,
                        stage_type = EXCLUDED.stage_type
                """, (stage_id, name, sequence, stage_type, True, self.env.uid, self.env.uid))
        
        # Reset sequence
        self.env.cr.execute("SELECT setval('avf_project_stage_id_seq', (SELECT MAX(id) FROM avf_project_stage), true)")
        self.env.cr.commit()


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