from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Vendor(models.Model):
    _name = 'avgc.vendor'
    _description = 'Vendor Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char('Vendor Name', required=True, tracking=True)
    code = fields.Char('Vendor Code', required=True, copy=False,
                      default=lambda self: _('New'), tracking=True)
    
    # Contact Information
    email = fields.Char('Email', tracking=True)
    phone = fields.Char('Phone', tracking=True)
    mobile = fields.Char('Mobile', tracking=True)
    website = fields.Char('Website', tracking=True)
    
    # Address Information
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char('ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    
    # Business Information
    registration_number = fields.Char('Registration Number', tracking=True)
    pan_number = fields.Char('PAN Number', tracking=True)
    gst_number = fields.Char('GST Number', tracking=True)
    license_number = fields.Char('License Number', tracking=True)
    
    # Classification
    vendor_type = fields.Selection([
        ('manufacturer', 'Manufacturer'),
        ('distributor', 'Distributor'),
        ('service_provider', 'Service Provider'),
        ('contractor', 'Contractor'),
        ('consultant', 'Consultant'),
    ], string='Vendor Type', required=True, tracking=True)
    
    category_ids = fields.Many2many('avgc.vendor.category', string='Categories')
    
    # Financial Information
    annual_turnover = fields.Monetary('Annual Turnover', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    credit_limit = fields.Monetary('Credit Limit', currency_field='currency_id')
    payment_terms = fields.Char('Payment Terms')
    
    # Status and Approval
    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
        ('blacklisted', 'Blacklisted'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    approval_date = fields.Date('Approval Date', tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By', tracking=True)
    
    # Performance Metrics
    performance_rating = fields.Float('Performance Rating', digits=(2, 1), 
                                    help='Rating out of 5.0')
    quality_rating = fields.Float('Quality Rating', digits=(2, 1))
    delivery_rating = fields.Float('Delivery Rating', digits=(2, 1))
    service_rating = fields.Float('Service Rating', digits=(2, 1))
    
    # Compliance and Certifications
    is_msme = fields.Boolean('MSME Registered', default=False)
    is_iso_certified = fields.Boolean('ISO Certified', default=False)
    iso_certificate_number = fields.Char('ISO Certificate Number')
    iso_expiry_date = fields.Date('ISO Expiry Date')
    
    # Additional Certifications
    certification_ids = fields.One2many('avgc.vendor.certification', 'vendor_id', 
                                       string='Certifications')
    
    # Document Management
    document_ids = fields.One2many('avgc.vendor.document', 'vendor_id', string='Documents')
    document_count = fields.Integer('Document Count', compute='_compute_document_count')
    
    # Tender Participation
    tender_ids = fields.Many2many('avgc.tender', string='Participated Tenders')
    submission_ids = fields.One2many('avgc.tender.submission', 'vendor_id', 
                                    string='Tender Submissions')
    
    # Statistics
    total_tenders = fields.Integer('Total Tenders', compute='_compute_tender_stats')
    won_tenders = fields.Integer('Won Tenders', compute='_compute_tender_stats')
    success_rate = fields.Float('Success Rate (%)', compute='_compute_tender_stats', digits=(5, 2))
    
    # Contact Person
    contact_person = fields.Char('Contact Person', tracking=True)
    contact_designation = fields.Char('Contact Designation')
    contact_email = fields.Char('Contact Email')
    contact_phone = fields.Char('Contact Phone')
    
    # Bank Details
    bank_name = fields.Char('Bank Name')
    bank_account_number = fields.Char('Bank Account Number')
    bank_ifsc = fields.Char('IFSC Code')
    bank_branch = fields.Char('Bank Branch')
    
    # Internal Notes
    internal_notes = fields.Text('Internal Notes')
    blacklist_reason = fields.Text('Blacklist Reason')
    
    # Computed Fields
    is_active = fields.Boolean('Active', default=True)
    
    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('avgc.vendor') or _('New')
        return super(Vendor, self).create(vals)
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    @api.depends('submission_ids')
    def _compute_tender_stats(self):
        for record in self:
            submissions = record.submission_ids
            record.total_tenders = len(submissions)
            record.won_tenders = len(submissions.filtered(lambda s: s.status == 'awarded'))
            if record.total_tenders > 0:
                record.success_rate = (record.won_tenders / record.total_tenders) * 100
            else:
                record.success_rate = 0.0
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError(_('Please enter a valid email address.'))
    
    @api.constrains('performance_rating', 'quality_rating', 'delivery_rating', 'service_rating')
    def _check_ratings(self):
        for record in self:
            ratings = [record.performance_rating, record.quality_rating, 
                      record.delivery_rating, record.service_rating]
            for rating in ratings:
                if rating and (rating < 0 or rating > 5):
                    raise ValidationError(_('Ratings must be between 0 and 5.'))
    
    def action_approve(self):
        """Approve vendor"""
        for record in self:
            if record.status == 'pending_approval':
                record.status = 'approved'
                record.approval_date = fields.Date.today()
                record.approved_by = self.env.user
                record.message_post(body=_('Vendor has been approved.'))
    
    def action_suspend(self):
        """Suspend vendor"""
        for record in self:
            record.status = 'suspended'
            record.message_post(body=_('Vendor has been suspended.'))
    
    def action_blacklist(self):
        """Blacklist vendor"""
        return {
            'name': _('Blacklist Vendor'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'avgc.vendor.blacklist.wizard',
            'target': 'new',
            'context': {'default_vendor_id': self.id},
        }
    
    def action_view_documents(self):
        """View vendor documents"""
        return {
            'name': _('Vendor Documents'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'avgc.vendor.document',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id},
        }
    
    def action_view_tenders(self):
        """View vendor tender participation"""
        return {
            'name': _('Tender Participation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'avgc.tender.submission',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id},
        }


class VendorCategory(models.Model):
    _name = 'avgc.vendor.category'
    _description = 'Vendor Category'
    _order = 'name'
    
    name = fields.Char('Category Name', required=True)
    code = fields.Char('Category Code', required=True)
    description = fields.Text('Description')
    parent_id = fields.Many2one('avgc.vendor.category', string='Parent Category')
    child_ids = fields.One2many('avgc.vendor.category', 'parent_id', string='Child Categories')
    
    vendor_ids = fields.Many2many('avgc.vendor', string='Vendors')
    vendor_count = fields.Integer('Vendor Count', compute='_compute_vendor_count')
    
    @api.depends('vendor_ids')
    def _compute_vendor_count(self):
        for record in self:
            record.vendor_count = len(record.vendor_ids)


class VendorCertification(models.Model):
    _name = 'avgc.vendor.certification'
    _description = 'Vendor Certification'
    _order = 'issue_date desc'
    
    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True, ondelete='cascade')
    name = fields.Char('Certification Name', required=True)
    certification_type = fields.Selection([
        ('iso', 'ISO Certification'),
        ('quality', 'Quality Certification'),
        ('safety', 'Safety Certification'),
        ('environmental', 'Environmental Certification'),
        ('industry_specific', 'Industry Specific'),
        ('other', 'Other'),
    ], string='Type', required=True)
    
    certificate_number = fields.Char('Certificate Number', required=True)
    issuing_authority = fields.Char('Issuing Authority', required=True)
    issue_date = fields.Date('Issue Date', required=True)
    expiry_date = fields.Date('Expiry Date')
    
    certificate_file = fields.Binary('Certificate File')
    certificate_filename = fields.Char('Certificate Filename')
    
    is_expired = fields.Boolean('Expired', compute='_compute_is_expired')
    days_to_expiry = fields.Integer('Days to Expiry', compute='_compute_days_to_expiry')
    
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            record.is_expired = record.expiry_date and record.expiry_date < today
    
    @api.depends('expiry_date')
    def _compute_days_to_expiry(self):
        today = fields.Date.today()
        for record in self:
            if record.expiry_date:
                delta = record.expiry_date - today
                record.days_to_expiry = delta.days
            else:
                record.days_to_expiry = 0


class VendorDocument(models.Model):
    _name = 'avgc.vendor.document'
    _description = 'Vendor Document'
    _inherit = ['mail.thread']
    
    name = fields.Char('Document Name', required=True)
    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True, ondelete='cascade')
    
    document_type = fields.Selection([
        ('registration', 'Registration Certificate'),
        ('pan', 'PAN Card'),
        ('gst', 'GST Certificate'),
        ('bank', 'Bank Details'),
        ('experience', 'Experience Certificate'),
        ('financial', 'Financial Documents'),
        ('technical', 'Technical Qualification'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    
    file_data = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')
    file_size = fields.Integer('File Size')
    mime_type = fields.Char('MIME Type')
    
    is_mandatory = fields.Boolean('Mandatory', default=True)
    is_verified = fields.Boolean('Verified', default=False)
    verified_by = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Datetime('Verification Date')
    verification_notes = fields.Text('Verification Notes')
    
    expiry_date = fields.Date('Expiry Date')
    is_expired = fields.Boolean('Expired', compute='_compute_is_expired')
    
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for record in self:
            record.is_expired = record.expiry_date and record.expiry_date < today
    
    def action_verify(self):
        """Verify document"""
        for record in self:
            record.is_verified = True
            record.verified_by = self.env.user
            record.verification_date = fields.Datetime.now()
            record.message_post(body=_('Document has been verified.'))


class VendorEvaluation(models.Model):
    _name = 'avgc.vendor.evaluation'
    _description = 'Vendor Performance Evaluation'
    _inherit = ['mail.thread']
    
    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True, ondelete='cascade')
    tender_id = fields.Many2one('avgc.tender', string='Related Tender')
    evaluation_period = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('project_based', 'Project Based'),
    ], string='Evaluation Period', required=True)
    
    # Rating Criteria
    quality_rating = fields.Float('Quality Rating', digits=(2, 1), required=True)
    delivery_rating = fields.Float('Delivery Rating', digits=(2, 1), required=True)
    service_rating = fields.Float('Service Rating', digits=(2, 1), required=True)
    compliance_rating = fields.Float('Compliance Rating', digits=(2, 1), required=True)
    cost_rating = fields.Float('Cost Effectiveness', digits=(2, 1), required=True)
    
    # Overall Score
    overall_rating = fields.Float('Overall Rating', compute='_compute_overall_rating', 
                                 digits=(2, 1), store=True)
    
    # Evaluation Details
    evaluator_id = fields.Many2one('res.users', string='Evaluator', required=True,
                                  default=lambda self: self.env.user)
    evaluation_date = fields.Date('Evaluation Date', required=True, default=fields.Date.today)
    
    # Comments and Feedback
    strengths = fields.Text('Strengths')
    weaknesses = fields.Text('Areas for Improvement')
    recommendations = fields.Text('Recommendations')
    general_comments = fields.Text('General Comments')
    
    # Action Items
    action_required = fields.Boolean('Action Required', default=False)
    action_items = fields.Text('Action Items')
    follow_up_date = fields.Date('Follow-up Date')
    
    @api.depends('quality_rating', 'delivery_rating', 'service_rating', 
                 'compliance_rating', 'cost_rating')
    def _compute_overall_rating(self):
        for record in self:
            ratings = [record.quality_rating, record.delivery_rating, 
                      record.service_rating, record.compliance_rating, record.cost_rating]
            if all(ratings):
                record.overall_rating = sum(ratings) / len(ratings)
            else:
                record.overall_rating = 0.0
    
    @api.constrains('quality_rating', 'delivery_rating', 'service_rating', 
                    'compliance_rating', 'cost_rating')
    def _check_ratings(self):
        for record in self:
            ratings = [record.quality_rating, record.delivery_rating, 
                      record.service_rating, record.compliance_rating, record.cost_rating]
            for rating in ratings:
                if rating < 0 or rating > 5:
                    raise ValidationError(_('All ratings must be between 0 and 5.'))
    
    @api.model
    def create(self, vals):
        result = super(VendorEvaluation, self).create(vals)
        # Update vendor's overall performance rating
        result._update_vendor_rating()
        return result
    
    def write(self, vals):
        result = super(VendorEvaluation, self).write(vals)
        # Update vendor's overall performance rating
        for record in self:
            record._update_vendor_rating()
        return result
    
    def _update_vendor_rating(self):
        """Update vendor's overall performance rating based on evaluations"""
        for record in self:
            evaluations = self.search([('vendor_id', '=', record.vendor_id.id)])
            if evaluations:
                avg_rating = sum(evaluations.mapped('overall_rating')) / len(evaluations)
                record.vendor_id.performance_rating = avg_rating