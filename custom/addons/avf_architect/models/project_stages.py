# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


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
    def create(self, vals):
        if not vals.get('sequence'):
            vals['sequence'] = len(self.search([])) + 1
        return super().create(vals)

    @api.model
    def _handle_migration_conflicts(self):
        """Handle foreign key conflicts during migration"""
        try:
            # Ensure we have stages with IDs 1-6 to prevent FK violations
            required_stages = [
                (1, 'Initiation', 'initiation'),
                (2, 'Planning', 'planning'),
                (3, 'Design', 'development'),
                (4, 'Approval', 'monitoring'),
                (5, 'Execution', 'execution'),
                (6, 'Completion', 'closure'),
            ]

            for stage_id, name, stage_type in required_stages:
                # Check if stage exists
                self.env.cr.execute("SELECT id FROM avf_project_stage WHERE id = %s", (stage_id,))
                if not self.env.cr.fetchone():
                    # Use SQL to create stage with specific ID
                    self.env.cr.execute("""
                        INSERT INTO avf_project_stage 
                        (id, name, sequence, stage_type, active, color, fold, create_date, write_date, create_uid, write_uid)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, (stage_id, name, stage_id, stage_type, True, 0, False, 1, 1))

            # Update sequence to continue from the highest ID
            self.env.cr.execute("""
                SELECT setval('avf_project_stage_id_seq', 
                    (SELECT COALESCE(MAX(id), 0) FROM avf_project_stage), true)
            """)
            
            # Commit the transaction
            self.env.cr.commit()

        except Exception as e:
            _logger.warning(f"Migration conflict handling error: {e}")

    @api.model
    def create_missing_stages(self):
        """Create any missing stages that are referenced by existing data"""
        try:
            # Find all stage_id values referenced in project_project
            self.env.cr.execute("""
                SELECT DISTINCT stage_id 
                FROM project_project 
                WHERE stage_id IS NOT NULL 
                AND stage_id NOT IN (SELECT id FROM avf_project_stage)
            """)
            missing_stage_ids = [row[0] for row in self.env.cr.fetchall()]
            
            for stage_id in missing_stage_ids:
                self.env.cr.execute("""
                    INSERT INTO avf_project_stage 
                    (id, name, sequence, stage_type, active, color, fold, create_date, write_date, create_uid, write_uid)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (stage_id, f'Stage {stage_id}', stage_id, 'initiation', True, 0, False, 1, 1))
            
            self.env.cr.commit()
            _logger.info(f"Created missing stages: {missing_stage_ids}")
            
        except Exception as e:
            _logger.warning(f"Error creating missing stages: {e}")

    @api.model
    def _force_stage_ids(self):
        """Force specific stage IDs for migration compatibility"""
        self._handle_migration_conflicts()
        self.create_missing_stages()


class ProjectProjectStageExtension(models.Model):
    _inherit = 'project.project'

    stage_id = fields.Many2one('avf.project.stage', string='Project Stage')
    stage_progress = fields.Float(string='Stage Progress %')
    stage_start_date = fields.Date(string='Stage Start Date')
    stage_notes = fields.Text(string='Stage Notes')

    @api.model
    def _register_hook(self):
        """Handle migration conflicts when the model is loaded"""
        try:
            # Ensure stage records exist before foreign key constraints are applied
            stage_model = self.env['avf.project.stage']
            stage_model._handle_migration_conflicts()
            stage_model.create_missing_stages()
        except Exception as e:
            _logger.warning(f"Migration hook error: {e}")
        return super()._register_hook()

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