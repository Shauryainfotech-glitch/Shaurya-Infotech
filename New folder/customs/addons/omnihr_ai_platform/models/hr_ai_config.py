from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import json
import logging

_logger = logging.getLogger(__name__)

class HRAdvancedAIConfig(models.Model):
    _name = 'hr.advanced.ai.config'
    _description = 'Advanced AI Configuration for HR System'
    _rec_name = 'name'
    
    name = fields.Char('Configuration Name', required=True, default='Default AI Config')
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    
    # Multi-Provider Settings
    provider_priority = fields.Text(
        'AI Provider Priority Matrix',
        help='JSON configuration for task-based provider selection',
        default='{"recruitment": ["openai", "claude"], "analysis": ["claude", "gemini"], "conversation": ["claude", "openai"]}'
    )
    enable_multi_provider = fields.Boolean('Enable Multi-Provider Mode', default=True)
    
    # Advanced Features
    enable_consensus_mode = fields.Boolean('Enable Multi-AI Consensus', default=True)
    consensus_threshold = fields.Float(
        'Consensus Agreement Threshold',
        default=0.8,
        help='Minimum agreement percentage required for consensus decisions'
    )
    
    # Performance Optimization
    enable_caching = fields.Boolean('Enable AI Response Caching', default=True)
    cache_duration = fields.Integer('Cache Duration (hours)', default=24)
    max_concurrent_requests = fields.Integer('Max Concurrent AI Requests', default=10)
    
    # Cost Management
    monthly_budget_limit = fields.Float('Monthly AI Budget Limit ($)', default=1000.0)
    cost_alert_threshold = fields.Float('Budget Alert Threshold (%)', default=80.0)
    current_month_usage = fields.Float('Current Month Usage ($)', readonly=True)
    
    # Quality Assurance
    enable_response_validation = fields.Boolean('Enable Response Quality Validation', default=True)
    min_confidence_score = fields.Float('Minimum Confidence Score', default=0.75)
    enable_human_review = fields.Boolean('Enable Human Review for Critical Decisions', default=True)
    
    # Monitoring & Logging
    enable_detailed_logging = fields.Boolean('Enable Detailed AI Logging', default=True)
    log_retention_days = fields.Integer('Log Retention Days', default=90)
    
    @api.constrains('consensus_threshold')
    def _check_consensus_threshold(self):
        for record in self:
            if not 0.5 <= record.consensus_threshold <= 1.0:
                raise ValidationError(_('Consensus threshold must be between 0.5 and 1.0'))
    
    @api.constrains('provider_priority')
    def _check_provider_priority_json(self):
        for record in self:
            if record.provider_priority:
                try:
                    json.loads(record.provider_priority)
                except json.JSONDecodeError:
                    raise ValidationError(_('Provider priority must be valid JSON'))
    
    def get_provider_priority(self, task_type):
        """Get provider priority for specific task type"""
        try:
            priority_dict = json.loads(self.provider_priority or '{}')
            return priority_dict.get(task_type, ['openai'])
        except json.JSONDecodeError:
            _logger.warning(f"Invalid JSON in provider_priority for config {self.name}")
            return ['openai']
    
    def check_budget_limit(self, proposed_cost):
        """Check if proposed cost exceeds budget limits"""
        if self.monthly_budget_limit > 0:
            projected_usage = self.current_month_usage + proposed_cost
            if projected_usage > self.monthly_budget_limit:
                raise UserError(_(
                    'Proposed AI operation would exceed monthly budget limit. '
                    f'Current usage: ${self.current_month_usage:.2f}, '
                    f'Limit: ${self.monthly_budget_limit:.2f}'
                ))
    
    def update_usage_cost(self, cost):
        """Update current month usage cost"""
        self.current_month_usage += cost
        
        # Check alert threshold
        if self.cost_alert_threshold > 0:
            usage_percentage = (self.current_month_usage / self.monthly_budget_limit) * 100
            if usage_percentage >= self.cost_alert_threshold:
                self._send_budget_alert(usage_percentage)
    
    def _send_budget_alert(self, usage_percentage):
        """Send budget alert notification"""
        self.env['mail.mail'].create({
            'subject': f'AI Budget Alert - {usage_percentage:.1f}% Used',
            'body_html': f'''
                <p>AI Budget Alert for {self.company_id.name}</p>
                <p>Current usage: ${self.current_month_usage:.2f} ({usage_percentage:.1f}%)</p>
                <p>Monthly limit: ${self.monthly_budget_limit:.2f}</p>
            ''',
            'email_to': self.env.user.email,
        }).send() 