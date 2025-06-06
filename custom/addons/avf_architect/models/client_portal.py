
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AvfClientPortal(models.Model):
    _name = 'avf.client.portal'
    _description = 'Client Portal Access'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Portal Name', required=True, compute='_compute_name', store=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True, 
                               domain=[('is_company', '=', True)], ondelete='cascade')
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')

    # Access permissions
    can_view_drawings = fields.Boolean(string='Can View Drawings', default=True)
    can_view_dpr = fields.Boolean(string='Can View DPR', default=True)
    can_view_compliance = fields.Boolean(string='Can View Compliance', default=True)
    can_view_financial = fields.Boolean(string='Can View Financial', default=False)
    can_upload_documents = fields.Boolean(string='Can Upload Documents', default=False)
    can_comment = fields.Boolean(string='Can Comment', default=True)

    # Status
    is_active = fields.Boolean(string='Active', default=True)
    access_granted_date = fields.Datetime(string='Access Granted Date', default=fields.Datetime.now)
    last_login = fields.Datetime(string='Last Login')

    # Portal user
    portal_user_id = fields.Many2one('res.users', string='Portal User')

    # Notifications
    email_notifications = fields.Boolean(string='Email Notifications', default=True)
    sms_notifications = fields.Boolean(string='SMS Notifications', default=False)

    @api.depends('client_id', 'project_id')
    def _compute_name(self):
        for record in self:
            if record.client_id and record.project_id:
                record.name = f"{record.client_id.name} - {record.project_id.name}"
            else:
                record.name = "New Portal Access"

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to handle batch creation"""
        records = super().create(vals_list)
        for record in records:
            if not record.portal_user_id and record.client_id:
                record._create_portal_user()
        return records

    def _create_portal_user(self):
        """Create portal user for client"""
        self.ensure_one()
        if not self.client_id.user_ids:
            # Create portal user
            portal_group = self.env.ref('base.group_portal')
            user_vals = {
                'name': self.client_id.name,
                'login': self.client_id.email or f"client_{self.client_id.id}@portal.com",
                'email': self.client_id.email,
                'partner_id': self.client_id.id,
                'groups_id': [(6, 0, [portal_group.id])],
                'active': True,
            }
            portal_user = self.env['res.users'].create(user_vals)
            self.portal_user_id = portal_user.id

    def action_grant_access(self):
        """Grant portal access"""
        self.ensure_one()
        self.is_active = True
        self.access_granted_date = fields.Datetime.now()
        self.message_post(body=_("Portal access granted."))

    def action_revoke_access(self):
        """Revoke portal access"""
        self.ensure_one()
        self.is_active = False
        if self.portal_user_id:
            self.portal_user_id.active = False
        self.message_post(body=_("Portal access revoked."))

    def action_send_invitation(self):
        """Send portal invitation email"""
        self.ensure_one()
        if not self.client_id.email:
            raise ValidationError(_("Client email is required to send invitation."))
        
        # Send invitation email logic here
        self.message_post(body=_("Portal invitation sent to %s") % self.client_id.email)

class AvfClientDocument(models.Model):
    _name = 'avf.client.document'
    _description = 'Client Uploaded Documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Document Name', required=True)
    portal_id = fields.Many2one('avf.client.portal', string='Portal Access', required=True, ondelete='cascade')
    project_id = fields.Many2one('project.project', string='Project', related='portal_id.project_id', store=True)
    client_id = fields.Many2one('res.partner', string='Client', related='portal_id.client_id', store=True)

    # File
    document_file = fields.Binary(string='Document', attachment=True, required=True)
    document_filename = fields.Char(string='Filename')
    document_size = fields.Integer(string='File Size')

    # Document details
    document_type = fields.Selection([
        ('approval', 'Approval Document'),
        ('feedback', 'Feedback'),
        ('specification', 'Specification'),
        ('other', 'Other')
    ], string='Document Type', required=True)

    description = fields.Text(string='Description')
    upload_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now)

    # Status
    is_reviewed = fields.Boolean(string='Reviewed', default=False)
    reviewed_by = fields.Many2one('res.users', string='Reviewed By')
    review_date = fields.Datetime(string='Review Date')
    review_comments = fields.Text(string='Review Comments')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to handle batch creation"""
        return super().create(vals_list)

    def action_mark_reviewed(self):
        """Mark document as reviewed"""
        self.ensure_one()
        self.is_reviewed = True
        self.reviewed_by = self.env.user
        self.review_date = fields.Datetime.now()
        self.message_post(body=_("Document marked as reviewed."))

class AvfClientFeedback(models.Model):
    _name = 'avf.client.feedback'
    _description = 'Client Feedback'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'subject'

    subject = fields.Char(string='Subject', required=True)
    portal_id = fields.Many2one('avf.client.portal', string='Portal Access', required=True, ondelete='cascade')
    project_id = fields.Many2one('project.project', string='Project', related='portal_id.project_id', store=True)
    client_id = fields.Many2one('res.partner', string='Client', related='portal_id.client_id', store=True)

    # Feedback details
    feedback_type = fields.Selection([
        ('general', 'General Feedback'),
        ('design', 'Design Feedback'),
        ('progress', 'Progress Feedback'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion')
    ], string='Feedback Type', required=True)

    message = fields.Html(string='Message', required=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium')

    # Status
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', default='new', tracking=True)

    # Response
    response = fields.Html(string='Response')
    responded_by = fields.Many2one('res.users', string='Responded By')
    response_date = fields.Datetime(string='Response Date')

    # Dates
    feedback_date = fields.Datetime(string='Feedback Date', default=fields.Datetime.now)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to handle batch creation"""
        return super().create(vals_list)

    def action_respond(self):
        """Open response wizard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Respond to Feedback',
            'res_model': 'avf.client.feedback',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_mark_resolved(self):
        """Mark feedback as resolved"""
        self.ensure_one()
        self.state = 'resolved'
        self.message_post(body=_("Feedback marked as resolved."))

    def action_close(self):
        """Close feedback"""
        self.ensure_one()
        self.state = 'closed'
        self.message_post(body=_("Feedback closed."))
