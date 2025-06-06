# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError


class AvfClientPortal(models.Model):
    _name = 'avf.client.portal'
    _description = 'Client Portal Access and Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Portal Name', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True,
                               domain=[('is_company', '=', True)])
    project_id = fields.Many2one('architect.project', string='Project', required=True)

    # Access details
    portal_url = fields.Char(string='Portal URL', compute='_compute_portal_url')
    access_token = fields.Char(string='Access Token', copy=False)

    # Portal users
    portal_user_ids = fields.Many2many('res.users', string='Portal Users')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed')
    ], string='Status', default='draft', tracking=True)

    # Permissions
    view_drawings = fields.Boolean(string='Can View Drawings', default=True)
    download_documents = fields.Boolean(string='Can Download Documents', default=True)
    submit_feedback = fields.Boolean(string='Can Submit Feedback', default=True)
    view_progress = fields.Boolean(string='Can View Progress', default=True)
    view_financials = fields.Boolean(string='Can View Financials', default=False)

    # Portal features
    show_milestones = fields.Boolean(string='Show Milestones', default=True)
    show_timeline = fields.Boolean(string='Show Timeline', default=True)
    show_gallery = fields.Boolean(string='Show Gallery', default=True)

    # Notifications
    email_notifications = fields.Boolean(string='Email Notifications', default=True)
    sms_notifications = fields.Boolean(string='SMS Notifications', default=False)

    # Activity tracking
    last_login = fields.Datetime(string='Last Login')
    login_count = fields.Integer(string='Login Count', default=0)

    # Feedback and communication
    feedback_ids = fields.One2many('avf.client.feedback', 'portal_id', string='Feedback')
    message_count = fields.Integer(string='Messages', compute='_compute_message_count')

    @api.depends('access_token')
    def _compute_portal_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.access_token:
                record.portal_url = f"{base_url}/client/portal/{record.access_token}"
            else:
                record.portal_url = False

    def _compute_message_count(self):
        for record in self:
            record.message_count = len(record.message_ids)

    @api.model
    def create(self, vals):
        if not vals.get('access_token'):
            vals['access_token'] = self._generate_access_token()
        return super().create(vals)

    def _generate_access_token(self):
        """Generate a unique access token for the portal"""
        import secrets
        return secrets.token_urlsafe(32)

    def action_activate_portal(self):
        """Activate the client portal"""
        self.state = 'active'
        # Send activation email to portal users
        self._send_portal_activation_email()

    def action_suspend_portal(self):
        """Suspend portal access"""
        self.state = 'suspended'

    def _send_portal_activation_email(self):
        """Send portal activation email to users"""
        # Implementation for sending activation emails
        pass

    def record_login(self):
        """Record portal login activity"""
        self.last_login = fields.Datetime.now()
        self.login_count += 1


class AvfClientFeedback(models.Model):
    _name = 'avf.client.feedback'
    _description = 'Client Feedback and Comments'
    _order = 'create_date desc'

    portal_id = fields.Many2one('avf.client.portal', string='Portal', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)
    subject = fields.Char(string='Subject', required=True)
    message = fields.Text(string='Message', required=True)

    # Feedback type
    feedback_type = fields.Selection([
        ('general', 'General Feedback'),
        ('design', 'Design Feedback'),
        ('progress', 'Progress Update'),
        ('issue', 'Issue/Problem'),
        ('suggestion', 'Suggestion'),
        ('approval', 'Approval/Sign-off')
    ], string='Feedback Type', required=True, default='general')

    # Status
    state = fields.Selection([
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', default='new')

    # Response
    response = fields.Text(string='Response')
    responded_by = fields.Many2one('res.users', string='Responded By')
    response_date = fields.Datetime(string='Response Date')

    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    # Priority
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium')

    def action_acknowledge(self):
        """Acknowledge the feedback"""
        self.state = 'acknowledged'

    def action_respond(self):
        """Mark as responded"""
        self.state = 'resolved'
        self.responded_by = self.env.user
        self.response_date = fields.Datetime.now()