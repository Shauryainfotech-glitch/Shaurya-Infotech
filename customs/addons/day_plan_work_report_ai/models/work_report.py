import logging
from datetime import date, datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class WorkReport(models.Model):
    _name = "work.report"
    _description = "Daily Work Report"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string="Report Title", required=True, default="Work Report")
    sequence = fields.Char(string="Reference", readonly=True, copy=False, index=True)
    date = fields.Date(string="Report Date", required=True, default=fields.Date.context_today, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,
                                  default=lambda self: self.env.user.employee_id, tracking=True)
    day_plan_id = fields.Many2one('day.plan', string="Related Day Plan")

    # Report Content
    accomplishments = fields.Text(string="Accomplishments", help="What did you accomplish today?")
    challenges = fields.Text(string="Challenges", help="What challenges did you face?")
    solutions = fields.Text(string="Solutions", help="How did you solve the challenges?")
    learnings = fields.Text(string="Key Learnings", help="What did you learn today?")
    next_steps = fields.Text(string="Next Steps", help="What are your next steps?")

    # Self Assessment
    self_productivity = fields.Selection([
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string="Productivity Self-Assessment", default='3')

    self_quality = fields.Selection([
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string="Quality Self-Assessment", default='3')

    self_satisfaction = fields.Selection([
        ('1', 'Very Low'),
        ('2', 'Low'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string="Satisfaction Self-Assessment", default='3')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed')
    ], string="Status", default='draft', tracking=True)

    # AI Analysis
    ai_analysis_ids = fields.One2many('ai.analysis', 'work_report_id', string="AI Analysis")

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('work.report') or 'New'
        return super(WorkReport, self).create(vals)

    def action_submit(self):
        """Submit the work report"""
        self.state = 'submitted'

    def action_request_ai_analysis(self):
        """Request AI analysis for this work report"""
        return {
            'name': _('Request AI Analysis'),
            'view_mode': 'form',
            'res_model': 'ai.analysis',
            'type': 'ir.actions.act_window',
            'context': {
                'default_work_report_id': self.id,
                'default_analysis_type': 'work_report'
            },
            'target': 'new'
        }