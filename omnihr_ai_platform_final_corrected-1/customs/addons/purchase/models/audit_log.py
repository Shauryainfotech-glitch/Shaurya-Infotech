from odoo import api, fields, models, _

class PurchaseAIRequestLog(models.Model):
    _name = 'purchase.ai.request.log'
    _description = 'AI Request and Response Audit Log'
    _order = 'timestamp desc'
    _rec_name = 'display_name'

    # Service information
    service_id = fields.Many2one('purchase.ai.service', 'AI Service', ondelete='set null')
    provider = fields.Char('Provider', related='service_id.provider', store=True)
    usage_type = fields.Char('Usage Type', related='service_id.usage_type', store=True)
    
    # Request details
    request_payload = fields.Text('Request Payload')
    response_payload = fields.Text('Response Payload')
    success = fields.Boolean('Success', default=True)
    error_message = fields.Text('Error Message')
    
    # Metadata
    timestamp = fields.Datetime('Timestamp', default=fields.Datetime.now, required=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    
    # Performance metrics
    response_time = fields.Float('Response Time (seconds)')
    tokens_used = fields.Integer('Tokens Used')
    cost = fields.Float('Cost')
    
    # Related record information
    model_name = fields.Char('Related Model')
    record_id = fields.Integer('Related Record ID')
    
    # Computed fields
    display_name = fields.Char('Display Name', compute='_compute_display_name', store=True)
    status_color = fields.Integer('Status Color', compute='_compute_status_color')

    @api.depends('provider', 'usage_type', 'timestamp', 'success')
    def _compute_display_name(self):
        for record in self:
            status = "✓" if record.success else "✗"
            provider = record.provider or "Unknown"
            usage = record.usage_type or "Unknown"
            timestamp = record.timestamp.strftime('%Y-%m-%d %H:%M') if record.timestamp else ""
            record.display_name = f"{status} {provider} - {usage} ({timestamp})"

    @api.depends('success')
    def _compute_status_color(self):
        for record in self:
            record.status_color = 10 if record.success else 1  # Green for success, red for failure

    def action_view_related_record(self):
        """View the related record if available"""
        if self.model_name and self.record_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Related Record'),
                'res_model': self.model_name,
                'res_id': self.record_id,
                'view_mode': 'form',
                'target': 'current',
            }
        return False

    @api.model
    def get_usage_statistics(self, days=30):
        """Get usage statistics for the last N days"""
        from datetime import timedelta
        
        cutoff_date = fields.Datetime.now() - timedelta(days=days)
        logs = self.search([('timestamp', '>=', cutoff_date)])
        
        stats = {
            'total_requests': len(logs),
            'successful_requests': len(logs.filtered('success')),
            'failed_requests': len(logs.filtered(lambda l: not l.success)),
            'total_tokens': sum(logs.mapped('tokens_used')),
            'total_cost': sum(logs.mapped('cost')),
            'avg_response_time': sum(logs.mapped('response_time')) / len(logs) if logs else 0,
            'by_provider': {},
            'by_usage_type': {},
        }
        
        # Group by provider
        for provider in logs.mapped('provider'):
            provider_logs = logs.filtered(lambda l: l.provider == provider)
            stats['by_provider'][provider] = {
                'requests': len(provider_logs),
                'success_rate': len(provider_logs.filtered('success')) / len(provider_logs) * 100 if provider_logs else 0,
                'avg_response_time': sum(provider_logs.mapped('response_time')) / len(provider_logs) if provider_logs else 0,
                'total_cost': sum(provider_logs.mapped('cost')),
            }
        
        # Group by usage type
        for usage_type in logs.mapped('usage_type'):
            usage_logs = logs.filtered(lambda l: l.usage_type == usage_type)
            stats['by_usage_type'][usage_type] = {
                'requests': len(usage_logs),
                'success_rate': len(usage_logs.filtered('success')) / len(usage_logs) * 100 if usage_logs else 0,
                'avg_response_time': sum(usage_logs.mapped('response_time')) / len(usage_logs) if usage_logs else 0,
                'total_cost': sum(usage_logs.mapped('cost')),
            }
        
        return stats

    @api.model
    def cleanup_old_logs(self, days=365):
        """Clean up logs older than specified days"""
        from datetime import timedelta
        
        cutoff_date = fields.Datetime.now() - timedelta(days=days)
        old_logs = self.search([('timestamp', '<', cutoff_date)])
        count = len(old_logs)
        old_logs.unlink()
        
        return count 