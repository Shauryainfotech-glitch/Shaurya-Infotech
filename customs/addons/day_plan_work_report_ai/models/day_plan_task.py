import logging
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DayPlanTask(models.Model):
    _name = "day.plan.task"
    _description = "Day Plan Task"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, sequence, id'

    name = fields.Char(string="Task Name", required=True, tracking=True)
    sequence = fields.Integer(string="Sequence", default=10)
    day_plan_id = fields.Many2one('day.plan', string="Day Plan", required=True, ondelete='cascade')

    # Task Details
    description = fields.Text(string="Description")
    task_type = fields.Selection([
        ('meeting', 'Meeting'),
        ('development', 'Development'),
        ('analysis', 'Analysis'),
        ('documentation', 'Documentation'),
        ('review', 'Review'),
        ('other', 'Other')
    ], string="Task Type", default='other')

    # Status and Priority
    status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='todo', tracking=True)

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string="Priority", default='1')

    # Time Management
    estimated_hours = fields.Float(string="Estimated Hours")
    actual_hours = fields.Float(string="Actual Hours")
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    deadline = fields.Datetime(string="Deadline")

    # Progress
    progress = fields.Float(string="Progress (%)", default=0.0)

    # Relations
    project_id = fields.Many2one('project.project', string="Project")
    tag_ids = fields.Many2many('day.plan.task.tag', string="Tags")

    # Notes
    blocker_notes = fields.Text(string="Blocker Notes")
    completion_notes = fields.Text(string="Completion Notes")

    @api.onchange('status')
    def _onchange_status(self):
        if self.status == 'done':
            self.progress = 100.0
            if not self.end_time:
                self.end_time = fields.Datetime.now()
        elif self.status == 'in_progress':
            if not self.start_time:
                self.start_time = fields.Datetime.now()

    def action_start_task(self):
        """Start the task"""
        self.write({
            'status': 'in_progress',
            'start_time': fields.Datetime.now()
        })

    def action_complete_task(self):
        """Complete the task"""
        self.write({
            'status': 'done',
            'progress': 100.0,
            'end_time': fields.Datetime.now()
        })


class DayPlanTaskTag(models.Model):
    _name = "day.plan.task.tag"
    _description = "Task Tag"

    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string="Color")
    active = fields.Boolean(string="Active", default=True)