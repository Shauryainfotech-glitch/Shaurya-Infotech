
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError

class AVFClientPortal(models.Model):
    _name = 'avf.client.portal'
    _description = 'Client Portal Access'
    _rec_name = 'client_name'

    client_name = fields.Char(string='Client Name', required=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    
    # Access Control
    portal_access = fields.Boolean(string='Portal Access Enabled', default=True)
    access_level = fields.Selection([
        ('basic', 'Basic - View Only'),
        ('standard', 'Standard - View & Comment'),
        ('premium', 'Premium - Full Access')
    ], string='Access Level', default='standard')

    # Portal Features
    can_view_drawings = fields.Boolean(string='Can View Drawings', default=True)
    can_view_progress = fields.Boolean(string='Can View Progress', default=True)
    can_view_documents = fields.Boolean(string='Can View Documents', default=True)
    can_view_financials = fields.Boolean(string='Can View Financials', default=False)
    can_submit_feedback = fields.Boolean(string='Can Submit Feedback', default=True)
    can_approve_changes = fields.Boolean(string='Can Approve Changes', default=False)

    # Credentials
    portal_user_id = fields.Many2one('res.users', string='Portal User')
    last_login = fields.Datetime(string='Last Login')
    login_count = fields.Integer(string='Login Count', default=0)

    # Communication
    email_notifications = fields.Boolean(string='Email Notifications', default=True)
    sms_notifications = fields.Boolean(string='SMS Notifications', default=False)
    notification_frequency = fields.Selection([
        ('real_time', 'Real Time'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Summary'),
        ('milestone', 'Milestone Based')
    ], string='Notification Frequency', default='daily')

    # Status
    active = fields.Boolean(default=True)
    portal_url = fields.Char(string='Portal URL', compute='_compute_portal_url')
    
    # Related Records
    feedback_ids = fields.One2many('avf.client.feedback', 'portal_id', string='Feedback')
    notification_ids = fields.One2many('avf.client.notification', 'portal_id', string='Notifications')

    @api.depends('client_id', 'project_id')
    def _compute_portal_url(self):
        """Compute portal URL for client"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.client_id and record.project_id:
                record.portal_url = f"{base_url}/client/portal/{record.id}"
            else:
                record.portal_url = ""

    def action_create_portal_user(self):
        """Create portal user for client"""
        self.ensure_one()
        if self.portal_user_id:
            raise ValidationError(_("Portal user already exists for this client."))
        
        # Create portal user
        user_vals = {
            'name': self.client_name,
            'login': self.client_id.email,
            'email': self.client_id.email,
            'partner_id': self.client_id.id,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
        }
        portal_user = self.env['res.users'].sudo().create(user_vals)
        self.portal_user_id = portal_user.id

    def action_send_portal_invitation(self):
        """Send portal invitation to client"""
        self.ensure_one()
        if not self.portal_user_id:
            self.action_create_portal_user()
        
        # Send invitation email
        template = self.env.ref('avf_architect.client_portal_invitation_template', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def action_deactivate_access(self):
        """Deactivate portal access"""
        self.ensure_one()
        self.portal_access = False
        if self.portal_user_id:
            self.portal_user_id.active = False

    def action_reactivate_access(self):
        """Reactivate portal access"""
        self.ensure_one()
        self.portal_access = True
        if self.portal_user_id:
            self.portal_user_id.active = True

class AVFClientFeedback(models.Model):
    _name = 'avf.client.feedback'
    _description = 'Client Feedback'
    _order = 'create_date desc'

    portal_id = fields.Many2one('avf.client.portal', string='Portal', required=True, ondelete='cascade')
    project_id = fields.Many2one('project.project', string='Project', related='portal_id.project_id', store=True)
    
    subject = fields.Char(string='Subject', required=True)
    message = fields.Text(string='Message', required=True)
    
    feedback_type = fields.Selection([
        ('general', 'General Feedback'),
        ('design_change', 'Design Change Request'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('appreciation', 'Appreciation')
    ], string='Feedback Type', required=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium')
    
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', default='new')
    
    # Response
    response = fields.Text(string='Response')
    responded_by = fields.Many2one('res.users', string='Responded By')
    response_date = fields.Datetime(string='Response Date')
    
    # Files
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    def action_respond(self):
        """Open response wizard"""
        return {
            'name': _('Respond to Feedback'),
            'type': 'ir.actions.act_window',
            'res_model': 'avf.client.feedback.response.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_feedback_id': self.id},
        }

class AVFClientNotification(models.Model):
    _name = 'avf.client.notification'
    _description = 'Client Notification'
    _order = 'create_date desc'

    portal_id = fields.Many2one('avf.client.portal', string='Portal', required=True, ondelete='cascade')
    
    title = fields.Char(string='Title', required=True)
    message = fields.Text(string='Message', required=True)
    
    notification_type = fields.Selection([
        ('info', 'Information'),
        ('milestone', 'Milestone Update'),
        ('alert', 'Alert'),
        ('approval_request', 'Approval Request'),
        ('document_ready', 'Document Ready')
    ], string='Type', required=True)
    
    # Status
    is_read = fields.Boolean(string='Read', default=False)
    read_date = fields.Datetime(string='Read Date')
    
    # Actions
    action_required = fields.Boolean(string='Action Required', default=False)
    action_url = fields.Char(string='Action URL')
    action_button_text = fields.Char(string='Action Button Text')
    
    def action_mark_read(self):
        """Mark notification as read"""
        self.ensure_one()
        self.is_read = True
        self.read_date = fields.Datetime.now()
