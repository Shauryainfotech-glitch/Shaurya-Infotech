from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class VendorCategory(models.Model):
    _name = 'avgc.vendor.category'
    _description = 'Vendor Category'
    _parent_store = True
    _order = 'sequence, name'

    name = fields.Char('Category Name', required=True)
    code = fields.Char('Category Code')
    parent_id = fields.Many2one('avgc.vendor.category', string='Parent Category',
                               ondelete='restrict')
    child_ids = fields.One2many('avgc.vendor.category', 'parent_id',
                               string='Child Categories')
    parent_path = fields.Char(index=True)
    sequence = fields.Integer('Sequence', default=10)
    
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
    
    vendor_count = fields.Integer('Vendor Count', compute='_compute_vendor_count')
    
    @api.depends('child_ids.vendor_count')
    def _compute_vendor_count(self):
        for record in self:
            vendors = self.env['avgc.vendor'].search([
                ('category_ids', 'child_of', record.id)
            ])
            record.vendor_count = len(vendors)

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive categories.'))


class Vendor(models.Model):
    _name = 'avgc.vendor'
    _description = 'Vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Vendor Name', required=True, tracking=True)
    code = fields.Char('Vendor Code', copy=False)
    company_type = fields.Selection([
        ('individual', 'Individual'),
        ('company', 'Company'),
    ], string='Company Type', default='company', required=True)
    
    # Contact Information
    email = fields.Char('Email', required=True)
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    website = fields.Char('Website')
    
    # Address
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char('ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    
    # Categories and Classification
    category_ids = fields.Many2many('avgc.vendor.category', string='Categories')
    vendor_type = fields.Selection([
        ('manufacturer', 'Manufacturer'),
        ('distributor', 'Distributor'),
        ('service', 'Service Provider'),
        ('contractor', 'Contractor'),
        ('consultant', 'Consultant'),
    ], string='Vendor Type', required=True)
    
    # Company Details
    registration_no = fields.Char('Registration Number')
    tax_id = fields.Char('Tax ID')
    establishment_date = fields.Date('Establishment Date')
    employee_count = fields.Integer('Number of Employees')
    annual_revenue = fields.Monetary('Annual Revenue', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    
    # Compliance and Certification
    is_certified = fields.Boolean('Is Certified')
    certification_ids = fields.One2many('avgc.vendor.certification', 'vendor_id',
                                      string='Certifications')
    compliance_score = fields.Float('Compliance Score', digits=(5, 2))
    
    # Performance Metrics
    rating = fields.Float('Rating', digits=(2, 1), default=0.0)
    successful_bids = fields.Integer('Successful Bids', compute='_compute_bid_stats')
    total_bids = fields.Integer('Total Bids', compute='_compute_bid_stats')
    success_rate = fields.Float('Success Rate (%)', compute='_compute_bid_stats')
    
    # Status
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('qualified', 'Qualified'),
        ('approved', 'Approved'),
        ('blacklisted', 'Blacklisted'),
    ], string='Status', default='draft', tracking=True)
    
    # Documents
    document_ids = fields.One2many('avgc.vendor.document', 'vendor_id',
                                 string='Documents')
    document_count = fields.Integer('Document Count', compute='_compute_document_count')

    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)

    @api.depends('submission_ids', 'submission_ids.status')
    def _compute_bid_stats(self):
        for record in self:
            submissions = self.env['avgc.tender.submission'].search([
                ('vendor_id', '=', record.id)
            ])
            record.total_bids = len(submissions)
            record.successful_bids = len(submissions.filtered(
                lambda s: s.status == 'awarded'
            ))
            record.success_rate = (record.successful_bids / record.total_bids * 100
                                 if record.total_bids else 0)

    def action_qualify(self):
        self.write({'state': 'qualified'})
        self.message_post(body=_('Vendor has been qualified.'))

    def action_approve(self):
        self.write({'state': 'approved'})
        self.message_post(body=_('Vendor has been approved.'))

    def action_blacklist(self):
        self.write({'state': 'blacklisted', 'active': False})
        self.message_post(body=_('Vendor has been blacklisted.'))

    def action_reactivate(self):
        self.write({'state': 'draft', 'active': True})
        self.message_post(body=_('Vendor has been reactivated.'))


class VendorCertification(models.Model):
    _name = 'avgc.vendor.certification'
    _description = 'Vendor Certification'

    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True,
                               ondelete='cascade')
    name = fields.Char('Certification Name', required=True)
    issuer = fields.Char('Issuing Authority')
    certificate_no = fields.Char('Certificate Number')
    issue_date = fields.Date('Issue Date')
    expiry_date = fields.Date('Expiry Date')
    attachment = fields.Binary('Certificate Copy')
    attachment_name = fields.Char('File Name')
    status = fields.Selection([
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ], string='Status', compute='_compute_status', store=True)

    @api.depends('expiry_date')
    def _compute_status(self):
        today = fields.Date.today()
        for record in self:
            if not record.expiry_date:
                record.status = 'valid'
            elif record.expiry_date < today:
                record.status = 'expired'
            else:
                record.status = 'valid'


class VendorDocument(models.Model):
    _name = 'avgc.vendor.document'
    _description = 'Vendor Document'
    _inherit = ['mail.thread']

    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True,
                               ondelete='cascade')
    name = fields.Char('Document Name', required=True)
    document_type = fields.Selection([
        ('registration', 'Company Registration'),
        ('tax', 'Tax Document'),
        ('financial', 'Financial Statement'),
        ('certification', 'Certification'),
        ('compliance', 'Compliance Document'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    
    file_data = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')
    expiry_date = fields.Date('Expiry Date')
    
    is_verified = fields.Boolean('Verified', default=False)
    verified_by = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Datetime('Verification Date')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ], string='Status', default='draft', tracking=True)

    def action_verify(self):
        self.write({
            'state': 'verified',
            'is_verified': True,
            'verified_by': self.env.user.id,
            'verification_date': fields.Datetime.now(),
        })
        self.message_post(body=_('Document has been verified.'))

    def action_reject(self):
        self.write({'state': 'rejected'})
        self.message_post(body=_('Document has been rejected.'))
