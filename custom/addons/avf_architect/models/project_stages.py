# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ArchitectProjectStage(models.Model):
    _name = 'avf.project.stage'
    _description = 'Architect Project Stages'
    _order = 'sequence, id'
    _rec_name = 'name'

    name = fields.Char(string='Stage Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    is_default = fields.Boolean(string='Default Stage')
    fold = fields.Boolean(string='Folded in Kanban')
    active = fields.Boolean(string='Active', default=True)

    # Stage configuration
    allow_timesheet = fields.Boolean(string='Allow Timesheets', default=True)
    is_closed = fields.Boolean(string='Closing Stage', help='Tasks in this stage are considered closed')

    project_ids = fields.One2many('architect.project', 'stage_id', string='Projects')
    project_count = fields.Integer(string='Project Count', compute='_compute_project_count')

    @api.depends('project_ids')
    def _compute_project_count(self):
        for stage in self:
            stage.project_count = len(stage.project_ids)

    @api.constrains('is_default')
    def _check_default_stage(self):
        if self.is_default:
            other_defaults = self.search([('is_default', '=', True), ('id', '!=', self.id)])
            if other_defaults:
                raise ValidationError(_('Only one stage can be set as default.'))

class ArchitectStageChecklistTemplate(models.Model):
    _name = 'architect.stage.checklist.template'
    _description = 'Stage Checklist Template'

    name = fields.Char(string='Checklist Item', required=True)
    stage_id = fields.Many2one('avf.project.stage', string='Stage', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    required = fields.Boolean(string='Required', default=True)
    description = fields.Text(string='Description')

class ArchitectProjectChecklist(models.Model):
    _name = 'architect.project.checklist'
    _description = 'Project Checklist Item'

    name = fields.Char(string='Checklist Item', required=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    stage_id = fields.Many2one('avf.project.stage', string='Stage')
    completed = fields.Boolean(string='Completed', default=False)
    completed_date = fields.Datetime(string='Completed Date')
    user_id = fields.Many2one('res.users', string='Responsible User')
    notes = fields.Text(string='Notes')