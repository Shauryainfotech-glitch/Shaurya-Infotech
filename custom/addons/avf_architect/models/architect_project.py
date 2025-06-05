# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class ArchitectProject(models.Model):
    _inherit = 'project.project'
    
    is_architect_project = fields.Boolean(string='Is Architect Project', default=False)
    project_type = fields.Selection([
        ('government', 'Government Project'),
        ('private', 'Private Project'),
        ('dpr', 'DPR Project'),
        ('survey', 'Survey Project')
    ], string='Project Type')
    
    client_name = fields.Char(string='Client Name')
    project_location = fields.Text(string='Project Location')
    estimated_area = fields.Float(string='Estimated Area (sq ft)')
    estimated_budget = fields.Monetary(string='Estimated Budget')
    
    # DPR related fields
    dpr_required = fields.Boolean(string='DPR Required')
    dpr_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='DPR Status', default='not_started')
    
    # Compliance fields
    fca_compliance = fields.Boolean(string='FCA Compliance Required')
    ecotourism_compliance = fields.Boolean(string='Ecotourism Compliance')
    
    stage_id = fields.Many2one('avf.project.stage', string='Project Stage')

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
    start_date = fields.Date(string='Start Date', tracking=True)
    expected_end_date = fields.Date(string='Expected End Date')
    actual_end_date = fields.Date(string='Actual End Date')

    # Financial
    budget = fields.Monetary(string='Budget', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)

    # Status
    stage_id = fields.Many2one('architect.project.stage', string='Stage', 
                               default=lambda self: self._get_default_stage())
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

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('architect.project') or 'New'
        return super(ArchitectProject, self).create(vals)

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