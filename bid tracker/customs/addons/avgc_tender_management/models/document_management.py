from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import hashlib
import base64
import logging

_logger = logging.getLogger(__name__)


class DocumentCategory(models.Model):
    _name = 'avgc.document.category'
    _description = 'Document Category'
    _order = 'name'
    
    name = fields.Char('Category Name', required=True)
    code = fields.Char('Category Code', required=True)
    description = fields.Text('Description')
    parent_id = fields.Many2one('avgc.document.category', string='Parent Category')
    child_ids = fields.One2many('avgc.document.category', 'parent_id', string='Child Categories')
    
    is_required = fields.Boolean('Required Category', default=False)
    sort_order = fields.Integer('Sort Order', default=10)
    
    document_count = fields.Integer('Document Count', compute='_compute_document_count')
    
    @api.depends('name')
    def _compute_document_count(self):
        for record in self:
            # Count documents in this category
            count = self.env['avgc.firm.document'].search_count([('category_id', '=', record.id)])
            record.document_count = count


class FirmDocument(models.Model):
    _name = 'avgc.firm.document'
    _description = 'Firm Document Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # Basic Information
    document_name = fields.Char('Document Name', required=True, tracking=True)
    document_number = fields.Char('Document Number', tracking=True)
    description = fields.Text('Description')
    
    # Classification
    firm_id = fields.Many2one('avgc.firm', string='Firm', required=True, ondelete='cascade')
    category_id = fields.Many2one('avgc.document.category', string='Category', required=True)
    
    # File Information
    file_data = fields.Binary('Document File', required=True)
    file_name = fields.Char('File Name', required=True)
    file_size = fields.Integer('File Size (bytes)')
    mime_type = fields.Char('MIME Type')
    file_hash = fields.Char('File Hash (SHA-256)', readonly=True)
    
    # Status and Workflow
    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Version Control
    version = fields.Char('Version', default='1.0', tracking=True)
    previous_version_id = fields.Many2one('avgc.firm.document', string='Previous Version')
    next_version_ids = fields.One2many('avgc.firm.document', 'previous_version_id', string='Next Versions')
    is_current_version = fields.Boolean('Current Version', default=True, tracking=True)
    
    # Dates
    effective_date = fields.Date('Effective Date', default=fields.Date.today)
    expiry_date = fields.Date('Expiry Date')
    review_date = fields.Date('Review Date')
    
    # Access Control
    confidentiality_level = fields.Selection([
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
    ], string='Confidentiality Level', default='internal', required=True)
    
    # Approval Workflow
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    reviewed_by = fields.Many2one('res.users', string='Reviewed By')
    approved_by = fields.Many2one('res.users', string='Approved By')
    review_date_actual = fields.Datetime('Actual Review Date')
    approval_date = fields.Datetime('Approval Date')
    
    # Tags and Metadata
    tags = fields.Char('Tags')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='medium')
    
    # External References
    external_reference = fields.Char('External Reference')
    source_system = fields.Char('Source System')
    
    # Computed Fields
    is_expired = fields.Boolean('Expired', compute='_compute_is_expired')
    days_to_expiry = fields.Integer('Days to Expiry', compute='_compute_days_to_expiry')
    
    # Related Documents
    related_document_ids = fields.Many2many('avgc.firm.document', 
                                           'document_relation_rel', 
                                           'document_id', 
                                           'related_document_id',
                                           string='Related Documents')
    
    # Audit Trail
    access_log_ids = fields.One2many('avgc.document.access.log', 'document_id', string='Access Log')
    
    @api.model
    def create(self, vals):
        # Generate file hash
        if vals.get('file_data'):
            file_content = base64.b64decode(vals['file_data'])
            vals['file_hash'] = hashlib.sha256(file_content).hexdigest()
            vals['file_size'] = len(file_content)
        
        result = super(FirmDocument, self).create(vals)
        result._log_access('create')
        return result
    
    def write(self, vals):
        # Generate new file hash if file changed
        if vals.get('file_data'):
            file_content = base64.b64decode(vals['file_data'])
            vals['file_hash'] = hashlib.sha256(file_content).hexdigest()
            vals['file_size'] = len(file_content)
        
        result = super(FirmDocument, self).write(vals)
        for record in self:
            record._log_access('update')
        return result
    
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
    
    def _log_access(self, action):
        """Log document access"""
        self.env['avgc.document.access.log'].create({
            'document_id': self.id,
            'user_id': self.env.user.id,
            'action': action,
            'timestamp': fields.Datetime.now(),
            'ip_address': self.env.context.get('remote_addr', 'unknown'),
        })
    
    def action_submit_for_review(self):
        """Submit document for review"""
        for record in self:
            if record.status == 'draft':
                record.status = 'pending_review'
                record.message_post(body=_('Document submitted for review.'))
    
    def action_approve(self):
        """Approve document"""
        for record in self:
            if record.status == 'pending_review':
                record.status = 'approved'
                record.approved_by = self.env.user
                record.approval_date = fields.Datetime.now()
                record.message_post(body=_('Document approved.'))
    
    def action_reject(self):
        """Reject document"""
        return {
            'name': _('Reject Document'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'avgc.document.reject.wizard',
            'target': 'new',
            'context': {'default_document_id': self.id},
        }
    
    def action_create_new_version(self):
        """Create new version of document"""
        for record in self:
            # Mark current version as not current
            record.is_current_version = False
            
            # Create new version
            new_version = record.copy({
                'version': self._increment_version(record.version),
                'previous_version_id': record.id,
                'status': 'draft',
                'is_current_version': True,
            })
            
            return {
                'name': _('New Document Version'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'avgc.firm.document',
                'res_id': new_version.id,
                'target': 'current',
            }
    
    def _increment_version(self, current_version):
        """Increment version number"""
        try:
            parts = current_version.split('.')
            if len(parts) >= 2:
                parts[-1] = str(int(parts[-1]) + 1)
                return '.'.join(parts)
            else:
                return f"{current_version}.1"
        except:
            return "1.1"
    
    def action_download(self):
        """Download document"""
        self._log_access('download')
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/avgc.firm.document/{self.id}/file_data/{self.file_name}?download=true',
            'target': 'self',
        }
    
    def action_preview(self):
        """Preview document"""
        self._log_access('view')
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/avgc.firm.document/{self.id}/file_data/{self.file_name}',
            'target': 'new',
        }


