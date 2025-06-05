from datetime import timedelta
from odoo import api, fields, models, _

class AIResponseCache(models.Model):
    _name = 'ai.response.cache'
    _description = 'AI Response Cache'
    _order = 'create_date desc'

    cache_key = fields.Char('Cache Key', required=True, index=True)
    response_data = fields.Text('Response Data', required=True)
    expiry_date = fields.Datetime('Expiry Date', required=True, index=True)
    provider = fields.Char('AI Provider')
    usage_type = fields.Char('Usage Type')
    hit_count = fields.Integer('Hit Count', default=0)
    last_accessed = fields.Datetime('Last Accessed', default=fields.Datetime.now)
    
    @api.model
    def cleanup_expired(self):
        """Remove expired cache entries"""
        expired = self.search([('expiry_date', '<', fields.Datetime.now())])
        count = len(expired)
        expired.unlink()
        return count

    def increment_hit_count(self):
        """Increment hit count when cache is accessed"""
        self.hit_count += 1
        self.last_accessed = fields.Datetime.now() 