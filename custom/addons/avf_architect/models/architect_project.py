# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ArchitectProject(models.Model):
    _inherit = 'project.project'
    _description = 'Architect Project Extension'

    # Project Classification
    project_category = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('institutional', 'Institutional'),
        ('infrastructure', 'Infrastructure')
    ], string='Project Category', required=True)

    project_type = fields.Selection([
        ('new_construction', 'New Construction'),
        ('renovation', 'Renovation'),
        ('restoration', 'Restoration'),
        ('extension', 'Extension')
    ], string='Project Type', required=True)

    # Government Specific Fields
    government_project = fields.Boolean(string='Government Project', default=False)
    tender_number = fields.Char(string='Tender Number')
    department = fields.Char(string='Department/Ministry')
    project_code = fields.Char(string='Project Code', required=True)

    # Location Details
    site_address = fields.Text(string='Site Address', required=True)
    city = fields.Char(string='City', required=True)
    state = fields.Char(string='State', required=True)
    pincode = fields.Char(string='PIN Code')
    gps_coordinates = fields.Char(string='GPS Coordinates')

    # Project Scope
    built_up_area = fields.Float(string='Built-up Area (Sq.Ft)', digits=(12, 2))
    plot_area = fields.Float(string='Plot Area (Sq.Ft)', digits=(12, 2))
    floors = fields.Integer(string='Number of Floors')
    basement = fields.Boolean(string='Basement', default=False)

    # Financial Information
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id')
    approved_budget = fields.Monetary(string='Approved Budget', currency_field='currency_id')
    actual_cost = fields.Monetary(string='Actual Cost', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)

    # Timeline - Using different field names to avoid conflicts
    project_start_date = fields.Date(string='Project Start Date', required=True)
    expected_completion_date = fields.Date(string='Expected Completion Date', required=True)
    actual_completion_date = fields.Date(string='Actual Completion Date')

    # Status and Progress
    project_status = fields.Selection([
        ('planning', 'Planning'),
        ('design', 'Design Phase'),
        ('approval', 'Approval Process'),
        ('construction', 'Under Construction'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled')
    ], string='Project Status', default='planning', required=True)

    progress_percentage = fields.Float(string='Progress %', compute='_compute_progress_percentage', store=True)

    # Team Information
    project_manager_id = fields.Many2one('hr.employee', string='Project Manager')
    architect_id = fields.Many2one('hr.employee', string='Lead Architect')
    team_members = fields.Many2many('hr.employee', string='Team Members')

    # Compliance and Approvals
    environmental_clearance = fields.Boolean(string='Environmental Clearance Required')
    fire_clearance = fields.Boolean(string='Fire Safety Clearance Required')
    building_permit = fields.Boolean(string='Building Permit Required')

    # Documents and Drawings
    drawing_count = fields.Integer(string='Drawings', compute='_compute_drawing_count')
    document_count = fields.Integer(string='Documents', compute='_compute_document_count')

    # AI Integration
    ai_recommendations = fields.Text(string='AI Recommendations')
    design_optimization = fields.Text(string='Design Optimization Suggestions')

    # Relations
    dpr_ids = fields.One2many('architect.dpr', 'project_id', string='DPR Reports')
    survey_ids = fields.One2many('architect.survey', 'project_id', string='Surveys')
    drawing_ids = fields.One2many('avf.drawing.management', 'project_id', string='Drawings')
    document_ids = fields.One2many('avf.document.management', 'project_id', string='Documents')

    @api.depends('project_status', 'task_ids.stage_id')
    def _compute_progress_percentage(self):
        """Compute progress based on project status and tasks"""
        for project in self:
            if project.project_status == 'planning':
                project.progress_percentage = 10.0
            elif project.project_status == 'design':
                project.progress_percentage = 30.0
            elif project.project_status == 'approval':
                project.progress_percentage = 50.0
            elif project.project_status == 'construction':
                # Calculate based on completed tasks
                if project.task_ids:
                    completed_tasks = project.task_ids.filtered(lambda t: t.stage_id.is_closed)
                    total_tasks = len(project.task_ids)
                    if total_tasks > 0:
                        task_progress = (len(completed_tasks) / total_tasks) * 100
                        project.progress_percentage = 50.0 + (task_progress * 0.4)  # 50% + up to 40% from tasks
                    else:
                        project.progress_percentage = 70.0
                else:
                    project.progress_percentage = 70.0
            elif project.project_status == 'completed':
                project.progress_percentage = 100.0
            else:
                project.progress_percentage = 0.0

    @api.depends('drawing_ids')
    def _compute_drawing_count(self):
        for project in self:
            project.drawing_count = len(project.drawing_ids)

    @api.depends('document_ids')
    def _compute_document_count(self):
        for project in self:
            project.document_count = len(project.document_ids)

    @api.constrains('project_start_date', 'expected_completion_date')
    def _check_dates(self):
        for record in self:
            if record.project_start_date and record.expected_completion_date:
                if record.project_start_date >= record.expected_completion_date:
                    raise ValidationError(_('Expected completion date must be after start date.'))

    @api.constrains('built_up_area', 'plot_area')
    def _check_areas(self):
        for record in self:
            if record.built_up_area and record.plot_area:
                if record.built_up_area > record.plot_area:
                    raise ValidationError(_('Built-up area cannot be greater than plot area.'))

    @api.model
    def create(self, vals):
        if not vals.get('project_code'):
            vals['project_code'] = self.env['ir.sequence'].next_by_code('architect.project') or '/'
        return super(ArchitectProject, self).create(vals)

    def action_view_drawings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Drawings',
            'res_model': 'avf.drawing.management',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def action_view_documents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Documents',
            'res_model': 'avf.document.management',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def generate_ai_recommendations(self):
        """Generate AI-powered project recommendations"""
        # Placeholder for AI integration
        recommendations = []

        if self.built_up_area and self.plot_area:
            far = self.built_up_area / self.plot_area
            if far > 0.8:
                recommendations.append("Consider optimizing the Floor Area Ratio (FAR) for better compliance.")

        if not self.environmental_clearance and self.built_up_area > 5000:
            recommendations.append("Environmental clearance may be required for projects above 5000 sq.ft.")

        if self.project_status == 'planning' and not self.architect_id:
            recommendations.append("Assign a lead architect to begin the design phase.")

        self.ai_recommendations = '\n'.join(recommendations) if recommendations else "No specific recommendations at this time."