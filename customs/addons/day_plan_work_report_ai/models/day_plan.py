import logging
from datetime import date, datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DayPlan(models.Model):
    _name = "day.plan"
    _description = "Daily Work Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # Basic Information
    name = fields.Char(string="Plan Title", required=True, tracking=True, default="New Plan")
    sequence = fields.Char(string="Reference", readonly=True, copy=False, index=True)
    date = fields.Date(string="Plan Date", required=True, default=fields.Date.context_today, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,
                                  default=lambda self: self.env.user.employee_id, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company, tracking=True)

    # Time Management
    planned_start = fields.Datetime(string="Planned Start Time", tracking=True)
    planned_end = fields.Datetime(string="Planned End Time", tracking=True)
    actual_start = fields.Datetime(string="Actual Start Time")
    actual_end = fields.Datetime(string="Actual End Time")

    # Plan Content
    goals = fields.Text(string="Daily Goals", help="What do you want to achieve today?")
    key_results = fields.Text(string="Key Results", help="What key results do you want to achieve?")
    focus_areas = fields.Text(string="Focus Areas", help="What areas will you focus on today?")
    potential_blockers = fields.Text(string="Potential Blockers", help="List any potential blockers")

    # Status and Progress
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', tracking=True)

    # Task Management
    task_ids = fields.One2many('day.plan.task', 'day_plan_id', string="Tasks")
    total_tasks = fields.Integer(string="Total Tasks", compute='_compute_task_stats', store=True)
    tasks_completed = fields.Integer(string="Completed Tasks", compute='_compute_task_stats', store=True)
    completion_ratio = fields.Float(string="Completion Ratio", compute='_compute_task_stats', store=True)

    # Work Report
    work_report_id = fields.One2many('work.report', 'day_plan_id', string="Work Report")
    has_work_report = fields.Boolean(string="Has Work Report", compute='_compute_has_work_report')

    # AI Analysis
    ai_analysis_ids = fields.One2many('ai.analysis', 'day_plan_id', string="AI Analysis")
    has_ai_analysis = fields.Boolean(string="Has AI Analysis", compute='_compute_has_ai_analysis')

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('day.plan') or 'New'
        return super(DayPlan, self).create(vals)

    @api.depends('task_ids', 'task_ids.status')
    def _compute_task_stats(self):
        for plan in self:
            tasks = plan.task_ids
            plan.total_tasks = len(tasks)
            plan.tasks_completed = len(tasks.filtered(lambda t: t.status == 'done'))
            plan.completion_ratio = (plan.tasks_completed / plan.total_tasks * 100) if plan.total_tasks else 0.0

    @api.depends('work_report_id')
    def _compute_has_work_report(self):
        for plan in self:
            plan.has_work_report = bool(plan.work_report_id)

    @api.depends('ai_analysis_ids')
    def _compute_has_ai_analysis(self):
        for plan in self:
            plan.has_ai_analysis = bool(plan.ai_analysis_ids)

    def action_start_plan(self):
        """Start the day plan"""
        self.write({
            'state': 'active',
            'actual_start': fields.Datetime.now()
        })

    def action_complete_plan(self):
        """Complete the day plan"""
        self.write({
            'state': 'completed',
            'actual_end': fields.Datetime.now()
        })

    def action_view_tasks(self):
        """View tasks for this plan"""
        return {
            'name': _('Tasks'),
            'view_mode': 'tree,form,kanban',
            'res_model': 'day.plan.task',
            'type': 'ir.actions.act_window',
            'domain': [('day_plan_id', '=', self.id)],
            'context': {'default_day_plan_id': self.id}
        }

    def action_create_work_report(self):
        """Create work report for this plan"""
        return {
            'name': _('Create Work Report'),
            'view_mode': 'form',
            'res_model': 'work.report',
            'type': 'ir.actions.act_window',
            'context': {'default_day_plan_id': self.id},
            'target': 'new'
        }