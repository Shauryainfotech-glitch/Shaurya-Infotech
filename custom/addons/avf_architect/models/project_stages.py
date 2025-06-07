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

    @api.model_create_multi
    def create(self, vals_list):
        """Create method with batch support to fix deprecation warning"""
        for vals in vals_list:
            if not vals.get('sequence'):
                # Get the next sequence number
                last_sequence = self.search([], order='sequence desc', limit=1)
                vals['sequence'] = (last_sequence.sequence + 1) if last_sequence else 1
        return super(AvfProjectStage, self).create(vals_list)

    def _auto_init(self):
        """Override _auto_init to handle migration safely"""
        try:
            # Call the parent _auto_init first
            result = super(AvfProjectStage, self)._auto_init()

            # Handle migration after table creation
            self._handle_migration_data()
            return result
        except Exception as e:
            _logger.error(f"Error in _auto_init: {e}")
            return super(AvfProjectStage, self)._auto_init()

    @api.model
    def _handle_migration_data(self):
        """Handle migration data creation safely"""
        try:
            # Check if we need to create default stages
            existing_stages = self.search([])
            if not existing_stages:
                # Create default stages
                default_stages = [
                    {'name': 'Initiation', 'sequence': 1, 'stage_type': 'initiation'},
                    {'name': 'Planning', 'sequence': 2, 'stage_type': 'planning'},
                    {'name': 'Design', 'sequence': 3, 'stage_type': 'development'},
                    {'name': 'Approval', 'sequence': 4, 'stage_type': 'monitoring'},
                    {'name': 'Execution', 'sequence': 5, 'stage_type': 'execution'},
                    {'name': 'Completion', 'sequence': 6, 'stage_type': 'closure'},
                ]

                # Create stages without triggering FK constraints
                for stage_data in default_stages:
                    self.create([stage_data])

                _logger.info("Default project stages created successfully")

        except Exception as e:
            _logger.warning(f"Migration data handling warning: {e}")


class ProjectProjectStageExtension(models.Model):
    _inherit = 'project.project'

    stage_id = fields.Many2one('avf.project.stage', string='Project Stage', ondelete='set null')
    stage_progress = fields.Float(string='Stage Progress %')
    stage_start_date = fields.Date(string='Stage Start Date')
    stage_notes = fields.Text(string='Stage Notes')

    def action_move_to_next_stage(self):
        """Move project to next stage"""
        self.ensure_one()
        if self.stage_id:
            # Find next stage by sequence
            next_stage = self.env['avf.project.stage'].search([
                ('sequence', '>', self.stage_id.sequence)
            ], order='sequence asc', limit=1)

            if next_stage:
                self.stage_id = next_stage
                self.stage_start_date = fields.Date.today()
                self.stage_progress = 0.0
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _('Project moved to stage: %s') % next_stage.name,
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _('This is already the final stage'),
                        'type': 'warning',
                    }
                }