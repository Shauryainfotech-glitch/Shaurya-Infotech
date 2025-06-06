# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ArchitectProject(models.Model):
    _inherit = 'project.project'
    _description = 'Extended Project for AVF Architect'

    # Basic project information
    project_type = fields.Selection(selection_add=[
        ('ecotourism', 'Ecotourism')
    ], ondelete={'ecotourism': 'set default'})

    project_category = fields.Selection([
        ('government', 'Government Project'),
        ('private', 'Private Project'),
        ('institutional', 'Institutional Project'),
        ('commercial', 'Commercial Project'),
        ('residential', 'Residential Project')
    ], string='Project Category', default='government')

    project_status = fields.Selection([
        ('planning', 'Planning'),
        ('design', 'Design Phase'),
        ('approval', 'Approval Phase'),
        ('construction', 'Construction'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled')
    ], string='Project Status', default='planning', tracking=True)

    project_code = fields.Char(string='Project Code', copy=False)

    # Location Details
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    site_address = fields.Text(string='Site Address')

    # Project Timeline - use existing date_start from project.project
    end_date = fields.Date(string='End Date', tracking=True)
    project_start_date = fields.Date(string='Project Start Date', related='date_start', store=True, readonly=False)
    expected_completion_date = fields.Date(string='Expected Completion Date')
    actual_completion_date = fields.Date(string='Actual Completion Date')

    # Client and location information
    client_name = fields.Char(string='Client Name')
    client_contact = fields.Char(string='Client Contact')
    client_email = fields.Char(string='Client Email')
    project_location = fields.Text(string='Project Location')
    site_area = fields.Float(string='Site Area (sq ft)')
    built_up_area = fields.Float(string='Built-up Area (sq ft)')

    # Budget and financial tracking
    estimated_budget = fields.Monetary(string='Estimated Budget', currency_field='currency_id')
    approved_budget = fields.Monetary(string='Approved Budget', currency_field='currency_id')
    actual_cost = fields.Monetary(string='Actual Cost', currency_field='currency_id', compute='_compute_actual_cost')
    budget_variance = fields.Monetary(string='Budget Variance', compute='_compute_actual_cost', store=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Progress tracking
    progress_percentage = fields.Float(string='Progress %', compute='_compute_progress_percentage', store=True)

    # Government project specific fields
    is_government_project = fields.Boolean(string='Government Project', default=False)
    tender_number = fields.Char(string='Tender Number')
    contract_value = fields.Monetary(string='Contract Value', currency_field='currency_id')
    project_authority = fields.Char(string='Project Authority')

    # Compliance and Documentation
    compliance_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Compliance Status', default='pending')

    # DPR and compliance
    dpr_required = fields.Boolean(string='DPR Required', default=False)
    dpr_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved')
    ], string='DPR Status', default='not_started')

    fca_required = fields.Boolean(string='FCA Clearance Required', default=False)
    environmental_clearance = fields.Boolean(string='Environmental Clearance Required', default=False)

    # Related records
    architect_drawing_ids = fields.One2many('avf.drawing.management', 'project_id', string='Architect Drawings')
    dpr_ids = fields.One2many('avf.dpr.management', 'project_id', string='Daily Progress Reports')
    survey_ids = fields.One2many('avf.survey.management', 'project_id', string='Survey Records')
    compliance_ids = fields.One2many('avf.compliance.tracking', 'project_id', string='Compliance Records')

    # Computed fields
    architect_drawing_count = fields.Integer(string='Architect Drawings Count', compute='_compute_architect_drawing_count')
    dpr_count = fields.Integer(string='DPR Count', compute='_compute_dpr_count')
    survey_count = fields.Integer(string='Survey Count', compute='_compute_survey_count')
    compliance_count = fields.Integer(string='Compliance Count', compute='_compute_compliance_count')

    @api.depends('task_ids', 'task_ids.stage_id')
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
                    completed_tasks = project.task_ids.filtered(lambda t: t.stage_id.is_closed if t.stage_id else False)
                    total_tasks = len(project.task_ids)
                    if total_tasks > 0:
                        task_progress = (len(completed_tasks) / total_tasks) * 50
                        project.progress_percentage = 50.0 + task_progress
                    else:
                        project.progress_percentage = 50.0
                else:
                    project.progress_percentage = 50.0
            elif project.project_status == 'completed':
                project.progress_percentage = 100.0
            else:
                project.progress_percentage = 0.0

    @api.depends('task_ids', 'task_ids.allocated_hours')
    def _compute_actual_cost(self):
        """Compute actual cost based on timesheet entries"""
        for project in self:
            total_cost = 0.0
            for task in project.task_ids:
                for timesheet in task.timesheet_ids:
                    if timesheet.employee_id and timesheet.employee_id.hourly_cost:
                        total_cost += timesheet.unit_amount * timesheet.employee_id.hourly_cost
                    else:
                        # Default hourly cost if not set
                        total_cost += timesheet.unit_amount * 50.0
            project.actual_cost = total_cost
            project.budget_variance = project.estimated_budget - project.actual_cost

    def _compute_architect_drawing_count(self):
        for project in self:
            project.architect_drawing_count = len(project.architect_drawing_ids)

    def _compute_dpr_count(self):
        for project in self:
            project.dpr_count = len(project.dpr_ids)

    def _compute_survey_count(self):
        for project in self:
            project.survey_count = len(project.survey_ids)

    def _compute_compliance_count(self):
        for project in self:
            project.compliance_count = len(project.compliance_ids)

    @api.constrains('date_start', 'end_date')
    def _check_project_dates(self):
        for project in self:
            if project.date_start and project.end_date and project.date_start > project.end_date:
                raise ValidationError(_("End date cannot be earlier than start date."))

    @api.constrains('site_area', 'built_up_area')
    def _check_areas(self):
        for project in self:
            if project.site_area and project.site_area < 0:
                raise ValidationError(_("Site area cannot be negative."))
            if project.built_up_area and project.built_up_area < 0:
                raise ValidationError(_("Built-up area cannot be negative."))
            if project.built_up_area and project.site_area and project.built_up_area > project.site_area:
                raise ValidationError(_("Built-up area cannot exceed site area."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('project_code'):
                vals['project_code'] = self.env['ir.sequence'].next_by_code('architect.project') or 'ARCH-001'
        return super().create(vals_list)

    def action_start_project(self):
        """Start the project"""
        self.ensure_one()
        self.project_status = 'design'
        self.message_post(body=_("Project started and moved to design phase."))

    def action_submit_for_approval(self):
        """Submit project for approval"""
        self.ensure_one()
        if self.project_status != 'design':
            raise ValidationError(_("Project must be in design phase to submit for approval."))
        self.project_status = 'approval'
        self.message_post(body=_("Project submitted for approval."))

    def action_approve_project(self):
        """Approve the project"""
        self.ensure_one()
        if self.project_status != 'approval':
            raise ValidationError(_("Project must be in approval phase to approve."))
        self.project_status = 'construction'
        self.message_post(body=_("Project approved and moved to construction phase."))

    def action_complete_project(self):
        """Complete the project"""
        self.ensure_one()
        self.project_status = 'completed'
        self.end_date = fields.Date.today()
        self.message_post(body=_("Project completed successfully."))

    def action_put_on_hold(self):
        """Put project on hold"""
        self.ensure_one()
        self.project_status = 'on_hold'
        self.message_post(body=_("Project put on hold."))

    def action_view_drawings(self):
        """View project drawings"""
        self.ensure_one()
        return {
            'name': _('Architect Drawings'),
            'type': 'ir.actions.act_window',
            'res_model': 'avf.drawing.management',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_view_dpr(self):
        """View DPR records"""
        self.ensure_one()
        return {
            'name': _('DPR Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'avf.dpr.management',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_generate_project_report(self):
        """Generate comprehensive project report"""
        return self.env.ref('avf_architect.report_project_summary').report_action(self)

    def action_ai_recommendations(self):
        """Get AI recommendations for the project"""
        return {
            'name': _('AI Recommendations'),
            'type': 'ir.actions.act_window',
            'res_model': 'avf.ai.assistant',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                'default_recommendation_type': 'project_optimization'
            },
        }