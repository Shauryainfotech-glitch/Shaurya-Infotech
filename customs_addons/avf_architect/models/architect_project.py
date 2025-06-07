# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class ArchitectProject(models.Model):
    _name = 'architect.project'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Architectural Project'
    _order = 'create_date desc'

    name = fields.Char(string='Project Name', required=True, tracking=True)
    code = fields.Char(string='Project Code', required=True, copy=False, tracking=True)
    description = fields.Text(string='Description')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True
    )
    partner_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    client_type = fields.Selection([
        ('government', 'Government'),
        ('private', 'Private'),
        ('public_sector', 'Public Sector'),
        ('ngo', 'NGO')
    ], string='Client Type', required=True, default='government')

    project_type = fields.Selection([
        ('architectural', 'Architectural Design'),
        ('urban_planning', 'Urban Planning'),
        ('landscape', 'Landscape Architecture'),
        ('interior', 'Interior Design'),
        ('consultation', 'Consultation'),
        ('survey', 'Survey & Assessment'),
        ('ecotourism', 'Ecotourism Development')
    ], string='Project Type', required=True, default='architectural')

    category = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('institutional', 'Institutional'),
        ('industrial', 'Industrial'),
        ('infrastructure', 'Infrastructure'),
        ('heritage', 'Heritage'),
        ('eco_tourism', 'Eco-Tourism')
    ], string='Category', required=True)

    location = fields.Text(string='Project Location', required=True)
    state_id = fields.Many2one('res.country.state', string='State')
    district = fields.Char(string='District')
    pin_code = fields.Char(string='PIN Code')
    gps_coordinates = fields.Char(string='GPS Coordinates')

    stage_id = fields.Many2one('architect.project.stage', string='Stage',
                               default=lambda self: self._get_default_stage(), tracking=True)
    user_id = fields.Many2one('res.users', string='Project Manager',
                              default=lambda self: self.env.user, tracking=True)
    team_ids = fields.Many2many('res.users', string='Team Members')

    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    deadline = fields.Date(string='Deadline', tracking=True)
    completion_date = fields.Date(string='Completion Date')

    budget = fields.Monetary(string='Budget', currency_field='currency_id')
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id')
    actual_cost = fields.Monetary(string='Actual Cost', compute='_compute_actual_cost', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    progress = fields.Float(string='Progress (%)', compute='_compute_progress', store=True)
    task_count = fields.Integer(string='Task Count', compute='_compute_task_count')
    drawing_count = fields.Integer(string='Drawings', compute='_compute_drawing_count')
    dpr_count = fields.Integer(string='DPR Count', compute='_compute_dpr_count')
    compliance_count = fields.Integer(string='Compliance Items', compute='_compute_compliance_count')

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='1')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    notes = fields.Html(string='Notes')
    tags = fields.Text(string='Tags')

    tender_reference = fields.Char(string='Tender Reference')
    department = fields.Char(string='Government Department')
    approval_authority = fields.Char(string='Approval Authority')

    ai_recommendations = fields.Text(string='AI Recommendations')
    risk_analysis = fields.Text(string='Risk Analysis')
    sustainability_score = fields.Float(string='Sustainability Score')

    @api.model
    def _get_default_stage(self):
        return self.env['architect.project.stage'].search([('sequence', '=', 1)], limit=1)

    @api.depends('stage_id')
    def _compute_progress(self):
        for project in self:
            project.progress = project.stage_id.progress if project.stage_id else 0.0

    def _compute_task_count(self):
        for project in self:
            project.task_count = self.env['project.task'].search_count([
                ('architect_project_id', '=', project.id)
            ])

    def _compute_drawing_count(self):
        for project in self:
            project.drawing_count = self.env['architect.drawing'].search_count([
                ('project_id', '=', project.id)
            ])

    def _compute_dpr_count(self):
        for project in self:
            project.dpr_count = self.env['architect.dpr'].search_count([
                ('project_id', '=', project.id)
            ])

    def _compute_compliance_count(self):
        for project in self:
            project.compliance_count = self.env['architect.compliance'].search_count([
                ('project_id', '=', project.id)
            ])

    @api.depends('estimated_cost')
    def _compute_actual_cost(self):
        for project in self:
            project.actual_cost = project.estimated_cost * 0.85

    @api.model
    def create(self, vals):
        if 'code' not in vals or not vals['code']:
            vals['code'] = self.env['ir.sequence'].next_by_code('architect.project') or 'New'
        return super().create(vals)

    def action_confirm(self):
        self.state = 'confirmed'
        self.message_post(body=_("Project confirmed and ready to start."))

    def action_start(self):
        self.state = 'in_progress'
        self.message_post(body=_("Project started."))

    def action_review(self):
        self.state = 'review'
        self.message_post(body=_("Project submitted for review."))

    def action_approve(self):
        self.state = 'approved'
        self.message_post(body=_("Project approved."))

    def action_complete(self):
        self.state = 'completed'
        self.completion_date = fields.Date.today()
        self.message_post(body=_("Project completed successfully."))

    def action_cancel(self):
        self.state = 'cancelled'
        self.message_post(body=_("Project cancelled."))

    def action_view_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project Tasks'),
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [('architect_project_id', '=', self.id)],
            'context': {'default_architect_project_id': self.id}
        }

    def action_view_drawings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project Drawings'),
            'res_model': 'architect.drawing',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def action_view_dpr(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('DPR Documents'),
            'res_model': 'architect.dpr',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def action_view_compliance(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compliance Tracking'),
            'res_model': 'architect.compliance',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def generate_ai_recommendations(self):
        recommendations = [
            "Consider sustainable materials for better environmental compliance",
            "Review local building codes for this region",
            "Optimize design for energy efficiency",
            "Plan for accessibility compliance",
            "Consider cultural heritage aspects"
        ]
        self.ai_recommendations = '\n'.join([f"• {rec}" for rec in recommendations])
        return True


class ArchitectProjectStage(models.Model):
    _name = 'architect.project.stage'
    _description = 'Project Stage'
    _order = 'sequence'

    name = fields.Char(string='Stage Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    progress = fields.Float(string='Progress %', help="Progress percentage for this stage")
    fold = fields.Boolean(string='Folded in Pipeline')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True
    )
    requirements = fields.Text(string='Stage Requirements')
    deliverables = fields.Text(string='Expected Deliverables')
    requires_approval = fields.Boolean(string='Requires Approval')
    approval_users = fields.Many2many('res.users', string='Approval Users')
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


class ArchitectProjectChecklist(models.Model):
    _name = 'architect.project.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Checklist'

    name = fields.Char('Name', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('approved', 'Approved')
    ], string="Status", default='draft', tracking=True)
