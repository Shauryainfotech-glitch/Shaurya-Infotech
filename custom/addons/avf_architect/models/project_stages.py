# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectStages(models.Model):
    _name = 'avf.project.stage'
    _description = 'Architect Project Stages'
    _order = 'sequence, id'
    _rec_name = 'name'

    name = fields.Char(string='Stage Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    is_default = fields.Boolean(string='Default Stage')
    fold = fields.Boolean(string='Folded in Kanban')

    project_ids = fields.One2many('project.project', 'stage_id', string='Projects')
    
class ArchitectProjectStage(models.Model):
    _name = 'architect.project.stage'
    _description = 'Project Stage'
    _order = 'sequence, name'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    progress = fields.Float(string='Progress (%)', default=0.0)
    color = fields.Integer(string='Color Index', default=0)
    fold = fields.Boolean(string='Folded in Kanban')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Stage Properties
    is_closed = fields.Boolean(string='Closing Stage')
    is_initial = fields.Boolean(string='Initial Stage')
    mail_template_id = fields.Many2one('mail.template', string='Email Template')

    # Checklist Requirements
    checklist_template_ids = fields.One2many('architect.stage.checklist.template', 'stage_id', string='Checklist Templates')

class ArchitectStageChecklistTemplate(models.Model):
    _name = 'architect.stage.checklist.template'
    _description = 'Stage Checklist Template'

    name = fields.Char(string='Checklist Item', required=True)
    stage_id = fields.Many2one('architect.project.stage', string='Stage', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    required = fields.Boolean(string='Required', default=True)
    description = fields.Text(string='Description')

class ArchitectProjectChecklist(models.Model):
    _name = 'architect.project.checklist'
    _description = 'Project Checklist Item'

    name = fields.Char(string='Checklist Item', required=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    stage_id = fields.Many2one('architect.project.stage', string='Stage')
    completed = fields.Boolean(string='Completed', default=False)
    completed_date = fields.Datetime(string='Completed Date')
    user_id = fields.Many2one('res.users', string='Responsible User')
    notes = fields.Text(string='Notes')