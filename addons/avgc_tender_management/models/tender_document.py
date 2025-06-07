from odoo import models, fields, api, _
from datetime import timedelta

class TenderDocument(models.Model):
    _name = 'avgc.tender.document'
    _description = 'Tender Document'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char('Document Name', required=True, tracking=True)
    tender_id = fields.Many2one('avgc.tender', string='Tender', required=True,
                               ondelete='cascade')
    document_type = fields.Selection([
        ('rfp', 'Request for Proposal'),
        ('technical', 'Technical Specification'),
        ('financial', 'Financial Document'),
        ('legal', 'Legal Document'),
        ('compliance', 'Compliance Document'),
        ('addendum', 'Addendum'),
        ('clarification', 'Clarification'),
        ('evaluation', 'Evaluation Document'),
        ('other', 'Other'),
    ], string='Document Type', required=True, tracking=True)
    
    # File Information
    file_data = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')
    file_size = fields.Integer('File Size', compute='_compute_file_size', store=True)
    mime_type = fields.Char('MIME Type')
    
    # Document Properties
    is_mandatory = fields.Boolean('Mandatory Document', default=True)
    version = fields.Char('Version', default='1.0')
    valid_from = fields.Date('Valid From')
    valid_until = fields.Date('Valid Until')
    
    # AI Analysis
    analysis_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Analysis Status', default='pending')
    ocr_text = fields.Text('OCR Text')
    ai_summary = fields.Text('AI Summary')
    compliance_score = fields.Float('Compliance Score', digits=(5, 2))
    
    # Access Control
    created_by = fields.Many2one('res.users', string='Created By',
                                default=lambda self: self.env.user,
                                readonly=True)
    access_level = fields.Selection([
        ('public', 'Public'),
        ('internal', 'Internal Only'),
        ('restricted', 'Restricted'),
    ], string='Access Level', default='internal', required=True)
    
    # Version Control
    parent_id = fields.Many2one('avgc.tender.document', string='Previous Version')
    child_ids = fields.One2many('avgc.tender.document', 'parent_id',
                               string='Subsequent Versions')
    is_latest_version = fields.Boolean('Latest Version', compute='_compute_is_latest',
                                     store=True)
    
    # Document Sharing
    shared_with_ids = fields.Many2many('res.users', string='Shared With')
    share_expiry = fields.Datetime('Share Expiry')
    
    # Document Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('file_data')
    def _compute_file_size(self):
        for record in self:
            record.file_size = len(record.file_data) if record.file_data else 0

    @api.depends('child_ids')
    def _compute_is_latest(self):
        for record in self:
            record.is_latest_version = not bool(record.child_ids)

    def action_submit_for_review(self):
        self.write({'state': 'under_review'})
        self.message_post(body=_('Document submitted for review.'))

    def action_approve(self):
        self.write({'state': 'approved'})
        self.message_post(body=_('Document has been approved.'))

    def action_publish(self):
        self.write({'state': 'published'})
        self.message_post(body=_('Document has been published.'))

    def action_archive(self):
        self.write({'state': 'archived'})
        self.message_post(body=_('Document has been archived.'))

    def action_process_ocr(self):
        """Process document through OCR"""
        self.ensure_one()
        self.write({
            'analysis_status': 'in_progress'
        })
        # OCR processing would be implemented here
        self.message_post(body=_('OCR processing initiated.'))

    def action_analyze_content(self):
        """Analyze document content using AI"""
        self.ensure_one()
        if not self.ocr_text:
            self.action_process_ocr()
        self.write({
            'analysis_status': 'in_progress'
        })
        # AI analysis would be implemented here
        self.message_post(body=_('Content analysis initiated.'))

    def create_new_version(self):
        """Create a new version of the document"""
        self.ensure_one()
        new_version = self.copy({
            'parent_id': self.id,
            'version': f"{float(self.version) + 0.1:.1f}",
            'state': 'draft'
        })
        self.message_post(
            body=_('New version %s has been created.') % new_version.version
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'avgc.tender.document',
            'res_id': new_version.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def extend_share(self, days=7):
        """Extend document sharing period"""
        self.ensure_one()
        new_expiry = fields.Datetime.now() + timedelta(days=days)
        self.write({'share_expiry': new_expiry})
        self.message_post(
            body=_('Document sharing extended until %s') % new_expiry
        )

    @api.model
    def cleanup_expired_shares(self):
        """Cleanup expired document shares"""
        expired_docs = self.search([
            ('share_expiry', '!=', False),
            ('share_expiry', '<', fields.Datetime.now())
        ])
        expired_docs.write({
            'shared_with_ids': [(5, 0, 0)],  # Clear all shares
            'share_expiry': False
        })
