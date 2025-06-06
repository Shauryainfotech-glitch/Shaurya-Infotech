# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class AvfComplianceTracking(models.Model):
    _name = 'avf.compliance.tracking'
    _description = 'Compliance Tracking for Architectural Projects'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'compliance_date desc'

    name = fields.Char(string='Compliance Reference', required=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    compliance_type_id = fields.Many2one('avf.compliance.type', string='Compliance Type', required=True)

    # Compliance details
    compliance_date = fields.Date(string='Compliance Date', required=True, default=fields.Date.today)
    due_date = fields.Date(string='Due Date')
    description = fields.Text(string='Description')

    # Status
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('expired', 'Expired')
    ], string='Status', default='pending', tracking=True)

    # Authority details
    authority_name = fields.Char(string='Authority Name')
    reference_number = fields.Char(string='Reference Number')
    inspector_name = fields.Char(string='Inspector Name')

    # Documents
    attachment_ids = fields.Many2many('ir.attachment', string='Supporting Documents')
    certificate_attachment = fields.Many2one('ir.attachment', string='Compliance Certificate')

    # Additional fields
    remarks = fields.Text(string='Remarks')
    compliance_score = fields.Float(string='Compliance Score (%)', default=0.0)

    @api.constrains('compliance_score')
    def _check_compliance_score(self):
        for record in self:
            if not 0 <= record.compliance_score <= 100:
                raise ValidationError(_('Compliance score must be between 0 and 100.'))

    def action_mark_compliant(self):
        """Mark compliance as compliant"""
        self.state = 'compliant'
        self.compliance_score = 100.0

    def action_mark_non_compliant(self):
        """Mark compliance as non-compliant"""
        self.state = 'non_compliant'


class AvfComplianceType(models.Model):
    _name = 'avf.compliance.type'
    _description = 'Compliance Types'
    _order = 'name'

    name = fields.Char(string='Compliance Type', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    # Category
    category = fields.Selection([
        ('building_code', 'Building Code'),
        ('environmental', 'Environmental'),
        ('safety', 'Safety'),
        ('accessibility', 'Accessibility'),
        ('fire_safety', 'Fire Safety'),
        ('structural', 'Structural'),
        ('planning', 'Planning Permission')
    ], string='Category', required=True)

    # Requirements
    mandatory = fields.Boolean(string='Mandatory', default=True)
    renewal_required = fields.Boolean(string='Renewal Required')
    renewal_period_months = fields.Integer(string='Renewal Period (Months)')

    # Authority
    authority_name = fields.Char(string='Governing Authority')
    contact_details = fields.Text(string='Contact Details')


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Add compliance tracking to standard project model
    compliance_ids = fields.One2many('avf.compliance.tracking', 'project_id', string='Compliance Records')