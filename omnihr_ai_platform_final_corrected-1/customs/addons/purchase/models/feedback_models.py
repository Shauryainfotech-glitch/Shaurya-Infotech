from odoo import api, fields, models, _

class VendorSuggestionFeedback(models.Model):
    _name = 'vendor.suggestion.feedback'
    _description = 'Vendor Suggestion Feedback for Continuous Learning'
    _order = 'feedback_date desc'

    suggestion_id = fields.Many2one('purchase.vendor.suggestion', 'Suggestion', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', 'Vendor', related='suggestion_id.vendor_id', store=True)
    product_id = fields.Many2one('product.product', 'Product', related='suggestion_id.product_id', store=True)
    
    # Feedback details
    rating = fields.Selection([
        ('positive', 'Positive - Good suggestion'),
        ('negative', 'Negative - Poor suggestion'),
        ('neutral', 'Neutral - Average suggestion'),
    ], required=True, string='Rating')
    
    comment = fields.Text('Comment')
    feedback_date = fields.Datetime('Feedback Date', default=fields.Datetime.now, required=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user, required=True)
    
    # Detailed feedback scores (optional)
    price_satisfaction = fields.Selection([
        ('1', 'Very Poor'),
        ('2', 'Poor'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent'),
    ], string='Price Satisfaction')
    
    quality_satisfaction = fields.Selection([
        ('1', 'Very Poor'),
        ('2', 'Poor'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent'),
    ], string='Quality Satisfaction')
    
    delivery_satisfaction = fields.Selection([
        ('1', 'Very Poor'),
        ('2', 'Poor'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent'),
    ], string='Delivery Satisfaction')
    
    # Context information
    purchase_order_id = fields.Many2one('purchase.order', 'Related Purchase Order')
    actual_price = fields.Float('Actual Price Paid')
    actual_delivery_days = fields.Integer('Actual Delivery Days')
    
    # Learning flags
    used_for_learning = fields.Boolean('Used for Learning', default=False)
    learning_weight = fields.Float('Learning Weight', default=1.0, 
                                  help="Weight of this feedback for learning algorithms")

    @api.model
    def create_from_purchase_order(self, purchase_order):
        """Create feedback records from completed purchase orders"""
        feedback_records = []
        
        for line in purchase_order.order_line:
            # Find related suggestion
            suggestion = self.env['purchase.vendor.suggestion'].search([
                ('vendor_id', '=', purchase_order.partner_id.id),
                ('product_id', '=', line.product_id.id),
            ], limit=1)
            
            if suggestion:
                # Calculate satisfaction scores based on actual vs predicted
                price_score = self._calculate_price_satisfaction(
                    suggestion.avg_price, line.price_unit
                )
                
                delivery_score = self._calculate_delivery_satisfaction(
                    suggestion.avg_delivery_time, 
                    self._get_actual_delivery_days(purchase_order)
                )
                
                feedback_data = {
                    'suggestion_id': suggestion.id,
                    'purchase_order_id': purchase_order.id,
                    'actual_price': line.price_unit,
                    'actual_delivery_days': self._get_actual_delivery_days(purchase_order),
                    'price_satisfaction': str(price_score),
                    'delivery_satisfaction': str(delivery_score),
                    'rating': self._determine_overall_rating(price_score, delivery_score),
                    'comment': f'Auto-generated feedback from PO {purchase_order.name}',
                }
                
                feedback_records.append(self.create(feedback_data))
        
        return feedback_records

    def _calculate_price_satisfaction(self, predicted_price, actual_price):
        """Calculate price satisfaction score (1-5)"""
        if not predicted_price or predicted_price == 0:
            return 3  # Neutral
        
        ratio = actual_price / predicted_price
        
        if ratio <= 0.8:  # 20% cheaper than predicted
            return 5
        elif ratio <= 0.9:  # 10% cheaper
            return 4
        elif ratio <= 1.1:  # Within 10%
            return 3
        elif ratio <= 1.2:  # 20% more expensive
            return 2
        else:  # More than 20% expensive
            return 1

    def _calculate_delivery_satisfaction(self, predicted_days, actual_days):
        """Calculate delivery satisfaction score (1-5)"""
        if not predicted_days or predicted_days == 0:
            return 3  # Neutral
        
        if actual_days <= predicted_days:
            return 5  # On time or early
        elif actual_days <= predicted_days * 1.1:
            return 4  # Slightly late
        elif actual_days <= predicted_days * 1.2:
            return 3  # Moderately late
        elif actual_days <= predicted_days * 1.5:
            return 2  # Significantly late
        else:
            return 1  # Very late

    def _get_actual_delivery_days(self, purchase_order):
        """Calculate actual delivery days"""
        if purchase_order.effective_date and purchase_order.date_order:
            return (purchase_order.effective_date - purchase_order.date_order).days
        return 0

    def _determine_overall_rating(self, price_score, delivery_score):
        """Determine overall rating based on individual scores"""
        avg_score = (price_score + delivery_score) / 2
        
        if avg_score >= 4:
            return 'positive'
        elif avg_score >= 3:
            return 'neutral'
        else:
            return 'negative'

    @api.model
    def get_learning_data(self, limit=1000):
        """Get feedback data for machine learning"""
        feedback_records = self.search([
            ('used_for_learning', '=', False)
        ], limit=limit)
        
        learning_data = []
        for feedback in feedback_records:
            data_point = {
                'vendor_id': feedback.vendor_id.id,
                'product_id': feedback.product_id.id,
                'rating': feedback.rating,
                'price_satisfaction': int(feedback.price_satisfaction) if feedback.price_satisfaction else 3,
                'quality_satisfaction': int(feedback.quality_satisfaction) if feedback.quality_satisfaction else 3,
                'delivery_satisfaction': int(feedback.delivery_satisfaction) if feedback.delivery_satisfaction else 3,
                'actual_price': feedback.actual_price,
                'actual_delivery_days': feedback.actual_delivery_days,
                'learning_weight': feedback.learning_weight,
                'feedback_date': feedback.feedback_date.isoformat(),
            }
            learning_data.append(data_point)
        
        # Mark as used for learning
        feedback_records.write({'used_for_learning': True})
        
        return learning_data

    def action_mark_for_relearning(self):
        """Mark feedback for re-learning (useful when algorithms improve)"""
        self.write({'used_for_learning': False})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Marked for Re-learning'),
                'message': _('Selected feedback records marked for re-learning'),
                'type': 'success',
                'sticky': False,
            }
        }


class AIPerformanceMetrics(models.Model):
    _name = 'ai.performance.metrics'
    _description = 'AI Performance Metrics Tracking'
    _order = 'date desc'

    date = fields.Date('Date', required=True, default=fields.Date.today)
    
    # Suggestion accuracy metrics
    total_suggestions = fields.Integer('Total Suggestions')
    positive_feedback = fields.Integer('Positive Feedback')
    negative_feedback = fields.Integer('Negative Feedback')
    neutral_feedback = fields.Integer('Neutral Feedback')
    
    accuracy_rate = fields.Float('Accuracy Rate (%)', compute='_compute_accuracy_rate', store=True)
    
    # Cost and usage metrics
    total_ai_calls = fields.Integer('Total AI Calls')
    successful_calls = fields.Integer('Successful Calls')
    failed_calls = fields.Integer('Failed Calls')
    total_cost = fields.Float('Total Cost')
    avg_response_time = fields.Float('Avg Response Time (seconds)')
    
    # Provider breakdown
    claude_calls = fields.Integer('Claude Calls')
    openai_calls = fields.Integer('OpenAI Calls')
    gemini_calls = fields.Integer('Gemini Calls')
    
    # Usage type breakdown
    vendor_suggestion_calls = fields.Integer('Vendor Suggestion Calls')
    risk_assessment_calls = fields.Integer('Risk Assessment Calls')
    document_analysis_calls = fields.Integer('Document Analysis Calls')
    
    @api.depends('positive_feedback', 'negative_feedback', 'neutral_feedback')
    def _compute_accuracy_rate(self):
        for record in self:
            total_feedback = record.positive_feedback + record.negative_feedback + record.neutral_feedback
            if total_feedback > 0:
                record.accuracy_rate = (record.positive_feedback / total_feedback) * 100
            else:
                record.accuracy_rate = 0.0

    @api.model
    def generate_daily_metrics(self, date=None):
        """Generate metrics for a specific date"""
        if not date:
            date = fields.Date.today()
        
        # Check if metrics already exist for this date
        existing = self.search([('date', '=', date)])
        if existing:
            existing.unlink()
        
        # Get feedback data for the date
        feedback_data = self.env['vendor.suggestion.feedback'].search([
            ('feedback_date', '>=', date),
            ('feedback_date', '<', date + timedelta(days=1))
        ])
        
        # Get AI log data for the date
        log_data = self.env['purchase.ai.request.log'].search([
            ('timestamp', '>=', date),
            ('timestamp', '<', date + timedelta(days=1))
        ])
        
        # Calculate metrics
        metrics_data = {
            'date': date,
            'total_suggestions': len(feedback_data),
            'positive_feedback': len(feedback_data.filtered(lambda f: f.rating == 'positive')),
            'negative_feedback': len(feedback_data.filtered(lambda f: f.rating == 'negative')),
            'neutral_feedback': len(feedback_data.filtered(lambda f: f.rating == 'neutral')),
            'total_ai_calls': len(log_data),
            'successful_calls': len(log_data.filtered('success')),
            'failed_calls': len(log_data.filtered(lambda l: not l.success)),
            'total_cost': sum(log_data.mapped('cost')),
            'avg_response_time': sum(log_data.mapped('response_time')) / len(log_data) if log_data else 0,
            'claude_calls': len(log_data.filtered(lambda l: l.provider == 'claude')),
            'openai_calls': len(log_data.filtered(lambda l: l.provider == 'openai')),
            'gemini_calls': len(log_data.filtered(lambda l: l.provider == 'gemini')),
            'vendor_suggestion_calls': len(log_data.filtered(lambda l: l.usage_type == 'vendor_suggestion')),
            'risk_assessment_calls': len(log_data.filtered(lambda l: l.usage_type == 'risk_assessment')),
            'document_analysis_calls': len(log_data.filtered(lambda l: l.usage_type == 'document_analysis')),
        }
        
        return self.create(metrics_data)

    @api.model
    def get_performance_trends(self, days=30):
        """Get performance trends for the last N days"""
        from datetime import timedelta
        
        end_date = fields.Date.today()
        start_date = end_date - timedelta(days=days)
        
        metrics = self.search([
            ('date', '>=', start_date),
            ('date', '<=', end_date)
        ], order='date asc')
        
        trends = {
            'dates': metrics.mapped('date'),
            'accuracy_rates': metrics.mapped('accuracy_rate'),
            'total_costs': metrics.mapped('total_cost'),
            'response_times': metrics.mapped('avg_response_time'),
            'success_rates': [
                (m.successful_calls / m.total_ai_calls * 100) if m.total_ai_calls > 0 else 0
                for m in metrics
            ]
        }
        
        return trends 