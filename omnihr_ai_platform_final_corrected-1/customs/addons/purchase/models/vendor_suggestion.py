import json
import logging
import numpy as np
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)

class VendorSuggestion(models.Model):
    _name = 'purchase.vendor.suggestion'
    _description = 'AI-Powered Vendor Suggestion with Detailed Scoring'
    _order = 'ai_score desc, create_date desc'

    # Core relationship fields
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, ondelete='cascade')
    
    # AI scoring
    ai_score = fields.Float('AI Confidence Score', required=True, help="Overall AI confidence score (0-1)")
    ai_reasoning = fields.Text('AI Reasoning', help="AI explanation for the suggestion")
    
    # Detailed scoring breakdown
    scoring_factors = fields.Json('Scoring Breakdown', default=lambda self: {
        'price_competitiveness': 0.0,
        'quality_history': 0.0,
        'delivery_reliability': 0.0,
        'relationship_score': 0.0,
        'compliance_rating': 0.0,
        'capacity_match': 0.0,
        'geographic_proximity': 0.0,
        'payment_terms': 0.0,
    })
    
    # Historical performance data
    historical_orders = fields.Integer('Historical Orders', compute='_compute_historical_data', store=True)
    avg_delivery_time = fields.Float('Avg Delivery Time (days)', compute='_compute_historical_data', store=True)
    on_time_delivery_rate = fields.Float('On-Time Delivery Rate (%)', compute='_compute_historical_data', store=True)
    quality_rating = fields.Float('Quality Rating', compute='_compute_historical_data', store=True)
    avg_price = fields.Float('Average Price', compute='_compute_historical_data', store=True)
    
    # Metadata
    last_updated = fields.Datetime('Last Updated', default=fields.Datetime.now)
    suggestion_context = fields.Json('Suggestion Context', help="Context data used for suggestion")
    confidence_level = fields.Selection([
        ('low', 'Low (< 0.3)'),
        ('medium', 'Medium (0.3-0.7)'),
        ('high', 'High (> 0.7)'),
    ], compute='_compute_confidence_level', store=True)
    
    # User feedback
    user_feedback = fields.Selection([
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ], string='User Feedback')
    feedback_comment = fields.Text('Feedback Comment')
    feedback_date = fields.Datetime('Feedback Date')
    feedback_user = fields.Many2one('res.users', string='Feedback User')
    
    # Status
    active = fields.Boolean('Active', default=True)
    suggestion_type = fields.Selection([
        ('automatic', 'Automatic AI Suggestion'),
        ('manual_request', 'Manual Request'),
        ('rfq_based', 'RFQ-Based'),
        ('market_analysis', 'Market Analysis'),
    ], default='automatic')

    @api.depends('ai_score')
    def _compute_confidence_level(self):
        """Compute confidence level based on AI score"""
        for record in self:
            if record.ai_score < 0.3:
                record.confidence_level = 'low'
            elif record.ai_score < 0.7:
                record.confidence_level = 'medium'
            else:
                record.confidence_level = 'high'

    @api.depends('vendor_id', 'product_id')
    def _compute_historical_data(self):
        """Compute historical performance data"""
        for record in self:
            if not record.vendor_id or not record.product_id:
                record.historical_orders = 0
                record.avg_delivery_time = 0.0
                record.on_time_delivery_rate = 0.0
                record.quality_rating = 0.0
                record.avg_price = 0.0
                continue
            
            # Get historical purchase orders
            purchase_lines = self.env['purchase.order.line'].search([
                ('partner_id', '=', record.vendor_id.id),
                ('product_id', '=', record.product_id.id),
                ('order_id.state', 'in', ['purchase', 'done']),
            ])
            
            record.historical_orders = len(purchase_lines)
            
            if purchase_lines:
                # Calculate average delivery time
                delivered_lines = purchase_lines.filtered(lambda l: l.order_id.effective_date)
                if delivered_lines:
                    delivery_times = []
                    for line in delivered_lines:
                        if line.order_id.date_order and line.order_id.effective_date:
                            delta = line.order_id.effective_date - line.order_id.date_order
                            delivery_times.append(delta.days)
                    
                    if delivery_times:
                        record.avg_delivery_time = sum(delivery_times) / len(delivery_times)
                        
                        # Calculate on-time delivery rate (assuming 30 days is expected)
                        on_time_count = sum(1 for days in delivery_times if days <= 30)
                        record.on_time_delivery_rate = (on_time_count / len(delivery_times)) * 100
                
                # Calculate average price
                prices = purchase_lines.mapped('price_unit')
                if prices:
                    record.avg_price = sum(prices) / len(prices)
                
                # Get quality rating from vendor feedback
                record.quality_rating = record._get_quality_rating()

    def _get_quality_rating(self):
        """Get quality rating from vendor feedback system"""
        # This would integrate with a vendor feedback/rating system
        # For now, return a computed value based on historical performance
        feedback_records = self.env['vendor.suggestion.feedback'].search([
            ('suggestion_id.vendor_id', '=', self.vendor_id.id),
            ('suggestion_id.product_id', '=', self.product_id.id),
            ('rating', '!=', False)
        ])
        
        if feedback_records:
            ratings = []
            for feedback in feedback_records:
                if feedback.rating == 'positive':
                    ratings.append(5.0)
                elif feedback.rating == 'neutral':
                    ratings.append(3.0)
                else:  # negative
                    ratings.append(1.0)
            
            return sum(ratings) / len(ratings) if ratings else 3.0
        
        return 3.0  # Default neutral rating

    @api.model
    def generate_suggestions_for_product(self, product_id, context=None):
        """Generate AI-powered vendor suggestions for a product"""
        product = self.env['product.product'].browse(product_id)
        if not product.exists():
            raise UserError(_("Product not found"))
        
        # Queue async suggestion generation
        self.with_delay().async_generate_suggestions(product_id, context or {})
        
        return True

    @job
    def async_generate_suggestions(self, product_id, context):
        """Async job to generate vendor suggestions"""
        try:
            product = self.env['product.product'].browse(product_id)
            
            # Get AI-powered suggestions
            suggestions = self._get_ai_suggestions(product, context)
            
            # Clear old suggestions for this product
            old_suggestions = self.search([('product_id', '=', product_id)])
            old_suggestions.unlink()
            
            # Create new suggestions
            for suggestion_data in suggestions:
                self.create(suggestion_data)
                
            _logger.info(f"Generated {len(suggestions)} suggestions for product {product.name}")
            
        except Exception as e:
            _logger.error(f"Failed to generate suggestions for product {product_id}: {e}")

    def _get_ai_suggestions(self, product, context):
        """Get AI-powered vendor suggestions"""
        # Prepare comprehensive prompt for AI
        prompt = self._prepare_suggestion_prompt(product, context)
        
        try:
            # Call AI service
            response = self.env['purchase.ai.service'].call_ai_service(
                'vendor_suggestion', prompt, context
            )
            
            # Parse AI response
            ai_suggestions = self._parse_ai_suggestions(response, product)
            
            # Enhance with historical data and scoring
            enhanced_suggestions = []
            for ai_suggestion in ai_suggestions:
                enhanced = self._enhance_suggestion_with_data(ai_suggestion, product, context)
                if enhanced:
                    enhanced_suggestions.append(enhanced)
            
            # Sort by AI score and limit results
            settings = self.env['purchase.ai.settings'].get_settings()
            enhanced_suggestions.sort(key=lambda x: x['ai_score'], reverse=True)
            
            return enhanced_suggestions[:settings.vendor_suggestion_limit]
            
        except Exception as e:
            _logger.error(f"AI suggestion generation failed: {e}")
            # Fallback to rule-based suggestions
            return self._get_fallback_suggestions(product, context)

    def _prepare_suggestion_prompt(self, product, context):
        """Prepare comprehensive prompt for AI vendor suggestion"""
        # Get product details
        product_info = {
            'name': product.name,
            'category': product.categ_id.name if product.categ_id else 'Unknown',
            'description': product.description or '',
            'standard_price': product.standard_price,
            'uom': product.uom_id.name if product.uom_id else '',
        }
        
        # Get historical vendor data
        historical_vendors = self._get_historical_vendors(product)
        
        # Get market context
        market_context = context.get('market_context', {})
        
        # Get company preferences
        company_prefs = self._get_company_preferences()
        
        prompt = f"""
        Suggest the best vendors for the following product procurement:
        
        PRODUCT INFORMATION:
        {json.dumps(product_info, indent=2)}
        
        HISTORICAL VENDOR PERFORMANCE:
        {json.dumps(historical_vendors, indent=2)}
        
        MARKET CONTEXT:
        {json.dumps(market_context, indent=2)}
        
        COMPANY PREFERENCES:
        {json.dumps(company_prefs, indent=2)}
        
        REQUIREMENTS:
        Please analyze and suggest the top vendors considering:
        
        1. Price competitiveness
        2. Quality track record
        3. Delivery reliability
        4. Compliance and certifications
        5. Geographic proximity
        6. Payment terms flexibility
        7. Capacity to handle volume
        8. Relationship strength
        
        For each suggested vendor, provide:
        - Vendor name and ID (if known)
        - Overall confidence score (0-1)
        - Detailed scoring breakdown for each factor (0-1)
        - Reasoning for the suggestion
        - Estimated price range
        - Delivery timeframe
        - Key strengths and potential risks
        
        Return response in JSON format:
        {{
            "suggestions": [
                {{
                    "vendor_name": "string",
                    "vendor_id": "integer or null",
                    "confidence_score": 0.0-1.0,
                    "scoring_factors": {{
                        "price_competitiveness": 0.0-1.0,
                        "quality_history": 0.0-1.0,
                        "delivery_reliability": 0.0-1.0,
                        "relationship_score": 0.0-1.0,
                        "compliance_rating": 0.0-1.0,
                        "capacity_match": 0.0-1.0,
                        "geographic_proximity": 0.0-1.0,
                        "payment_terms": 0.0-1.0
                    }},
                    "reasoning": "string",
                    "estimated_price_range": "string",
                    "delivery_timeframe": "string",
                    "strengths": ["list"],
                    "risks": ["list"]
                }}
            ]
        }}
        """
        
        return prompt

    def _get_historical_vendors(self, product):
        """Get historical vendor performance data"""
        # Get vendors who have supplied this product
        purchase_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            ('order_id.state', 'in', ['purchase', 'done']),
        ], limit=50)  # Limit for performance
        
        vendor_data = {}
        for line in purchase_lines:
            vendor_id = line.partner_id.id
            if vendor_id not in vendor_data:
                vendor_data[vendor_id] = {
                    'vendor_name': line.partner_id.name,
                    'vendor_id': vendor_id,
                    'orders': [],
                    'total_quantity': 0,
                    'avg_price': 0,
                    'delivery_performance': []
                }
            
            order_data = {
                'date': line.order_id.date_order.isoformat() if line.order_id.date_order else None,
                'quantity': line.product_qty,
                'price': line.price_unit,
                'delivery_date': line.order_id.effective_date.isoformat() if line.order_id.effective_date else None,
            }
            
            vendor_data[vendor_id]['orders'].append(order_data)
            vendor_data[vendor_id]['total_quantity'] += line.product_qty
        
        # Calculate aggregated metrics
        for vendor_id, data in vendor_data.items():
            if data['orders']:
                prices = [order['price'] for order in data['orders']]
                data['avg_price'] = sum(prices) / len(prices)
                
                # Calculate delivery performance
                delivered_orders = [order for order in data['orders'] if order['delivery_date']]
                if delivered_orders:
                    delivery_times = []
                    for order in delivered_orders:
                        if order['date'] and order['delivery_date']:
                            order_date = datetime.fromisoformat(order['date'].replace('Z', '+00:00'))
                            delivery_date = datetime.fromisoformat(order['delivery_date'].replace('Z', '+00:00'))
                            delivery_times.append((delivery_date - order_date).days)
                    
                    if delivery_times:
                        data['avg_delivery_days'] = sum(delivery_times) / len(delivery_times)
                        data['on_time_rate'] = sum(1 for days in delivery_times if days <= 30) / len(delivery_times)
        
        return list(vendor_data.values())

    def _get_company_preferences(self):
        """Get company procurement preferences"""
        company = self.env.company
        
        # Get vendor scoring weights
        scoring_weights = self.env['vendor.scoring.weights'].search([], limit=1)
        
        preferences = {
            'currency': company.currency_id.name,
            'country': company.country_id.name if company.country_id else '',
            'payment_terms': company.property_supplier_payment_term_id.name if company.property_supplier_payment_term_id else '',
        }
        
        if scoring_weights:
            preferences['scoring_weights'] = {
                'price_weight': scoring_weights.price_weight,
                'quality_weight': scoring_weights.quality_weight,
                'delivery_weight': scoring_weights.delivery_weight,
                'relationship_weight': scoring_weights.relationship_weight,
                'compliance_weight': scoring_weights.compliance_weight,
            }
        
        return preferences

    def _parse_ai_suggestions(self, ai_response, product):
        """Parse AI response into suggestion data"""
        try:
            content = ai_response.get('content', '{}')
            
            # Parse JSON response
            try:
                response_data = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in AI response")
            
            suggestions = response_data.get('suggestions', [])
            parsed_suggestions = []
            
            for suggestion in suggestions:
                # Find or create vendor
                vendor = self._find_or_suggest_vendor(suggestion)
                
                if vendor:
                    parsed_suggestions.append({
                        'vendor_id': vendor.id,
                        'ai_score': suggestion.get('confidence_score', 0.5),
                        'scoring_factors': suggestion.get('scoring_factors', {}),
                        'ai_reasoning': suggestion.get('reasoning', ''),
                        'suggestion_context': {
                            'estimated_price_range': suggestion.get('estimated_price_range', ''),
                            'delivery_timeframe': suggestion.get('delivery_timeframe', ''),
                            'strengths': suggestion.get('strengths', []),
                            'risks': suggestion.get('risks', []),
                            'ai_generated': True,
                        }
                    })
            
            return parsed_suggestions
            
        except Exception as e:
            _logger.error(f"Failed to parse AI suggestions: {e}")
            return []

    def _find_or_suggest_vendor(self, suggestion_data):
        """Find existing vendor or suggest creating new one"""
        vendor_name = suggestion_data.get('vendor_name', '')
        vendor_id = suggestion_data.get('vendor_id')
        
        # Try to find by ID first
        if vendor_id:
            vendor = self.env['res.partner'].browse(vendor_id)
            if vendor.exists():
                return vendor
        
        # Try to find by name
        if vendor_name:
            vendor = self.env['res.partner'].search([
                ('name', 'ilike', vendor_name),
                ('supplier_rank', '>', 0)
            ], limit=1)
            
            if vendor:
                return vendor
            
            # Suggest creating new vendor
            # For now, we'll skip unknown vendors
            # In a full implementation, this could trigger vendor creation workflow
            _logger.info(f"AI suggested unknown vendor: {vendor_name}")
        
        return None

    def _enhance_suggestion_with_data(self, suggestion_data, product, context):
        """Enhance AI suggestion with real data and calculations"""
        vendor_id = suggestion_data.get('vendor_id')
        if not vendor_id:
            return None
        
        vendor = self.env['res.partner'].browse(vendor_id)
        if not vendor.exists():
            return None
        
        # Calculate real scoring factors
        real_scoring = self._calculate_real_scoring_factors(vendor, product)
        
        # Merge AI scoring with real data
        ai_scoring = suggestion_data.get('scoring_factors', {})
        merged_scoring = {}
        
        for factor in ['price_competitiveness', 'quality_history', 'delivery_reliability', 
                      'relationship_score', 'compliance_rating', 'capacity_match', 
                      'geographic_proximity', 'payment_terms']:
            
            ai_score = ai_scoring.get(factor, 0.5)
            real_score = real_scoring.get(factor, 0.5)
            
            # Weight AI vs real data (70% real, 30% AI for factors with real data)
            if real_score > 0:
                merged_scoring[factor] = (real_score * 0.7) + (ai_score * 0.3)
            else:
                merged_scoring[factor] = ai_score
        
        # Calculate final AI score
        weights = self._get_scoring_weights()
        final_score = sum(merged_scoring[factor] * weights.get(factor, 0.125) 
                         for factor in merged_scoring)
        
        return {
            'product_id': product.id,
            'vendor_id': vendor_id,
            'ai_score': final_score,
            'scoring_factors': merged_scoring,
            'ai_reasoning': suggestion_data.get('ai_reasoning', ''),
            'suggestion_context': suggestion_data.get('suggestion_context', {}),
            'suggestion_type': 'automatic',
            'last_updated': fields.Datetime.now(),
        }

    def _calculate_real_scoring_factors(self, vendor, product):
        """Calculate real scoring factors based on historical data"""
        scoring = {}
        
        # Price competitiveness
        scoring['price_competitiveness'] = self._calculate_price_competitiveness(vendor, product)
        
        # Quality history
        scoring['quality_history'] = self._calculate_quality_score(vendor, product)
        
        # Delivery reliability
        scoring['delivery_reliability'] = self._calculate_delivery_score(vendor, product)
        
        # Relationship score
        scoring['relationship_score'] = self._calculate_relationship_score(vendor)
        
        # Compliance rating
        scoring['compliance_rating'] = self._calculate_compliance_score(vendor)
        
        # Capacity match
        scoring['capacity_match'] = self._calculate_capacity_score(vendor, product)
        
        # Geographic proximity
        scoring['geographic_proximity'] = self._calculate_geographic_score(vendor)
        
        # Payment terms
        scoring['payment_terms'] = self._calculate_payment_terms_score(vendor)
        
        return scoring

    def _calculate_price_competitiveness(self, vendor, product):
        """Calculate price competitiveness score"""
        # Get recent prices from this vendor
        recent_lines = self.env['purchase.order.line'].search([
            ('partner_id', '=', vendor.id),
            ('product_id', '=', product.id),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=365)),
        ], limit=10)
        
        if not recent_lines:
            return 0.5  # Neutral score for no data
        
        vendor_avg_price = sum(recent_lines.mapped('price_unit')) / len(recent_lines)
        
        # Get market average price
        all_recent_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=365)),
        ], limit=50)
        
        if not all_recent_lines:
            return 0.5
        
        market_avg_price = sum(all_recent_lines.mapped('price_unit')) / len(all_recent_lines)
        
        if market_avg_price == 0:
            return 0.5
        
        # Score: 1.0 = much cheaper, 0.5 = market average, 0.0 = much more expensive
        price_ratio = vendor_avg_price / market_avg_price
        
        if price_ratio <= 0.8:
            return 1.0  # 20% cheaper or more
        elif price_ratio <= 0.9:
            return 0.8  # 10-20% cheaper
        elif price_ratio <= 1.1:
            return 0.6  # Within 10% of market
        elif price_ratio <= 1.2:
            return 0.4  # 10-20% more expensive
        else:
            return 0.2  # More than 20% expensive

    def _calculate_quality_score(self, vendor, product):
        """Calculate quality score based on feedback and returns"""
        # Get feedback scores
        feedback_records = self.env['vendor.suggestion.feedback'].search([
            ('suggestion_id.vendor_id', '=', vendor.id),
            ('suggestion_id.product_id', '=', product.id),
        ])
        
        if feedback_records:
            positive_count = len(feedback_records.filtered(lambda f: f.rating == 'positive'))
            total_count = len(feedback_records)
            return positive_count / total_count if total_count > 0 else 0.5
        
        return 0.5  # Neutral score for no feedback

    def _calculate_delivery_score(self, vendor, product):
        """Calculate delivery reliability score"""
        # Get recent orders
        recent_orders = self.env['purchase.order'].search([
            ('partner_id', '=', vendor.id),
            ('order_line.product_id', '=', product.id),
            ('state', 'in', ['purchase', 'done']),
            ('date_order', '>=', fields.Datetime.now() - timedelta(days=365)),
        ])
        
        if not recent_orders:
            return 0.5
        
        on_time_count = 0
        total_count = 0
        
        for order in recent_orders:
            if order.effective_date and order.date_planned:
                total_count += 1
                if order.effective_date <= order.date_planned:
                    on_time_count += 1
        
        return on_time_count / total_count if total_count > 0 else 0.5

    def _calculate_relationship_score(self, vendor):
        """Calculate relationship strength score"""
        # Factors: years of relationship, order frequency, communication quality
        first_order = self.env['purchase.order'].search([
            ('partner_id', '=', vendor.id),
            ('state', 'in', ['purchase', 'done']),
        ], order='date_order asc', limit=1)
        
        if not first_order:
            return 0.3  # New vendor
        
        # Years of relationship
        years = (fields.Datetime.now() - first_order.date_order).days / 365.25
        
        # Order frequency (orders per year)
        total_orders = self.env['purchase.order'].search_count([
            ('partner_id', '=', vendor.id),
            ('state', 'in', ['purchase', 'done']),
        ])
        
        orders_per_year = total_orders / max(years, 1)
        
        # Score based on relationship length and frequency
        relationship_score = min(years / 5, 1.0) * 0.6  # Max 0.6 for 5+ years
        frequency_score = min(orders_per_year / 12, 1.0) * 0.4  # Max 0.4 for monthly orders
        
        return relationship_score + frequency_score

    def _calculate_compliance_score(self, vendor):
        """Calculate compliance score"""
        # This would integrate with compliance tracking system
        # For now, return a basic score based on vendor categories
        
        compliance_categories = ['ISO Certified', 'Quality Certified', 'Environmental Certified']
        vendor_categories = vendor.category_id.mapped('name')
        
        matches = sum(1 for cat in compliance_categories if any(cat in vc for vc in vendor_categories))
        
        return matches / len(compliance_categories) if compliance_categories else 0.5

    def _calculate_capacity_score(self, vendor, product):
        """Calculate capacity match score"""
        # Get recent order volumes
        recent_lines = self.env['purchase.order.line'].search([
            ('partner_id', '=', vendor.id),
            ('product_id', '=', product.id),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=180)),
        ])
        
        if not recent_lines:
            return 0.5
        
        max_quantity = max(recent_lines.mapped('product_qty'))
        avg_quantity = sum(recent_lines.mapped('product_qty')) / len(recent_lines)
        
        # Score based on demonstrated capacity
        if max_quantity >= 1000:
            return 1.0  # High capacity
        elif max_quantity >= 500:
            return 0.8
        elif max_quantity >= 100:
            return 0.6
        else:
            return 0.4

    def _calculate_geographic_score(self, vendor):
        """Calculate geographic proximity score"""
        company_country = self.env.company.country_id
        vendor_country = vendor.country_id
        
        if not company_country or not vendor_country:
            return 0.5
        
        if company_country == vendor_country:
            return 1.0  # Same country
        elif company_country.continent_id == vendor_country.continent_id:
            return 0.7  # Same continent
        else:
            return 0.3  # Different continent

    def _calculate_payment_terms_score(self, vendor):
        """Calculate payment terms flexibility score"""
        vendor_terms = vendor.property_supplier_payment_term_id
        company_preferred = self.env.company.property_supplier_payment_term_id
        
        if not vendor_terms:
            return 0.5
        
        if vendor_terms == company_preferred:
            return 1.0
        
        # Score based on payment term days
        vendor_days = vendor_terms.line_ids[0].days if vendor_terms.line_ids else 30
        
        if vendor_days >= 60:
            return 1.0  # Generous terms
        elif vendor_days >= 30:
            return 0.8
        elif vendor_days >= 15:
            return 0.6
        else:
            return 0.4

    def _get_scoring_weights(self):
        """Get scoring weights from settings"""
        weights = self.env['vendor.scoring.weights'].search([], limit=1)
        
        if weights:
            return {
                'price_competitiveness': weights.price_weight,
                'quality_history': weights.quality_weight,
                'delivery_reliability': weights.delivery_weight,
                'relationship_score': weights.relationship_weight,
                'compliance_rating': weights.compliance_weight,
                'capacity_match': 0.1,
                'geographic_proximity': 0.1,
                'payment_terms': 0.1,
            }
        
        # Default weights
        return {
            'price_competitiveness': 0.25,
            'quality_history': 0.25,
            'delivery_reliability': 0.20,
            'relationship_score': 0.15,
            'compliance_rating': 0.15,
            'capacity_match': 0.0,
            'geographic_proximity': 0.0,
            'payment_terms': 0.0,
        }

    def _get_fallback_suggestions(self, product, context):
        """Get fallback suggestions when AI fails"""
        # Rule-based fallback suggestions
        suggestions = []
        
        # Get vendors who have supplied this product before
        recent_vendors = self.env['purchase.order.line'].search([
            ('product_id', '=', product.id),
            ('order_id.state', 'in', ['purchase', 'done']),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=365)),
        ]).mapped('partner_id')
        
        for vendor in recent_vendors[:5]:  # Limit to top 5
            suggestions.append({
                'product_id': product.id,
                'vendor_id': vendor.id,
                'ai_score': 0.5,  # Neutral score
                'scoring_factors': {factor: 0.5 for factor in [
                    'price_competitiveness', 'quality_history', 'delivery_reliability',
                    'relationship_score', 'compliance_rating', 'capacity_match',
                    'geographic_proximity', 'payment_terms'
                ]},
                'ai_reasoning': 'Fallback suggestion based on historical orders',
                'suggestion_context': {'fallback': True},
                'suggestion_type': 'automatic',
                'last_updated': fields.Datetime.now(),
            })
        
        return suggestions

    def action_provide_feedback(self):
        """Open feedback wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Provide Feedback'),
            'res_model': 'vendor.suggestion.feedback.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_suggestion_id': self.id}
        }

    def action_create_rfq(self):
        """Create RFQ for this vendor and product"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create RFQ'),
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_partner_id': self.vendor_id.id,
                'default_order_line': [(0, 0, {
                    'product_id': self.product_id.id,
                    'name': self.product_id.name,
                    'product_qty': 1,
                    'product_uom': self.product_id.uom_po_id.id,
                    'price_unit': self.avg_price or self.product_id.standard_price,
                })]
            }
        }

    @api.model
    def update_all_suggestions(self):
        """Cron job to update all vendor suggestions"""
        # Get products that need suggestion updates
        products_to_update = self.env['product.product'].search([
            ('purchase_ok', '=', True),
        ])
        
        for product in products_to_update:
            try:
                self.generate_suggestions_for_product(product.id)
            except Exception as e:
                _logger.error(f"Failed to update suggestions for product {product.name}: {e}") 