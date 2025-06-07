from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class GemBid(models.Model):
    _name = 'avgc.gem.bid'
    _description = 'GeM Bid Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'title'

    # Basic Information
    title = fields.Char('Bid Title', required=True, tracking=True)
    bid_number = fields.Char('Bid Number', required=True, copy=False,
                            default=lambda self: _('New'), tracking=True)
    description = fields.Html('Description', tracking=True)
    organization = fields.Char('Organization', required=True, tracking=True)
    
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
    
    item_category = fields.Char('Item Category', tracking=True)
    bid_type = fields.Selection([
        ('goods', 'Goods'),
        ('services', 'Services'),
        ('works', 'Works'),
    ], string='Bid Type', required=True, tracking=True)
    
    # Financial Information
    estimated_value = fields.Monetary('Estimated Value', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    unit_rate = fields.Monetary('Unit Rate', currency_field='currency_id')
    gst_rate = fields.Float('GST Rate (%)', digits=(5, 2))
    final_bid_amount = fields.Monetary('Final Bid Amount', currency_field='currency_id')
    
    # Location and Delivery
    location = fields.Char('Location', tracking=True)
    delivery_terms = fields.Text('Delivery Terms')
    delivery_date = fields.Date('Expected Delivery Date')
    delivery_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('delayed', 'Delayed'),
    ], string='Delivery Status', default='pending')
    
    # Important Dates
    deadline = fields.Date('Bid Deadline', required=True, tracking=True)
    opening_date = fields.Date('Bid Opening Date')
    award_date = fields.Date('Award Date')
    
    # Current Stage (1-14 GeM Bid Lifecycle)
    current_stage = fields.Integer('Current Stage', default=1, tracking=True)
    current_stage_name = fields.Char('Current Stage Name', compute='_compute_stage_name')
    
    # Stage Progress
    stage_ids = fields.One2many('avgc.gem.bid.stage', 'bid_id', string='Stages')
    progress_percentage = fields.Float('Progress (%)', compute='_compute_progress', digits=(5, 2))
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('submitted', 'Submitted'),
        ('under_evaluation', 'Under Evaluation'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Priority and Classification
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='medium', tracking=True)
    
    # Requirements and Specifications
    requirements = fields.Text('Requirements')
    eligibility_criteria = fields.Text('Eligibility Criteria')
    technical_qualification = fields.Text('Technical Qualification')
    
    # Search and Keywords
    search_keywords = fields.Char('Search Keywords')
    tags = fields.Char('Tags')
    
    # Compliance Requirements
    financial_document = fields.Boolean('Financial Document Required', default=False)
    emd_required = fields.Boolean('EMD Required', default=False)
    epbc_required = fields.Boolean('EPBC Required', default=False)
    mse_purchase_preference = fields.Boolean('MSE Purchase Preference', default=False)
    
    # Evaluation Method
    evaluation_method = fields.Selection([
        ('l1', 'L1 (Lowest Price)'),
        ('qcbs', 'QCBS (Quality and Cost Based)'),
        ('technical', 'Technical Evaluation'),
        ('comprehensive', 'Comprehensive Evaluation'),
    ], string='Evaluation Method', default='l1')
    
    # Contract Information
    contract_period = fields.Char('Contract Period')
    po_number = fields.Char('PO Number')
    po_received = fields.Boolean('PO Received', default=False)
    po_acceptance_date = fields.Date('PO Acceptance Date')
    
    # Invoice and Payment
    invoice_uploaded = fields.Boolean('Invoice Uploaded', default=False)
    invoice_number = fields.Char('Invoice Number')
    payment_received = fields.Boolean('Payment Received', default=False)
    payment_date = fields.Date('Payment Date')
    utr_number = fields.Char('UTR Number')
    
    # Performance and Feedback
    performance_rating = fields.Float('Performance Rating', digits=(2, 1))
    buyer_feedback = fields.Text('Buyer Feedback')
    
    # Pre-bid Query (Stage 3)
    pre_bid_query_submitted = fields.Boolean('Pre-bid Query Submitted', default=False)
    pre_bid_query_text = fields.Text('Pre-bid Query Text')
    
    # Technical Bid (Stage 5)
    technical_bid_submitted = fields.Boolean('Technical Bid Submitted', default=False)
    technical_bid_date = fields.Datetime('Technical Bid Date')
    technical_evaluation_status = fields.Selection([
        ('pending', 'Pending'),
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified'),
    ], string='Technical Evaluation Status')
    
    # Financial Bid (Stage 6)
    financial_bid_submitted = fields.Boolean('Financial Bid Submitted', default=False)
    financial_bid_date = fields.Datetime('Financial Bid Date')
    
    # Reverse Auction (Stage 8)
    reverse_auction_scheduled = fields.Boolean('Reverse Auction Scheduled', default=False)
    reverse_auction_date = fields.Datetime('Reverse Auction Date')
    reverse_auction_participated = fields.Boolean('Reverse Auction Participated', default=False)
    
    # Consignee Details
    consignee_details = fields.Text('Consignee Details')
    
    # Document Management
    document_ids = fields.One2many('avgc.gem.bid.document', 'bid_id', string='Documents')
    document_count = fields.Integer('Document Count', compute='_compute_document_count')
    
    # Statistics
    submission_count = fields.Integer('Submission Count', default=0)
    
    # Computed Fields
    is_overdue = fields.Boolean('Is Overdue', compute='_compute_is_overdue')
    days_to_deadline = fields.Integer('Days to Deadline', compute='_compute_days_to_deadline')
    
    @api.model
    def create(self, vals):
        if vals.get('bid_number', _('New')) == _('New'):
            vals['bid_number'] = self.env['ir.sequence'].next_by_code('avgc.gem.bid') or _('New')
        result = super(GemBid, self).create(vals)
        result._create_default_stages()
        return result
    
    def _create_default_stages(self):
        """Create default 14 stages for GeM Bid lifecycle"""
        stage_data = [
            (1, 'Tender Search & Identification'),
            (2, 'Bid Document Download'),
            (3, 'Pre-bid Query Submission'),
            (4, 'Bid Preparation'),
            (5, 'Technical Bid Submission'),
            (6, 'Financial Bid Submission'),
            (7, 'Bid Opening & Evaluation'),
            (8, 'Reverse Auction (if applicable)'),
            (9, 'Purchase Order Receipt'),
            (10, 'PO Acceptance'),
            (11, 'Delivery/Service Provision'),
            (12, 'Invoice Upload'),
            (13, 'Payment Processing'),
            (14, 'Performance Rating & Feedback'),
        ]
        
        for stage_number, stage_name in stage_data:
            self.env['avgc.gem.bid.stage'].create({
                'bid_id': self.id,
                'stage_number': stage_number,
                'stage_name': stage_name,
                'status': 'pending' if stage_number > 1 else 'in_progress',
            })
    
    @api.depends('current_stage')
    def _compute_stage_name(self):
        stage_names = {
            1: 'Tender Search & Identification',
            2: 'Bid Document Download',
            3: 'Pre-bid Query Submission',
            4: 'Bid Preparation',
            5: 'Technical Bid Submission',
            6: 'Financial Bid Submission',
            7: 'Bid Opening & Evaluation',
            8: 'Reverse Auction (if applicable)',
            9: 'Purchase Order Receipt',
            10: 'PO Acceptance',
            11: 'Delivery/Service Provision',
            12: 'Invoice Upload',
            13: 'Payment Processing',
            14: 'Performance Rating & Feedback',
        }
        for record in self:
            record.current_stage_name = stage_names.get(record.current_stage, 'Unknown Stage')
    
    @api.depends('current_stage')
    def _compute_progress(self):
        for record in self:
            if record.current_stage > 0:
                record.progress_percentage = (record.current_stage / 14) * 100
            else:
                record.progress_percentage = 0
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    @api.depends('deadline')
    def _compute_is_overdue(self):
        current_date = fields.Date.today()
        for record in self:
            record.is_overdue = record.deadline and record.deadline < current_date
    
    @api.depends('deadline')
    def _compute_days_to_deadline(self):
        current_date = fields.Date.today()
        for record in self:
            if record.deadline:
                delta = record.deadline - current_date
                record.days_to_deadline = delta.days
            else:
                record.days_to_deadline = 0
    
    def action_next_stage(self):
        """Move to next stage"""
        for record in self:
            if record.current_stage < 14:
                # Complete current stage
                current_stage_record = record.stage_ids.filtered(
                    lambda s: s.stage_number == record.current_stage
                )
                if current_stage_record:
                    current_stage_record.status = 'completed'
                    current_stage_record.completed_at = fields.Datetime.now()
                
                # Move to next stage
                record.current_stage += 1
                next_stage_record = record.stage_ids.filtered(
                    lambda s: s.stage_number == record.current_stage
                )
                if next_stage_record:
                    next_stage_record.status = 'in_progress'
                    next_stage_record.started_at = fields.Datetime.now()
                
                record.message_post(
                    body=_('Moved to Stage %s: %s') % (record.current_stage, record.current_stage_name)
                )
    
    def action_previous_stage(self):
        """Move to previous stage"""
        for record in self:
            if record.current_stage > 1:
                # Reset current stage
                current_stage_record = record.stage_ids.filtered(
                    lambda s: s.stage_number == record.current_stage
                )
                if current_stage_record:
                    current_stage_record.status = 'pending'
                    current_stage_record.started_at = False
                
                # Move to previous stage
                record.current_stage -= 1
                prev_stage_record = record.stage_ids.filtered(
                    lambda s: s.stage_number == record.current_stage
                )
                if prev_stage_record:
                    prev_stage_record.status = 'in_progress'
                
                record.message_post(
                    body=_('Moved back to Stage %s: %s') % (record.current_stage, record.current_stage_name)
                )
    
    def action_submit_bid(self):
        """Submit the bid"""
        for record in self:
            if record.status == 'active':
                record.status = 'submitted'
                record.submission_count += 1
                record.message_post(body=_('Bid has been submitted.'))
    
    def action_award(self):
        """Award the bid"""
        for record in self:
            if record.status == 'submitted':
                record.status = 'awarded'
                record.award_date = fields.Date.today()
                record.message_post(body=_('Bid has been awarded.'))
    
    def action_complete(self):
        """Complete the bid"""
        for record in self:
            record.status = 'completed'
            record.current_stage = 14
            # Complete all stages
            for stage in record.stage_ids:
                if stage.status != 'completed':
                    stage.status = 'completed'
                    stage.completed_at = fields.Datetime.now()
            record.message_post(body=_('Bid has been completed.'))
    
    def action_view_documents(self):
        """View bid documents"""
        return {
            'name': _('Bid Documents'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'avgc.gem.bid.document',
            'domain': [('bid_id', '=', self.id)],
            'context': {'default_bid_id': self.id},
        }
    
    def action_view_stages(self):
        """View bid stages"""
        return {
            'name': _('Bid Stages'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'avgc.gem.bid.stage',
            'domain': [('bid_id', '=', self.id)],
            'context': {'default_bid_id': self.id},
        }


class GemBidStage(models.Model):
    _name = 'avgc.gem.bid.stage'
    _description = 'GeM Bid Stage'
    _order = 'stage_number'
    
    bid_id = fields.Many2one('avgc.gem.bid', string='Bid', required=True, ondelete='cascade')
    stage_number = fields.Integer('Stage Number', required=True)
    stage_name = fields.Char('Stage Name', required=True)
    
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ], string='Status', default='pending', required=True)
    
    # Dates
    started_at = fields.Datetime('Started At')
    completed_at = fields.Datetime('Completed At')
    due_date = fields.Date('Due Date')
    
    # Assignment
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    
    # Progress and Notes
    notes = fields.Text('Notes')
    documents = fields.Text('Required Documents')
    checklist = fields.Text('Checklist')
    
    # Computed Fields
    duration_days = fields.Integer('Duration (Days)', compute='_compute_duration')
    is_overdue = fields.Boolean('Is Overdue', compute='_compute_is_overdue')
    
    @api.depends('started_at', 'completed_at')
    def _compute_duration(self):
        for record in self:
            if record.started_at and record.completed_at:
                delta = record.completed_at.date() - record.started_at.date()
                record.duration_days = delta.days
            else:
                record.duration_days = 0
    
    @api.depends('due_date', 'status')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (
                record.due_date and 
                record.due_date < today and 
                record.status not in ['completed', 'skipped']
            )
    
    def action_start(self):
        """Start the stage"""
        for record in self:
            record.status = 'in_progress'
            record.started_at = fields.Datetime.now()
            record.bid_id.current_stage = record.stage_number
    
    def action_complete(self):
        """Complete the stage"""
        for record in self:
            record.status = 'completed'
            record.completed_at = fields.Datetime.now()
            # Move bid to next stage if this is current stage
            if record.bid_id.current_stage == record.stage_number:
                record.bid_id.action_next_stage()
    
    def action_skip(self):
        """Skip the stage"""
        for record in self:
            record.status = 'skipped'
            record.completed_at = fields.Datetime.now()