class Firm(models.Model):
    _name = 'avgc.firm'
    _description = 'Firm Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    # Basic Information
    name = fields.Char('Firm Name', required=True, tracking=True)
    code = fields.Char('Firm Code', copy=False, default=lambda self: _('New'))
    
    # Contact Information
    email = fields.Char('Email', tracking=True)
    phone = fields.Char('Phone', tracking=True)
    website = fields.Char('Website')
    
    # Address
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char('ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    
    # Business Information
    registration_number = fields.Char('Registration Number', tracking=True)
    established_date = fields.Date('Established Date')
    contact_person = fields.Char('Contact Person')
    
    # Status
    is_active = fields.Boolean('Active', default=True, tracking=True)
    
    # Document Management
    document_ids = fields.One2many('avgc.firm.document', 'firm_id', string='Documents')
    document_count = fields.Integer('Document Count', compute='_compute_document_count')
    
    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('avgc.firm') or _('New')
        return super(Firm, self).create(vals)
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    def action_view_documents(self):
        """View firm documents"""
        return {
            'name': _('Firm Documents'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'avgc.firm.document',
            'domain': [('firm_id', '=', self.id)],
            'context': {'default_firm_id': self.id},
        }


class DocumentAccessLog(models.Model):
    _name = 'avgc.document.access.log'
    _description = 'Document Access Log'
    _order = 'timestamp desc'
    
    document_id = fields.Many2one('avgc.firm.document', string='Document', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)
    action = fields.Selection([
        ('create', 'Created'),
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
    ], string='Action', required=True)
    
    timestamp = fields.Datetime('Timestamp', required=True, default=fields.Datetime.now)
    ip_address = fields.Char('IP Address')
    user_agent = fields.Char('User Agent')
    session_id = fields.Char('Session ID')
    
    # Additional Context
    details = fields.Text('Additional Details')


class DocumentShare(models.Model):
    _name = 'avgc.document.share'
    _description = 'Document Sharing'
    _inherit = ['mail.thread']
    
    document_id = fields.Many2one('avgc.firm.document', string='Document', required=True, ondelete='cascade')
    shared_with = fields.Many2one('res.users', string='Shared With', required=True)
    shared_by = fields.Many2one('res.users', string='Shared By', default=lambda self: self.env.user)
    
    # Permissions
    can_view = fields.Boolean('Can View', default=True)
    can_download = fields.Boolean('Can Download', default=False)
    can_edit = fields.Boolean('Can Edit', default=False)
    can_approve = fields.Boolean('Can Approve', default=False)
    
    # Sharing Details
    share_date = fields.Datetime('Share Date', default=fields.Datetime.now)
    expiry_date = fields.Datetime('Expiry Date')
    access_count = fields.Integer('Access Count', default=0)
    last_accessed = fields.Datetime('Last Accessed')
    
    # Status
    is_active = fields.Boolean('Active', default=True)
    
    # Computed Fields
    is_expired = fields.Boolean('Expired', compute='_compute_is_expired')
    
    @api.depends('expiry_date')
    def _compute_is_expired(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_expired = record.expiry_date and record.expiry_date < now
    
    def action_revoke_access(self):
        """Revoke document access"""
        for record in self:
            record.is_active = False
            record.message_post(body=_('Document access revoked.'))


class DocumentVersion(models.Model):
    _name = 'avgc.document.version'
    _description = 'Document Version History'
    _order = 'version_number desc'
    
    document_id = fields.Many2one('avgc.firm.document', string='Document', required=True, ondelete='cascade')
    version_number = fields.Char('Version Number', required=True)
    
    # Version Data
    file_data = fields.Binary('File Data')
    file_name = fields.Char('File Name')
    file_size = fields.Integer('File Size')
    file_hash = fields.Char('File Hash')
    
    # Version Metadata
    created_by = fields.Many2one('res.users', string='Created By', required=True)
    creation_date = fields.Datetime('Creation Date', default=fields.Datetime.now)
    change_summary = fields.Text('Change Summary')
    
    # Status
    is_current = fields.Boolean('Current Version', default=False)
    
    def action_restore_version(self):
        """Restore this version as current"""
        for record in self:
            # Update document with this version's data
            record.document_id.write({
                'file_data': record.file_data,
                'file_name': record.file_name,
                'file_size': record.file_size,
                'file_hash': record.file_hash,
                'version': record.version_number,
            })
            
            # Update version flags
            record.document_id.version_ids.write({'is_current': False})
            record.is_current = True
            
            record.document_id.message_post(
                body=_('Restored to version %s') % record.version_number
            )


class DocumentBulkOperation(models.Model):
    _name = 'avgc.document.bulk.operation'
    _description = 'Document Bulk Operations'
    
    name = fields.Char('Operation Name', required=True)
    operation_type = fields.Selection([
        ('approve', 'Bulk Approve'),
        ('reject', 'Bulk Reject'),
        ('archive', 'Bulk Archive'),
        ('delete', 'Bulk Delete'),
        ('category_change', 'Change Category'),
        ('status_change', 'Change Status'),
    ], string='Operation Type', required=True)
    
    document_ids = fields.Many2many('avgc.firm.document', string='Documents')
    
    # Operation Parameters
    new_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ], string='New Status')
    
    new_category_id = fields.Many2one('avgc.document.category', string='New Category')
    notes = fields.Text('Notes')
    
    # Execution
    executed_by = fields.Many2one('res.users', string='Executed By')
    execution_date = fields.Datetime('Execution Date')
    is_executed = fields.Boolean('Executed', default=False)
    
    # Results
    success_count = fields.Integer('Success Count', default=0)
    error_count = fields.Integer('Error Count', default=0)
    error_log = fields.Text('Error Log')
    
    def action_execute(self):
        """Execute bulk operation"""
        self.ensure_one()
        
        if self.is_executed:
            raise UserError(_('This operation has already been executed.'))
        
        success_count = 0
        error_count = 0
        errors = []
        
        for document in self.document_ids:
            try:
                if self.operation_type == 'approve':
                    document.action_approve()
                elif self.operation_type == 'reject':
                    document.status = 'rejected'
                elif self.operation_type == 'archive':
                    document.status = 'archived'
                elif self.operation_type == 'category_change':
                    document.category_id = self.new_category_id
                elif self.operation_type == 'status_change':
                    document.status = self.new_status
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Document {document.name}: {str(e)}")
        
        # Update operation results
        self.write({
            'is_executed': True,
            'executed_by': self.env.user.id,
            'execution_date': fields.Datetime.now(),
            'success_count': success_count,
            'error_count': error_count,
            'error_log': '\n'.join(errors) if errors else '',
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Bulk Operation Completed'),
                'message': _('Successfully processed %s documents. %s errors.') % (success_count, error_count),
                'type': 'success' if error_count == 0 else 'warning',
                'sticky': False,
            }
        }