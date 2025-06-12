import logging
import json
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AIAnalysis(models.Model):
    _name = "ai.analysis"
    _description = "AI Analysis Results"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string="Analysis Name", required=True, default="AI Analysis")
    sequence = fields.Char(string="Reference", readonly=True, copy=False, index=True)

    # Analysis Type and Target
    analysis_type = fields.Selection([
        ('daily', 'Daily Plan Analysis'),
        ('work_report', 'Work Report Analysis'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Review'),
        ('trend', 'Trend Analysis')
    ], string="Analysis Type", required=True, default='daily')

    # Relations
    day_plan_id = fields.Many2one('day.plan', string="Day Plan")
    work_report_id = fields.Many2one('work.report', string="Work Report")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,
                                  default=lambda self: self.env.user.employee_id)

    # AI Provider
    ai_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google'),
        ('mock', 'Mock Provider')
    ], string="AI Provider", default='mock')

    # Analysis Results
    productivity_score = fields.Float(string="Productivity Score", help="0-100 scale")
    efficiency_rating = fields.Float(string="Efficiency Rating", help="0-100 scale")
    wellbeing_assessment = fields.Float(string="Wellbeing Assessment", help="0-100 scale")

    # Content
    summary = fields.Text(string="Analysis Summary")
    strengths = fields.Text(string="Identified Strengths")
    improvement_areas = fields.Text(string="Areas for Improvement")
    recommendations = fields.Text(string="Recommendations")
    trend_analysis = fields.Text(string="Trend Analysis")

    # Technical Data
    raw_prompt = fields.Text(string="Raw Prompt", groups="base.group_system")
    raw_response = fields.Text(string="Raw AI Response", groups="base.group_system")
    time_allocation = fields.Text(string="Time Allocation JSON")

    # Status
    state = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string="Status", default='pending', tracking=True)

    error_message = fields.Text(string="Error Message")

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('ai.analysis') or 'New'
        return super(AIAnalysis, self).create(vals)

    def action_process_analysis(self):
        """Process AI analysis"""
        self.state = 'processing'
        try:
            # Mock analysis for now
            self._perform_mock_analysis()
            self.state = 'completed'
        except Exception as e:
            self.error_message = str(e)
            self.state = 'failed'
            _logger.error("AI Analysis failed: %s", str(e))

    def _perform_mock_analysis(self):
        """Perform mock analysis for testing"""
        import random

        self.productivity_score = random.randint(70, 95)
        self.efficiency_rating = random.randint(65, 90)
        self.wellbeing_assessment = random.randint(60, 85)

        self.summary = "Mock AI analysis shows good productivity levels with room for improvement in time management."
        self.strengths = "Strong task completion rate and consistent goal achievement."
        self.improvement_areas = "Better time estimation and reducing context switching."
        self.recommendations = "1. Use time blocking techniques\n2. Batch similar tasks\n3. Take regular breaks"


class AIPromptTemplate(models.Model):
    _name = "ai.prompt.template"
    _description = "AI Prompt Template"

    name = fields.Char(string="Template Name", required=True)
    analysis_type = fields.Selection([
        ('daily', 'Daily Plan'),
        ('work_report', 'Work Report'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Review'),
        ('trend', 'Trend Analysis')
    ], string="Analysis Type", required=True)

    template = fields.Text(string="Prompt Template", required=True)
    description = fields.Text(string="Description")
    is_default = fields.Boolean(string="Is Default Template")
    active = fields.Boolean(string="Active", default=True)