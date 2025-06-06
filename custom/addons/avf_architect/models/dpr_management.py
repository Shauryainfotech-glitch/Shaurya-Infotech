
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class DPRManagement(models.Model):
    _name = 'avf.dpr.management'
    _description = 'Daily Progress Report Management'
    _rec_name = 'name'
    _order = 'report_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='DPR Name', required=True, default=lambda self: _('New'))
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    report_date = fields.Date(string='Report Date', required=True, default=fields.Date.today)
    report_number = fields.Char(string='Report Number', readonly=True)

    # Weather conditions
    weather_morning = fields.Selection([
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('stormy', 'Stormy')
    ], string='Morning Weather')
    
    weather_afternoon = fields.Selection([
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('stormy', 'Stormy')
    ], string='Afternoon Weather')

    # Work details
    work_description = fields.Text(string='Work Description', required=True)
    progress_percentage = fields.Float(string='Progress %', help="Overall progress percentage")
    
    # Resources
    labour_count = fields.Integer(string='Labour Count')
    machinery_used = fields.Text(string='Machinery Used')
    materials_used = fields.Text(string='Materials Used')

    # Issues and remarks
    issues_faced = fields.Text(string='Issues Faced')
    remarks = fields.Text(string='Remarks')
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    # Approval workflow
    submitted_by = fields.Many2one('res.users', string='Submitted By', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By')
    submission_date = fields.Datetime(string='Submission Date')
    approval_date = fields.Datetime(string='Approval Date')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('avf.dpr.management') or _('New')
            if not vals.get('report_number'):
                vals['report_number'] = self.env['ir.sequence'].next_by_code('avf.dpr.management.number') or _('DPR001')
        return super(DPRManagement, self).create(vals_list)

    def action_submit(self):
        """Submit DPR for approval"""
        self.ensure_one()
        if self.status != 'draft':
            raise ValidationError(_("Only draft reports can be submitted."))
        self.status = 'submitted'
        self.submission_date = fields.Datetime.now()
        self.message_post(body=_("DPR submitted for approval."))

    def action_approve(self):
        """Approve the DPR"""
        self.ensure_one()
        if self.status != 'submitted':
            raise ValidationError(_("Only submitted reports can be approved."))
        self.status = 'approved'
        self.approval_date = fields.Datetime.now()
        self.approved_by = self.env.user
        self.message_post(body=_("DPR approved."))

    def action_reject(self):
        """Reject the DPR"""
        self.ensure_one()
        if self.status != 'submitted':
            raise ValidationError(_("Only submitted reports can be rejected."))
        self.status = 'rejected'
        self.message_post(body=_("DPR rejected."))

class DPRActivity(models.Model):
    _name = 'avf.dpr.activity'
    _description = 'DPR Activity'
    _rec_name = 'activity_name'

    dpr_id = fields.Many2one('avf.dpr.management', string='DPR', required=True, ondelete='cascade')
    activity_name = fields.Char(string='Activity Name', required=True)
    planned_quantity = fields.Float(string='Planned Quantity')
    actual_quantity = fields.Float(string='Actual Quantity')
    unit = fields.Char(string='Unit')
    progress_percentage = fields.Float(string='Progress %', compute='_compute_progress')
    remarks = fields.Text(string='Remarks')

    @api.depends('planned_quantity', 'actual_quantity')
    def _compute_progress(self):
        for activity in self:
            if activity.planned_quantity > 0:
                activity.progress_percentage = (activity.actual_quantity / activity.planned_quantity) * 100
            else:
                activity.progress_percentage = 0.0

class DPRResource(models.Model):
    _name = 'avf.dpr.resource'
    _description = 'DPR Resource Usage'
    _rec_name = 'resource_name'

    dpr_id = fields.Many2one('avf.dpr.management', string='DPR', required=True, ondelete='cascade')
    resource_type = fields.Selection([
        ('labour', 'Labour'),
        ('machinery', 'Machinery'),
        ('material', 'Material')
    ], string='Resource Type', required=True)
    
    resource_name = fields.Char(string='Resource Name', required=True)
    quantity = fields.Float(string='Quantity')
    unit = fields.Char(string='Unit')
    cost = fields.Float(string='Cost')
    remarks = fields.Text(string='Remarks')
