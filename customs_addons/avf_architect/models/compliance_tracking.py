
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ArchitectCompliance(models.Model):
    _name = 'architect.compliance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Compliance Tracking'
    _order = 'priority desc, deadline'

    name = fields.Char(string='Compliance Item', required=True, tracking=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    is_overdue = fields.Boolean(string='Overdue', compute='_compute_is_overdue', store=True)

    # Compliance Type
    compliance_type_id = fields.Many2one('architect.compliance.type', string='Compliance Type', required=True)
    category = fields.Selection([
        ('environmental', 'Environmental'),
        ('safety', 'Safety & Security'),
        ('building_code', 'Building Code'),
        ('fire_safety', 'Fire Safety'),
        ('accessibility', 'Accessibility'),
        ('heritage', 'Heritage Conservation'),
        ('forest', 'Forest Conservation'),
        ('pollution', 'Pollution Control'),
        ('waste', 'Waste Management'),
        ('energy', 'Energy Efficiency'),
        ('water', 'Water Conservation'),
        ('structural', 'Structural'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('hvac', 'HVAC'),
        ('other', 'Other')
    ], string='Category', required=True)
    
    # Compliance Details
    description = fields.Text(string='Description')
    regulatory_reference = fields.Char(string='Regulatory Reference')
    authority = fields.Char(string='Regulatory Authority')
    
    # Status and Timeline
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('not_applicable', 'Not Applicable')
    ], string='Status', default='pending', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1', tracking=True)
    
    # Dates
    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    deadline = fields.Date(string='Deadline', required=True, tracking=True)
    submission_date = fields.Date(string='Submission Date')
    approval_date = fields.Date(string='Approval Date')
    expiry_date = fields.Date(string='Expiry Date')
    
    # Assignment
    responsible_user_id = fields.Many2one('res.users', string='Responsible Person', 
                                         default=lambda self: self.env.user)
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    
    # Progress and Documentation
    progress = fields.Float(string='Progress (%)', default=0.0)
    notes = fields.Html(string='Notes')
    requirements = fields.Html(string='Requirements')
    submission_details = fields.Html(string='Submission Details')
    
    # Documents
    document_count = fields.Integer(string='Documents', compute='_compute_document_count')
    
    # Checklist
    checklist_ids = fields.One2many('architect.compliance.checklist', 'compliance_id', string='Checklist Items')
    checklist_progress = fields.Float(string='Checklist Progress (%)', compute='_compute_checklist_progress')
    
    # Alerts and Notifications
    alert_days_before = fields.Integer(string='Alert Days Before Deadline', default=7)

    days_to_deadline = fields.Integer(string='Days to Deadline', compute='_compute_days_to_deadline')
    
    # Cost and Resources
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id')
    actual_cost = fields.Monetary(string='Actual Cost', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    # FCA Specific Fields
    forest_clearance_required = fields.Boolean(string='Forest Clearance Required')
    forest_area = fields.Float(string='Forest Area (in hectares)')
    compensatory_afforestation = fields.Float(string='Compensatory Afforestation (in hectares)')
    net_present_value = fields.Monetary(string='Net Present Value', currency_field='currency_id')
    
    # PARIVESH Integration
    parivesh_proposal_id = fields.Char(string='PARIVESH Proposal ID')
    parivesh_status = fields.Selection([
        ('not_submitted', 'Not Submitted'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('clarification_sought', 'Clarification Sought'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='PARIVESH Status', default='not_submitted')
    
    # Environmental Impact
    environmental_impact_high = fields.Boolean(string='High Environmental Impact')
    eia_required = fields.Boolean(string='EIA Required')
    public_hearing_required = fields.Boolean(string='Public Hearing Required')
    
    # Biodiversity
    biodiversity_assessment = fields.Html(string='Biodiversity Assessment')
    wildlife_impact = fields.Html(string='Wildlife Impact Assessment')
    mitigation_measures = fields.Html(string='Mitigation Measures')
    
    @api.depends('checklist_ids.completed')
    def _compute_checklist_progress(self):
        for compliance in self:
            total_items = len(compliance.checklist_ids)
            if total_items:
                completed_items = len(compliance.checklist_ids.filtered('completed'))
                compliance.checklist_progress = (completed_items / total_items) * 100
            else:
                compliance.checklist_progress = 0.0
    
    @api.depends('deadline')
    def _compute_overdue(self):
        today = fields.Date.today()
        for compliance in self:
            compliance.is_overdue = compliance.deadline and compliance.deadline < today and compliance.state not in ['approved', 'not_applicable']
    
    @api.depends('deadline')
    def _compute_days_to_deadline(self):
        today = fields.Date.today()
        for compliance in self:
            if compliance.deadline:
                delta = compliance.deadline - today
                compliance.days_to_deadline = delta.days
            else:
                compliance.days_to_deadline = 0
    
    def _compute_document_count(self):
        for compliance in self:
            compliance.document_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'architect.compliance'),
                ('res_id', '=', compliance.id)
            ])
    
    @api.model
    def create(self, vals):
        # Auto-create checklist based on compliance type
        result = super().create(vals)
        if result.compliance_type_id and result.compliance_type_id.checklist_template_ids:
            for template_item in result.compliance_type_id.checklist_template_ids:
                self.env['architect.compliance.checklist'].create({
                    'compliance_id': result.id,
                    'name': template_item.name,
                    'description': template_item.description,
                    'sequence': template_item.sequence,
                    'is_mandatory': template_item.is_mandatory
                })
        return result
    
    def action_start_compliance(self):
        self.state = 'in_progress'
        self.start_date = fields.Date.today()
        self.message_post(body=_("Compliance process started."))
    
    def action_submit_for_approval(self):
        if self.checklist_progress < 100:
            raise ValidationError(_("Please complete all mandatory checklist items before submission."))
        self.state = 'submitted'
        self.submission_date = fields.Date.today()
        self.message_post(body=_("Submitted for regulatory approval."))
    
    def action_approve(self):
        self.state = 'approved'
        self.approval_date = fields.Date.today()
        self.progress = 100.0
        self.message_post(body=_("Compliance approved."))
    
    def action_reject(self):
        self.state = 'rejected'
        self.message_post(body=_("Compliance rejected. Please review and resubmit."))
    
    def action_mark_not_applicable(self):
        self.state = 'not_applicable'
        self.message_post(body=_("Marked as not applicable."))
    
    def action_generate_compliance_report(self):
        return self.env.ref('avf_architect.report_compliance_status').report_action(self)
    
    def action_parivesh_integration(self):
        # Placeholder for PARIVESH portal integration
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://parivesh.nic.in/',
            'target': 'new',
        }

    @api.depends('deadline')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.is_overdue = bool(record.deadline and record.deadline < today)


class ArchitectComplianceType(models.Model):
    _name = 'architect.compliance.type'
    _description = 'Compliance Type'
    _order = 'sequence, name'

    name = fields.Char(string='Compliance Type', required=True)
    #code = fields.Char(string='Code', required=True)
    code = fields.Char(
        string='Compliance Code',
        required=True,
        copy=False,
        readonly=True,
        tracking=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('architect.compliance.type') or 'new'
    )
    description = fields.Text(string='Description')
    category = fields.Selection([
        ('environmental', 'Environmental'),
        ('safety', 'Safety & Security'),
        ('building_code', 'Building Code'),
        ('heritage', 'Heritage Conservation'),
        ('other', 'Other')
    ], string='Category', required=True)
    
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Regulatory Information
    regulatory_authority = fields.Char(string='Regulatory Authority')
    regulatory_reference = fields.Char(string='Regulatory Reference')
    validity_period = fields.Integer(string='Validity Period (Days)')
    
    # Requirements
    requirements = fields.Html(string='Requirements')
    submission_process = fields.Html(string='Submission Process')
    required_documents = fields.Html(string='Required Documents')
    
    # Checklist Template
    checklist_template_ids = fields.One2many('architect.compliance.checklist.template', 'compliance_type_id', 
                                           string='Checklist Template')
    
    # Applicability
    project_types = fields.Selection([
        ('all', 'All Projects'),
        ('government', 'Government Projects Only'),
        ('private', 'Private Projects Only'),
        ('specific', 'Specific Project Types')
    ], string='Applicable To', default='all')
    
    # Cost and Timeline
    typical_duration = fields.Integer(string='Typical Duration (Days)')
    typical_cost = fields.Monetary(
        string='Typical Cost',
        currency_field='currency_id'  # Link it to the currency_id field
    )
    # currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
@api.model
def _get_inr_currency(self):
    """Get INR currency, create if not exists"""
    inr = self.env.ref('base.INR', raise_if_not_found=False)
    if not inr:
        # If INR doesn't exist, create it
        inr = self.env['res.currency'].create({
            'name': 'INR',
            'symbol': '₹',
            'position': 'before',
            'decimal_places': 2,
            'active': True,
            'rounding': 0.01
        })
    return inr.id

currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

class ArchitectComplianceChecklist(models.Model):
    _name = 'architect.compliance.checklist'
    _description = 'Compliance Checklist'
    _order = 'sequence, name'

    name = fields.Char(string='Checklist Item', required=True)
    compliance_id = fields.Many2one('architect.compliance', string='Compliance', required=True, ondelete='cascade')
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    
    completed = fields.Boolean(string='Completed')
    completion_date = fields.Date(string='Completion Date')
    completed_by = fields.Many2one('res.users', string='Completed By')
    
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
    notes = fields.Text(string='Notes')
    
    # Documents
    document_required = fields.Boolean(string='Document Required')
    document_ids = fields.Many2many('ir.attachment', string='Documents')
    
    @api.onchange('completed')
    def _onchange_completed(self):
        if self.completed:
            self.completion_date = fields.Date.today()
            self.completed_by = self.env.user
        else:
            self.completion_date = False
            self.completed_by = False



class ArchitectComplianceChecklistTemplate(models.Model):
    _name = 'architect.compliance.checklist.template'
    _description = 'Compliance Checklist Template'
    _order = 'sequence, name'

    name = fields.Char(string='Checklist Item', required=True)
    compliance_type_id = fields.Many2one('architect.compliance.type', string='Compliance Type', 
                                       required=True, ondelete='cascade')
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
    document_required = fields.Boolean(string='Document Required')
    
    # AI Enhancement
    ai_checkable = fields.Boolean(string='AI Can Verify')
    ai_verification_criteria = fields.Text(string='AI Verification Criteria')