class GemBidDocument(models.Model):
    _name = 'avgc.gem.bid.document'
    _description = 'GeM Bid Document'
    _inherit = ['mail.thread']
    
    name = fields.Char('Document Name', required=True)
    bid_id = fields.Many2one('avgc.gem.bid', string='Bid', required=True, ondelete='cascade')
    stage_id = fields.Many2one('avgc.gem.bid.stage', string='Related Stage')
    
    document_type = fields.Selection([
        ('tender_document', 'Tender Document'),
        ('technical_bid', 'Technical Bid'),
        ('financial_bid', 'Financial Bid'),
        ('compliance', 'Compliance Document'),
        ('experience', 'Experience Certificate'),
        ('financial_statement', 'Financial Statement'),
        ('authorization', 'Authorization Letter'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    
    file_data = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')
    file_size = fields.Integer('File Size')
    mime_type = fields.Char('MIME Type')
    
    # Document Properties
    is_mandatory = fields.Boolean('Mandatory', default=True)
    version = fields.Char('Version', default='1.0')
    
    # Status and Verification
    status = fields.Selection([
        ('draft', 'Draft'),
        ('uploaded', 'Uploaded'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft')
    
    verified_by = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Datetime('Verification Date')
    verification_notes = fields.Text('Verification Notes')
    
    # AI Analysis Results
    ocr_text = fields.Text('OCR Extracted Text')
    ai_summary = fields.Text('AI Summary')
    compliance_score = fields.Float('Compliance Score', digits=(3, 1))
    
    def action_verify(self):
        """Verify document"""
        for record in self:
            record.status = 'verified'
            record.verified_by = self.env.user
            record.verification_date = fields.Datetime.now()
            record.message_post(body=_('Document has been verified.'))
    
    def action_reject(self):
        """Reject document"""
        for record in self:
            record.status = 'rejected'
            record.message_post(body=_('Document has been rejected.'))