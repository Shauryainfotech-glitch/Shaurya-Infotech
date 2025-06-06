# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ArchitectProject(models.Model):
    _inherit = 'project.project'

    # Mark as architect project
    is_architect_project = fields.Boolean(string='Is Architect Project', default=False)

    # Project classification
    project_type = fields.Selection([
        ('government', 'Government Project'),
        ('private', 'Private Project'),
        ('dpr', 'DPR Project'),
        ('survey', 'Survey Project'),
        ('eco_tourism', 'Eco Tourism'),
        ('infrastructure', 'Infrastructure')
    ], string='Project Type')

    category = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('institutional', 'Institutional'),
        ('infrastructure', 'Infrastructure'),
        ('eco_tourism', 'Eco Tourism'),
        ('mixed_use', 'Mixed Use')
    ], string='Project Category')

    # Client information
    client_name = fields.Char(string='Client Name')
    client_contact = fields.Char(string='Client Contact')
    client_email = fields.Char(string='Client Email')

    # Project details
    project_location = fields.Text(string='Project Location')
    estimated_area = fields.Float(string='Estimated Area (sq ft)')
    plot_area = fields.Float(string='Plot Area (sq ft)')
    built_up_area = fields.Float(string='Built-up Area (sq ft)')

    # Financial fields
    estimated_budget = fields.Monetary(string='Estimated Budget', currency_field='currency_id')
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id')
    budget = fields.Monetary(string='Approved Budget', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)

    # Timeline
    start_date = fields.Date(string='Start Date')
    deadline = fields.Date(string='Deadline')
    completion_date = fields.Date(string='Completion Date')

    # Progress tracking
    progress = fields.Float(string='Progress (%)', default=0.0)

    # Project state - this is the field that was missing
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold')
    ], string='Project State', default='draft', tracking=True)

    # DPR related fields
    dpr_required = fields.Boolean(string='DPR Required')
    dpr_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved')
    ], string='DPR Status', default='not_started')

    # Compliance fields
    fca_compliance = fields.Boolean(string='FCA Compliance Required')
    ecotourism_compliance = fields.Boolean(string='Ecotourism Compliance')
    environmental_clearance = fields.Boolean(string='Environmental Clearance Required')

    # Relationships
    stage_id = fields.Many2one('avf.project.stage', string='Project Stage')
    team_ids = fields.Many2many('architect.team', string='Project Teams')
    dpr_ids = fields.One2many('architect.dpr', 'project_id', string='DPR Records')
    survey_ids = fields.One2many('architect.survey', 'project_id', string='Surveys')

    # Computed fields
    dpr_count = fields.Integer(string='DPR Count', compute='_compute_dpr_count')
    survey_count = fields.Integer(string='Survey Count', compute='_compute_survey_count')

    @api.depends('dpr_ids')
    def _compute_dpr_count(self):
        for project in self:
            project.dpr_count = len(project.dpr_ids)

    @api.depends('survey_ids')
    def _compute_survey_count(self):
        for project in self:
            project.survey_count = len(project.survey_ids)

    @api.constrains('estimated_budget', 'estimated_cost')
    def _check_budget_cost(self):
        for project in self:
            if project.estimated_cost and project.estimated_budget:
                if project.estimated_cost > project.estimated_budget * 1.2:  # 20% tolerance
                    raise ValidationError(_('Estimated cost exceeds budget by more than 20%. Please review.'))

    def action_confirm(self):
        self.state = 'confirmed'

    def action_start(self):
        self.state = 'in_progress'
        if not self.start_date:
            self.start_date = fields.Date.today()

    def action_review(self):
        self.state = 'review'

    def action_approve(self):
        self.state = 'approved'

    def action_complete(self):
        self.state = 'completed'
        self.completion_date = fields.Date.today()
        self.progress = 100.0

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        self.state = 'draft'

