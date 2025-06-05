from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PurchaseAISettings(models.Model):
    _name = 'purchase.ai.settings'
    _description = 'AI Settings for Purchase Management'
    _rec_name = 'name'

    name = fields.Char('Configuration Name', required=True, default='AI Settings')
    
    # Risk and approval thresholds
    risk_threshold = fields.Float('Risk Threshold', default=0.7, 
                                 help="Risk score above which manual approval is required (0-1)")
    auto_approve_threshold = fields.Float('Auto-Approve Threshold', default=0.3,
                                         help="Risk score below which vendors are auto-approved (0-1)")
    
    # Vendor suggestion settings
    vendor_suggestion_limit = fields.Integer('Max Vendor Suggestions', default=5,
                                           help="Maximum number of vendor suggestions to generate")
    suggestion_refresh_hours = fields.Integer('Suggestion Refresh Hours', default=24,
                                            help="Hours between automatic suggestion updates")
    
    # AI behavior settings
    enable_continuous_learning = fields.Boolean('Enable Continuous Learning', default=True,
                                               help="Allow AI to learn from user feedback")
    ai_confidence_threshold = fields.Float('AI Confidence Threshold', default=0.6,
                                          help="Minimum AI confidence for suggestions (0-1)")
    
    # Caching settings
    cache_ai_responses = fields.Boolean('Cache AI Responses', default=True,
                                       help="Cache AI responses to reduce API calls")
    cache_duration_hours = fields.Integer('Cache Duration (Hours)', default=24,
                                         help="How long to cache AI responses")
    
    # Performance settings
    max_concurrent_ai_calls = fields.Integer('Max Concurrent AI Calls', default=5,
                                           help="Maximum number of concurrent AI API calls")
    ai_timeout_seconds = fields.Integer('AI Timeout (Seconds)', default=30,
                                       help="Timeout for AI API calls")
    
    # Cost management
    daily_ai_budget = fields.Float('Daily AI Budget', default=100.0,
                                  help="Maximum daily spending on AI services")
    monthly_ai_budget = fields.Float('Monthly AI Budget', default=2000.0,
                                    help="Maximum monthly spending on AI services")
    
    # Notification settings
    notify_high_risk_vendors = fields.Boolean('Notify High Risk Vendors', default=True)
    notify_ai_failures = fields.Boolean('Notify AI Failures', default=True)
    notify_budget_exceeded = fields.Boolean('Notify Budget Exceeded', default=True)
    
    # Advanced settings
    enable_market_analysis = fields.Boolean('Enable Market Analysis', default=True,
                                           help="Include market analysis in vendor suggestions")
    enable_document_analysis = fields.Boolean('Enable Document Analysis', default=True,
                                             help="Analyze vendor documents with AI")
    enable_price_prediction = fields.Boolean('Enable Price Prediction', default=True,
                                            help="Use AI for price prediction")
    
    # Data retention
    log_retention_days = fields.Integer('Log Retention Days', default=365,
                                       help="Days to retain AI request logs")
    suggestion_retention_days = fields.Integer('Suggestion Retention Days', default=90,
                                              help="Days to retain old vendor suggestions")

    @api.constrains('risk_threshold', 'auto_approve_threshold')
    def _check_thresholds(self):
        for record in self:
            if not 0.0 <= record.risk_threshold <= 1.0:
                raise ValidationError(_("Risk threshold must be between 0.0 and 1.0"))
            if not 0.0 <= record.auto_approve_threshold <= 1.0:
                raise ValidationError(_("Auto-approve threshold must be between 0.0 and 1.0"))
            if record.auto_approve_threshold >= record.risk_threshold:
                raise ValidationError(_("Auto-approve threshold must be less than risk threshold"))

    @api.constrains('ai_confidence_threshold')
    def _check_confidence_threshold(self):
        for record in self:
            if not 0.0 <= record.ai_confidence_threshold <= 1.0:
                raise ValidationError(_("AI confidence threshold must be between 0.0 and 1.0"))

    @api.model
    def get_settings(self):
        """Get current AI settings (singleton pattern)"""
        settings = self.search([], limit=1)
        if not settings:
            settings = self.create({'name': 'Default AI Settings'})
        return settings

    def action_test_ai_services(self):
        """Test all configured AI services"""
        ai_services = self.env['purchase.ai.service'].search([('active', '=', True)])
        
        results = []
        for service in ai_services:
            try:
                result = service.action_test_connection()
                results.append(f"✓ {service.name}: Connection successful")
            except Exception as e:
                results.append(f"✗ {service.name}: {str(e)}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Services Test Results'),
                'message': '\n'.join(results),
                'type': 'info',
                'sticky': True,
            }
        }

    def action_clear_cache(self):
        """Clear all AI response cache"""
        cache_records = self.env['ai.response.cache'].search([])
        count = len(cache_records)
        cache_records.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cache Cleared'),
                'message': _('Cleared %d cached AI responses') % count,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cleanup_old_data(self):
        """Cleanup old logs and suggestions"""
        # Cleanup old logs
        cutoff_date = fields.Datetime.now() - timedelta(days=self.log_retention_days)
        old_logs = self.env['purchase.ai.request.log'].search([
            ('timestamp', '<', cutoff_date)
        ])
        log_count = len(old_logs)
        old_logs.unlink()
        
        # Cleanup old suggestions
        suggestion_cutoff = fields.Datetime.now() - timedelta(days=self.suggestion_retention_days)
        old_suggestions = self.env['purchase.vendor.suggestion'].search([
            ('last_updated', '<', suggestion_cutoff)
        ])
        suggestion_count = len(old_suggestions)
        old_suggestions.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Data Cleanup Complete'),
                'message': _('Removed %d old logs and %d old suggestions') % (log_count, suggestion_count),
                'type': 'success',
                'sticky': False,
            }
        }


