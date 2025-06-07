from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Tender(models.Model):
    _name = 'avgc.tender'
    _description = 'Tender Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'title'

    # Basic Information
    title = fields.Char('Tender Title', required=True, tracking=True)
    reference = fields.Char('Reference Number', required=True, copy=False, 
                           default=lambda self: _('New'), tracking=True)
    description = fields.Html('Description', tracking=True)
    
    # Categories and Classification
    category = fields.Selection([
        ('infrastructure', 'Infrastructure'),
        ('technology', 'Technology'),
        ('construction', 'Construction'),
        ('consulting', 'Consulting'),
        ('supplies', 'Supplies'),
        ('services', 'Services'),
        ('maintenance', 'Maintenance'),
    ], string='Category', required=True, tracking=True)
    
    # Financial Information
    estimated_value = fields.Monetary('Estimated Value', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    document_fees = fields.Monetary('Document Fees', currency_field='currency_id')
    emd_value = fields.Monetary('EMD Value', currency_field='currency_id')
    
    # Status and Workflow
    status = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('in_progress', 'In Progress'),
        ('evaluation', 'Under Evaluation'),
        ('awarded', 'Awarded'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Important Dates
    submission_deadline = fields.Datetime('Submission Deadline', required=True, tracking=True)
    opening_date = fields.Datetime('Opening Date', tracking=True)
    start_date = fields.Datetime('Start Date', tracking=True)
    award_date = fields.Datetime('Award Date', tracking=True)
    
    # Location and Organization
    location = fields.Char('Location', tracking=True)
    department = fields.Char('Department', tracking=True)
    organization_name = fields.Char('Organization Name', tracking=True)
    ownership = fields.Selection([
        ('central_govt', 'Central Government'),
        ('state_govt', 'State Government'),
        ('private', 'Private'),
        ('psu', 'Public Sector Undertaking'),
    ], string='Ownership', tracking=True)
    
    # Tender Type and Classification
    tender_type = fields.Selection([
        ('open', 'Open Tender'),
        ('limited', 'Limited Tender'),
        ('single', 'Single Source'),
        ('gem', 'GeM Portal'),
        ('reverse_auction', 'Reverse Auction'),
    ], string='Tender Type', default='open', tracking=True)
    
    # Relationships
    created_by = fields.Many2one('res.users', string='Created By', 
                                default=lambda self: self.env.user, tracking=True)
    assigned_to = fields.Many2one('res.users', string='Assigned To', tracking=True)
    vendor_ids = fields.Many2many('avgc.vendor', string='Participating Vendors')
    
    # Document Management
    document_ids = fields.One2many('avgc.tender.document', 'tender_id', string='Documents')
    document_count = fields.Integer('Document Count', compute='_compute_document_count')
    
    # Submissions
    submission_ids = fields.One2many('avgc.tender.submission', 'tender_id', string='Submissions')
    submission_count = fields.Integer('Submission Count', compute='_compute_submission_count')
    
    # AI Analysis
    ai_analysis_ids = fields.One2many('avgc.ai.analysis', 'tender_id', string='AI Analysis')
    ai_analysis_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='AI Analysis Status', default='pending')
    
    # Compliance and Security
    compliance_score = fields.Float('Compliance Score', digits=(3, 1))
    security_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Security Level', default='medium')
    
    # Blockchain Integration
    blockchain_hash = fields.Char('Blockchain Hash', readonly=True)
    is_blockchain_verified = fields.Boolean('Blockchain Verified', default=False)
    
    # Computed Fields
    is_overdue = fields.Boolean('Is Overdue', compute='_compute_is_overdue')
    days_to_deadline = fields.Integer('Days to Deadline', compute='_compute_days_to_deadline')
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('avgc.tender') or _('New')
        return super(Tender, self).create(vals)
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    @api.depends('submission_ids')
    def _compute_submission_count(self):
        for record in self:
            record.submission_count = len(record.submission_ids)
    
    @api.depends('submission_deadline')
    def _compute_is_overdue(self):
        current_date = fields.Datetime.now()
        for record in self:
            record.is_overdue = record.submission_deadline and record.submission_deadline < current_date
    
    @api.depends('submission_deadline')
    def _compute_days_to_deadline(self):
        current_date = fields.Datetime.now()
        for record in self:
            if record.submission_deadline:
                delta = record.submission_deadline - current_date
                record.days_to_deadline = delta.days
            else:
                record.days_to_deadline = 0
    
    @api.constrains('submission_deadline', 'opening_date')
    def _check_dates(self):
        for record in self:
            if record.opening_date and record.submission_deadline:
                if record.opening_date <= record.submission_deadline:
                    raise ValidationError(_('Opening date must be after submission deadline.'))
    
    def action_publish(self):
        """Publish the tender"""
        for record in self:
            if record.status == 'draft':
                record.status = 'published'
                record.message_post(body=_('Tender has been published.'))
    
    def action_start_evaluation(self):
        """Start tender evaluation process"""
        for record in self:
            if record.status == 'published':
                record.status = 'evaluation'
                record.message_post(body=_('Tender evaluation has started.'))
    
    def action_award(self):
        """Award the tender"""
        for record in self:
            if record.status == 'evaluation':
                record.status = 'awarded'
                record.award_date = fields.Datetime.now()
                record.message_post(body=_('Tender has been awarded.'))
    
    def action_close(self):
        """Close the tender"""
        for record in self:
            record.status = 'closed'
            record.message_post(body=_('Tender has been closed.'))
    
    def action_cancel(self):
        """Cancel the tender"""
        for record in self:
            record.status = 'cancelled'
            record.message_post(body=_('Tender has been cancelled.'))
    
    def action_view_documents(self):
        """View tender documents"""
        return {
            'name': _('Tender Documents'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'avgc.tender.document',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
        }
    
    def action_view_submissions(self):
        """View tender submissions"""
        return {
            'name': _('Tender Submissions'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'avgc.tender.submission',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
        }
    
    def action_ai_analysis(self):
        """Trigger AI analysis of tender documents"""
        return {
            'name': _('AI Document Analysis'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'avgc.ai.analysis.wizard',
            'target': 'new',
            'context': {'default_tender_id': self.id},
        }


class TenderDocument(models.Model):
    _name = 'avgc.tender.document'
    _description = 'Tender Document'
    _inherit = ['mail.thread']
    
    name = fields.Char('Document Name', required=True)
    tender_id = fields.Many2one('avgc.tender', string='Tender', required=True, ondelete='cascade')
    document_type = fields.Selection([
        ('specification', 'Technical Specification'),
        ('terms', 'Terms and Conditions'),
        ('drawings', 'Drawings'),
        ('financial', 'Financial Documents'),
        ('legal', 'Legal Documents'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    
    file_data = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')
    file_size = fields.Integer('File Size')
    mime_type = fields.Char('MIME Type')
    
    is_mandatory = fields.Boolean('Mandatory Document', default=True)
    version = fields.Char('Version', default='1.0')
    
    # AI Analysis Results
    ocr_text = fields.Text('OCR Extracted Text')
    ai_summary = fields.Text('AI Summary')
    compliance_score = fields.Float('Compliance Score', digits=(3, 1))
    analysis_status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Analysis Status', default='pending')


class TenderSubmission(models.Model):
    _name = 'avgc.tender.submission'
    _description = 'Tender Submission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Submission Reference', required=True, copy=False,
                      default=lambda self: _('New'))
    tender_id = fields.Many2one('avgc.tender', string='Tender', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True)
    
    # Financial Information
    quoted_amount = fields.Monetary('Quoted Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    
    # Technical Information
    technical_score = fields.Float('Technical Score', digits=(3, 1))
    financial_score = fields.Float('Financial Score', digits=(3, 1))
    total_score = fields.Float('Total Score', compute='_compute_total_score', digits=(3, 1))
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified'),
        ('awarded', 'Awarded'),
    ], string='Status', default='draft', tracking=True)
    
    # Dates
    submission_date = fields.Datetime('Submission Date', default=fields.Datetime.now)
    evaluation_date = fields.Datetime('Evaluation Date')
    
    # Documents
    document_ids = fields.One2many('avgc.submission.document', 'submission_id', string='Documents')
    
    # Evaluation
    evaluator_id = fields.Many2one('res.users', string='Evaluator')
    evaluation_notes = fields.Text('Evaluation Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('avgc.tender.submission') or _('New')
        return super(TenderSubmission, self).create(vals)
    
    @api.depends('technical_score', 'financial_score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = (record.technical_score + record.financial_score) / 2


class SubmissionDocument(models.Model):
    _name = 'avgc.submission.document'
    _description = 'Submission Document'
    
    name = fields.Char('Document Name', required=True)
    submission_id = fields.Many2one('avgc.tender.submission', string='Submission', 
                                   required=True, ondelete='cascade')
    document_type = fields.Selection([
        ('technical', 'Technical Proposal'),
        ('financial', 'Financial Proposal'),
        ('compliance', 'Compliance Certificate'),
        ('experience', 'Experience Certificate'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    
    file_data = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')
    file_size = fields.Integer('File Size')
    
    is_verified = fields.Boolean('Verified', default=False)
    verification_notes = fields.Text('Verification Notes')