class ArchitectProject(models.Model):
    _name = 'architect.project'
    _description = 'Architectural Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Project Name', required=True, tracking=True)
    code = fields.Char(string='Project Code', required=True, copy=False)
    description = fields.Text(string='Description')

    # Client Information
    partner_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    contact_person = fields.Char(string='Contact Person')
    client_email = fields.Char(string='Client Email')
    client_phone = fields.Char(string='Client Phone')

    # Project Details
    project_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('institutional', 'Institutional'),
        ('industrial', 'Industrial'),
        ('government', 'Government'),
        ('mixed', 'Mixed Use')
    ], string='Project Type', required=True)

    # Location
    project_location = fields.Text(string='Project Location')
    state_id = fields.Many2one('res.country.state', string='State')
    district = fields.Char(string='District')

    # Dates
    date_start = fields.Date(string='Project Start Date')
    expected_end_date = fields.Date(string='Expected End Date')
    actual_end_date = fields.Date(string='Actual End Date')

    # Financial
    budget = fields.Monetary(string='Budget', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)

    # Status
    # Using project.task.type for stages instead of custom stage model
    project_stage_id = fields.Many2one('project.task.type', string='Project Stage', tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1')

    # Team
    user_id = fields.Many2one('res.users', string='Project Manager', 
                             default=lambda self: self.env.user, tracking=True)
    team_member_ids = fields.Many2many('res.users', string='Team Members')

    # Progress
    progress = fields.Float(string='Progress (%)', compute='_compute_progress', store=True)

    # Compliance
    requires_fca = fields.Boolean(string='Requires FCA Clearance')
    requires_environment = fields.Boolean(string='Requires Environmental Clearance')

    # Related Records
    drawing_count = fields.Integer(string='Drawings', compute='_compute_counts')
    document_count = fields.Integer(string='Documents', compute='_compute_counts')
    financial_tracking_ids = fields.One2many('architect.financial.tracking', 'project_id', string='Financial Records')
    budget_ids = fields.One2many('architect.budget', 'project_id', string='Budgets')
    cost_estimate_ids = fields.One2many('architect.cost.estimate', 'project_id', string='Cost Estimates')

    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _get_default_stage(self):
        return self.env['architect.project.stage'].search([('is_initial', '=', True)], limit=1)

    @api.depends('stage_id')
    def _compute_progress(self):
        for project in self:
            project.progress = project.stage_id.progress if project.stage_id else 0.0

    def _compute_counts(self):
        for project in self:
            project.drawing_count = 0  # Will be updated when drawing model is complete
            project.document_count = 0  # Will be updated when document model is complete


    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get('is_architect_project'):
                vals['name'] = self.env['ir.sequence'].next_by_code('avf.architect.project') or _('New Project')

        return super().create(vals_list)

class ArchitectProjectStage(models.Model):
    _name = 'architect.project.stage'
    _description = 'Project Stage'
    _order = 'sequence'

    name = fields.Char(string='Stage Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    progress = fields.Float(string='Progress %', help="Progress percentage for this stage")
    fold = fields.Boolean(string='Folded in Pipeline')

    # Stage Requirements
    requirements = fields.Text(string='Stage Requirements')
    deliverables = fields.Text(string='Expected Deliverables')

    # Approval Settings
    requires_approval = fields.Boolean(string='Requires Approval')
    approval_users = fields.Many2many('res.users', string='Approval Users')

    # Color coding
    color = fields.Integer(string='Color')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    architect_project_id = fields.Many2one('architect.project', string='Architect Project')
    task_type = fields.Selection([
        ('design', 'Design'),
        ('survey', 'Survey'),
        ('documentation', 'Documentation'),
        ('compliance', 'Compliance Check'),
        ('review', 'Review'),
        ('approval', 'Approval'),
        ('coordination', 'Coordination')
    ], string='Task Type')

    drawing_ids = fields.Many2many('architect.drawing', string='Related Drawings')
    requires_site_visit = fields.Boolean(string='Requires Site Visit')
    site_visit_date = fields.Datetime(string='Site Visit Date')