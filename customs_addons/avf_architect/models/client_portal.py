# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import hashlib
from datetime import datetime, timedelta

class ArchitectClientPortal(models.Model):
    _name = 'architect.client.portal'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']
    _description = 'Client Portal'

    name = fields.Char(string='Portal Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    project_ids = fields.Many2many('architect.project', string='Projects')
    dashboard_ids = fields.One2many(
        'architect.client.dashboard',  # or the correct model name
        'portal_id',  # the inverse field on dashboard model
        string='Dashboards'
    )

    portal_id = fields.Many2one('architect.client.portal', string='Client Portal')
    # Access Management
    access_token = fields.Char(string='Access Token', readonly=True, copy=False)
    last_login = fields.Datetime(string='Last Login')
    login_count = fields.Integer(string='Login Count', default=0)
    
    # Portal Features
    show_progress = fields.Boolean(string='Show Progress', default=True)
    show_timeline = fields.Boolean(string='Show Timeline', default=True)
    show_documents = fields.Boolean(string='Show Documents', default=True)
    show_financial = fields.Boolean(string='Show Financial', default=True)
    show_messages = fields.Boolean(string='Show Messages', default=True)
    
    # Customization
    theme = fields.Selection([
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('custom', 'Custom Theme')
    ], string='Portal Theme', default='light')
    custom_css = fields.Text(string='Custom CSS')
    company_logo = fields.Binary(string='Company Logo')
    
    # Notifications
    email_notifications = fields.Boolean(string='Email Notifications', default=True)
    notification_frequency = fields.Selection([
        ('instant', 'Instant'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Summary')
    ], string='Notification Frequency', default='instant')
    
    # Statistics
    visit_count = fields.Integer(string='Visit Count', default=0)
    last_activity = fields.Datetime(string='Last Activity')
    active = fields.Boolean(default=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('access_token'):
                vals['access_token'] = self._generate_access_token()
        return super().create(vals_list)
    
    def _generate_access_token(self):
        """Generate a secure access token"""
        return hashlib.sha256(str(fields.Datetime.now()).encode()).hexdigest()
    
    def reset_access_token(self):
        """Reset the access token"""
        self.access_token = self._generate_access_token()
        self.message_post(body=_("Access token has been reset."))
    
    def track_login(self):
        """Track portal login"""
        self.write({
            'last_login': fields.Datetime.now(),
            'login_count': self.login_count + 1
        })
    
    def track_activity(self):
        """Track portal activity"""
        self.write({
            'last_activity': fields.Datetime.now(),
            'visit_count': self.visit_count + 1
        })


class ArchitectClientDashboard(models.Model):
    _name = 'architect.client.dashboard'
    _description = 'Client Dashboard'

    portal_id = fields.Many2one('architect.client.portal', string='Portal', required=True)
    name = fields.Char(string='Dashboard Name', required=True)
    
    # Layout
    layout = fields.Selection([
        ('grid', 'Grid Layout'),
        ('list', 'List Layout'),
        ('custom', 'Custom Layout')
    ], string='Layout Type', default='grid')
    
    # Widgets
    widget_ids = fields.One2many('architect.dashboard.widget', 'dashboard_id', 
                                string='Dashboard Widgets')
    
    # Customization
    custom_css = fields.Text(string='Custom CSS')
    custom_js = fields.Text(string='Custom JavaScript')
    
    # Access
    is_default = fields.Boolean(string='Default Dashboard')
    sequence = fields.Integer(string='Sequence', default=10)


class ArchitectDashboardWidget(models.Model):
    _name = 'architect.dashboard.widget'
    _description = 'Dashboard Widget'
    _order = 'sequence, id'

    name = fields.Char(string='Widget Name', required=True)
    dashboard_id = fields.Many2one('architect.client.dashboard', string='Dashboard', 
                                  required=True)
    
    # Widget Type
    widget_type = fields.Selection([
        ('project_progress', 'Project Progress'),
        ('timeline', 'Timeline'),
        ('documents', 'Recent Documents'),
        ('messages', 'Messages'),
        ('financial', 'Financial Summary'),
        ('tasks', 'Tasks'),
        ('custom', 'Custom Widget')
    ], string='Widget Type', required=True)
    
    # Layout
    sequence = fields.Integer(string='Sequence', default=10)
    size = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('custom', 'Custom')
    ], string='Widget Size', default='medium')
    
    # Data Configuration
    data_source = fields.Text(string='Data Source')
    refresh_interval = fields.Integer(string='Refresh Interval (seconds)', default=300)
    
    # Customization
    custom_template = fields.Text(string='Custom Template')
    custom_style = fields.Text(string='Custom Style')
    
    # Options
    show_title = fields.Boolean(string='Show Title', default=True)
    collapsible = fields.Boolean(string='Collapsible', default=True)
    auto_refresh = fields.Boolean(string='Auto Refresh', default=True)


class ArchitectClientMessage(models.Model):
    _name = 'architect.client.message'
    _inherit = ['mail.thread']
    _description = 'Client Portal Message'
    _order = 'date desc, id desc'

    name = fields.Char(string='Subject', required=True)
    portal_id = fields.Many2one('architect.client.portal', string='Portal', required=True)
    project_id = fields.Many2one('architect.project', string='Project')
    
    # Message Details
    message_type = fields.Selection([
        ('update', 'Project Update'),
        ('notification', 'Notification'),
        ('request', 'Client Request'),
        ('response', 'Response'),
        ('other', 'Other')
    ], string='Message Type', required=True)
    
    content = fields.Html(string='Message Content', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    
    # Sender/Receiver
    sender_id = fields.Many2one('res.users', string='Sender', 
                               default=lambda self: self.env.user)
    recipient_ids = fields.Many2many('res.partner', string='Recipients')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('archived', 'Archived')
    ], string='Status', default='draft')
    
    # Tracking
    read_date = fields.Datetime(string='Read Date')
    read_by = fields.Many2many('res.partner', 'message_read_rel', 
                              string='Read By')
    
    def action_send(self):
        """Send the message"""
        self.ensure_one()
        self.state = 'sent'
        self.message_post(body=_("Message sent to client portal."))
    
    def mark_as_read(self, partner_id):
        """Mark message as read by a specific partner"""
        self.ensure_one()
        if partner_id not in self.read_by.ids:
            self.write({
                'read_by': [(4, partner_id)],
                'state': 'read',
                'read_date': fields.Datetime.now()
            })


class ArchitectClientActivity(models.Model):
    _name = 'architect.client.activity'
    _description = 'Client Portal Activity'
    _order = 'date desc, id desc'

    portal_id = fields.Many2one('architect.client.portal', string='Portal', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    
    # Activity Details
    activity_type = fields.Selection([
        ('login', 'Portal Login'),
        ('view', 'View Content'),
        ('download', 'Download Document'),
        ('message', 'Send Message'),
        ('other', 'Other Activity')
    ], string='Activity Type', required=True)
    
    description = fields.Text(string='Description')
    ip_address = fields.Char(string='IP Address')
    user_agent = fields.Char(string='User Agent')
    
    # Related Records
    project_id = fields.Many2one('architect.project', string='Related Project')
    document_id = fields.Many2one('ir.attachment', string='Related Document')
    
    def log_activity(self, portal_id, activity_type, description=False, **kwargs):
        """Log a new portal activity"""
        return self.create({
            'portal_id': portal_id,
            'activity_type': activity_type,
            'description': description,
            **kwargs
        })
