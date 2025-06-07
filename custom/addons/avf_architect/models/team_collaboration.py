# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AvfTeamCollaboration(models.Model):
    _name = 'avf.team.collaboration'
    _description = 'Team Collaboration and Task Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_deadline'

    name = fields.Char(string='Task Title', required=True, tracking=True)
    description = fields.Html(string='Description')
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')

    # Assignment
    assigned_to = fields.Many2one('res.users', string='Assigned To', required=True, tracking=True)
    team_members = fields.Many2many('res.users', string='Team Members')

    # Timing
    date_start = fields.Datetime(string='Start Date', default=fields.Datetime.now)
    date_deadline = fields.Datetime(string='Deadline', required=True)
    date_completed = fields.Datetime(string='Completed Date')

    # Priority and status
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1')

    state = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='todo', tracking=True)

    # Progress tracking
    progress = fields.Float(string='Progress (%)', default=0.0)
    estimated_hours = fields.Float(string='Estimated Hours')
    actual_hours = fields.Float(string='Actual Hours')

    # Files and attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    # Comments and notes
    notes = fields.Text(string='Notes')

    # Dependencies
    dependency_ids = fields.Many2many('avf.team.collaboration', 'task_dependency_rel', 
                                    'task_id', 'dependency_id', string='Dependencies')
    dependent_task_ids = fields.Many2many('avf.team.collaboration', 'task_dependency_rel', 
                                        'dependency_id', 'task_id', string='Dependent Tasks')

    @api.constrains('progress')
    def _check_progress(self):
        for record in self:
            if not 0 <= record.progress <= 100:
                raise ValidationError(_('Progress must be between 0 and 100.'))

    @api.constrains('date_start', 'date_deadline')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_deadline and record.date_start > record.date_deadline:
                raise ValidationError(_('Start date cannot be later than deadline.'))

    def action_start_task(self):
        self.state = 'in_progress'
        if not self.date_start:
            self.date_start = fields.Datetime.now()

    def action_complete_task(self):
        self.state = 'done'
        self.progress = 100.0
        self.date_completed = fields.Datetime.now()