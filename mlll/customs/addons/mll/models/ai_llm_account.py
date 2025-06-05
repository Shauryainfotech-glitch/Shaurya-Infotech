from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests
import json

class AiLlmAccount(models.Model):
    _name = 'ai.llm.account'
    _description = 'AI LLM Account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    
    name = fields.Char(string='Account Name', required=True, tracking=True)
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    provider_id = fields.Many2one(
        'ai.llm.provider',
        string='Provider',
        required=True,
        tracking=True
    )
    
    api_key = fields.Char(
        string='API Key',
        required=True,
        groups='mll.group_ai_admin'
    )
    
    user_ids = fields.Many2many(
        'res.users',
        'ai_llm_account_users_rel',
        'account_id',
        'user_id',
        string='Allowed Users',
        help='Users who can use this AI account'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    usage_limit = fields.Integer(
        string='Monthly Usage Limit',
        default=10000,
        help='Maximum API calls per month (0 = unlimited)'
    )
    current_usage = fields.Integer(
        string='Current Month Usage',
        compute='_compute_current_usage'
    )
    
    conversation_ids = fields.One2many(
        'ai.llm.conversation',
        'account_id',
        string='Conversations'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ], string='Status', default='draft', tracking=True)
    
    @api.depends('name', 'provider_id.name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.provider_id.name})"
    
    @api.depends('conversation_ids.create_date')
    def _compute_current_usage(self):
        """Calculate current month's API usage"""
        for record in self:
            # Implementation for usage calculation
            record.current_usage = 0  # Placeholder
    
    def action_activate(self):
        """Activate the AI account after validation"""
        self.ensure_one()
        if self._test_connection():
            self.state = 'active'
        else:
            raise ValidationError("Failed to connect to AI provider. Please check your credentials.")
    
    def action_suspend(self):
        """Suspend the AI account"""
        self.state = 'suspended'
    
    def _test_connection(self):
        """Test connection to AI provider"""
        # Implementation depends on provider
        return True  # Placeholder
    
    @api.model
    def get_available_account(self, user=None):
        """Get an available AI account for the user"""
        if not user:
            user = self.env.user
        
        domain = [
            ('state', '=', 'active'),
            '|',
            ('user_ids', '=', False),
            ('user_ids', 'in', user.id),
            ('company_id', '=', user.company_id.id)
        ]
        
        accounts = self.search(domain)
        # Return account with lowest usage
        return accounts.sorted('current_usage')[:1]