class VendorScoringWeights(models.Model):
    _name = 'vendor.scoring.weights'
    _description = 'Vendor Scoring Weights Configuration'
    _rec_name = 'name'

    name = fields.Char('Configuration Name', required=True, default='Default Weights')
    
    # Scoring weights (must sum to 1.0)
    price_weight = fields.Float('Price Weight', default=0.25, 
                               help="Weight for price competitiveness (0-1)")
    quality_weight = fields.Float('Quality Weight', default=0.25,
                                 help="Weight for quality history (0-1)")
    delivery_weight = fields.Float('Delivery Weight', default=0.20,
                                  help="Weight for delivery reliability (0-1)")
    relationship_weight = fields.Float('Relationship Weight', default=0.15,
                                      help="Weight for relationship strength (0-1)")
    compliance_weight = fields.Float('Compliance Weight', default=0.15,
                                    help="Weight for compliance rating (0-1)")
    
    # Additional weights for advanced scoring
    capacity_weight = fields.Float('Capacity Weight', default=0.0,
                                  help="Weight for capacity match (0-1)")
    geographic_weight = fields.Float('Geographic Weight', default=0.0,
                                    help="Weight for geographic proximity (0-1)")
    payment_terms_weight = fields.Float('Payment Terms Weight', default=0.0,
                                       help="Weight for payment terms (0-1)")
    
    total_weight = fields.Float('Total Weight', compute='_compute_total_weight', store=True)
    active = fields.Boolean('Active', default=True)

    @api.depends('price_weight', 'quality_weight', 'delivery_weight', 
                 'relationship_weight', 'compliance_weight', 'capacity_weight',
                 'geographic_weight', 'payment_terms_weight')
    def _compute_total_weight(self):
        for record in self:
            record.total_weight = (
                record.price_weight + record.quality_weight + record.delivery_weight +
                record.relationship_weight + record.compliance_weight + record.capacity_weight +
                record.geographic_weight + record.payment_terms_weight
            )

    @api.constrains('price_weight', 'quality_weight', 'delivery_weight', 
                    'relationship_weight', 'compliance_weight', 'capacity_weight',
                    'geographic_weight', 'payment_terms_weight')
    def _check_weights(self):
        for record in self:
            weights = [
                record.price_weight, record.quality_weight, record.delivery_weight,
                record.relationship_weight, record.compliance_weight, record.capacity_weight,
                record.geographic_weight, record.payment_terms_weight
            ]
            
            # Check individual weights are between 0 and 1
            for weight in weights:
                if not 0.0 <= weight <= 1.0:
                    raise ValidationError(_("All weights must be between 0.0 and 1.0"))
            
            # Check total weight is approximately 1.0 (allow small floating point errors)
            total = sum(weights)
            if not 0.99 <= total <= 1.01:
                raise ValidationError(_("Total weights must sum to 1.0 (currently: %.3f)") % total)

    def action_normalize_weights(self):
        """Normalize weights to sum to 1.0"""
        total = self.total_weight
        if total > 0:
            self.write({
                'price_weight': self.price_weight / total,
                'quality_weight': self.quality_weight / total,
                'delivery_weight': self.delivery_weight / total,
                'relationship_weight': self.relationship_weight / total,
                'compliance_weight': self.compliance_weight / total,
                'capacity_weight': self.capacity_weight / total,
                'geographic_weight': self.geographic_weight / total,
                'payment_terms_weight': self.payment_terms_weight / total,
            })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Weights Normalized'),
                'message': _('All weights have been normalized to sum to 1.0'),
                'type': 'success',
                'sticky': False,
            }
        } 