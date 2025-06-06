
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class AVFDPRManagement(models.Model):
    _name = 'avf.dpr.management'
    _description = 'Daily Progress Report Management'
    _rec_name = 'name'
    _order = 'report_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='DPR Name', required=True, default=lambda self: _('New'))
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    report_number = fields.Char(string='Report Number', readonly=True)
    report_date = fields.Date(string='Report Date', required=True, default=fields.Date.today)

    # Weather Information
    weather_condition = fields.Selection([
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('stormy', 'Stormy'),
        ('foggy', 'Foggy')
    ], string='Weather Condition')
    temperature = fields.Float(string='Temperature (°C)')
    humidity = fields.Float(string='Humidity (%)')

    # Work Progress
    work_description = fields.Text(string='Work Description', required=True)
    progress_summary = fields.Text(string='Progress Summary')
    achievements = fields.Text(string='Today\'s Achievements')
    planned_activities = fields.Text(string='Planned Activities for Tomorrow')

    # Resources
    total_workers = fields.Integer(string='Total Workers')
    skilled_workers = fields.Integer(string='Skilled Workers')
    unskilled_workers = fields.Integer(string='Unskilled Workers')
    
    # Equipment and Materials
    equipment_used = fields.Text(string='Equipment Used')
    materials_consumed = fields.Text(string='Materials Consumed')
    materials_received = fields.Text(string='Materials Received')

    # Issues and Challenges
    issues_faced = fields.Text(string='Issues Faced')
    safety_incidents = fields.Text(string='Safety Incidents')
    quality_issues = fields.Text(string='Quality Issues')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    # Responsible persons
    prepared_by = fields.Many2one('res.users', string='Prepared By', default=lambda self: self.env.user)
    reviewed_by = fields.Many2one('res.users', string='Reviewed By')
    approved_by = fields.Many2one('res.users', string='Approved By')

    # Related records
    activity_ids = fields.One2many('avf.dpr.activity', 'dpr_id', string='Activities')
    resource_ids = fields.One2many('avf.dpr.resource', 'dpr_id', string='Resources')

    # Files
    photos = fields.Binary(string='Progress Photos', attachment=True)
    photos_filename = fields.Char(string='Photos Filename')
    additional_documents = fields.Binary(string='Additional Documents', attachment=True)
    documents_filename = fields.Char(string='Documents Filename')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('avf.dpr.management') or _('New')
            if not vals.get('report_number'):
                vals['report_number'] = self.env['ir.sequence'].next_by_code('avf.dpr.number') or 'DPR-001'
        return super().create(vals_list)

    def action_submit(self):
        """Submit DPR for review"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_("Only draft DPRs can be submitted."))
        self.state = 'submitted'
        self.message_post(body=_("DPR submitted for review."))

    def action_approve(self):
        """Approve DPR"""
        self.ensure_one()
        if self.state != 'submitted':
            raise ValidationError(_("Only submitted DPRs can be approved."))
        self.state = 'approved'
        self.approved_by = self.env.user
        self.message_post(body=_("DPR approved."))

    def action_reject(self):
        """Reject DPR"""
        self.ensure_one()
        if self.state != 'submitted':
            raise ValidationError(_("Only submitted DPRs can be rejected."))
        self.state = 'rejected'
        self.message_post(body=_("DPR rejected."))

class AVFDPRActivity(models.Model):
    _name = 'avf.dpr.activity'
    _description = 'DPR Activity'
    _rec_name = 'activity_name'

    dpr_id = fields.Many2one('avf.dpr.management', string='DPR', required=True, ondelete='cascade')
    activity_name = fields.Char(string='Activity Name', required=True)
    activity_type = fields.Selection([
        ('excavation', 'Excavation'),
        ('foundation', 'Foundation'),
        ('structure', 'Structure'),
        ('masonry', 'Masonry'),
        ('plastering', 'Plastering'),
        ('flooring', 'Flooring'),
        ('roofing', 'Roofing'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('finishing', 'Finishing'),
        ('other', 'Other')
    ], string='Activity Type', required=True)

    planned_quantity = fields.Float(string='Planned Quantity')
    actual_quantity = fields.Float(string='Actual Quantity')
    unit = fields.Char(string='Unit')
    progress_percentage = fields.Float(string='Progress %')

    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)

    remarks = fields.Text(string='Remarks')

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for activity in self:
            if activity.start_time and activity.end_time:
                delta = activity.end_time - activity.start_time
                activity.duration = delta.total_seconds() / 3600
            else:
                activity.duration = 0.0

class AVFDPRResource(models.Model):
    _name = 'avf.dpr.resource'
    _description = 'DPR Resource'
    _rec_name = 'resource_name'

    dpr_id = fields.Many2one('avf.dpr.management', string='DPR', required=True, ondelete='cascade')
    resource_name = fields.Char(string='Resource Name', required=True)
    resource_type = fields.Selection([
        ('manpower', 'Manpower'),
        ('equipment', 'Equipment'),
        ('material', 'Material'),
        ('vehicle', 'Vehicle')
    ], string='Resource Type', required=True)

    quantity = fields.Float(string='Quantity')
    unit = fields.Char(string='Unit')
    unit_cost = fields.Float(string='Unit Cost')
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)

    supplier_id = fields.Many2one('res.partner', string='Supplier')
    remarks = fields.Text(string='Remarks')

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for resource in self:
            resource.total_cost = resource.quantity * resource.unit_cost
