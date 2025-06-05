import json
import logging
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # AI-powered fields
    ai_risk_score = fields.Float('AI Risk Score', compute='_compute_ai_risk_score', store=True)
    ai_risk_breakdown = fields.Json('Risk Breakdown', readonly=True)
    ai_alternative_vendors = fields.Many2many(
        'res.partner', 'purchase_alternative_vendor_rel', 
        'purchase_id', 'partner_id', 
        string='AI Suggested Alternative Vendors'
    )
    ai_recommendations = fields.Text('AI Recommendations', readonly=True)
    ai_price_analysis = fields.Json('AI Price Analysis', readonly=True)
    
    # Approval workflow
    requires_ai_approval = fields.Boolean('Requires AI Approval', compute='_compute_requires_ai_approval', store=True)
    ai_approval_status = fields.Selection([
        ('pending', 'Pending AI Review'),
        ('approved', 'AI Approved'),
        ('rejected', 'AI Rejected'),
        ('manual_review', 'Manual Review Required'),
    ], string='AI Approval Status', default='pending')
    
    # Performance tracking
    vendor_suggestion_used = fields.Many2one('purchase.vendor.suggestion', 'Used Vendor Suggestion')
    ai_prediction_accuracy = fields.Float('AI Prediction Accuracy (%)')
    
    # Enhanced approval fields
    approval_notes = fields.Text('Approval Notes')
    risk_mitigation_actions = fields.Text('Risk Mitigation Actions')

    @api.depends('partner_id', 'order_line', 'amount_total')
    def _compute_ai_risk_score(self):
        """Compute AI risk score for the purchase order"""
        for order in self:
            if not order.partner_id or not order.order_line:
                order.ai_risk_score = 0.0
                continue
            
            try:
                # Prepare AI prompt for risk assessment
                prompt = order._prepare_ai_risk_prompt()
                
                # Call AI service for risk assessment
                response = self.env['purchase.ai.service'].call_ai_service(
                    'risk_assessment', prompt
                )
                
                # Process AI response
                order._process_ai_risk_response(response)
                
            except Exception as e:
                _logger.warning(f"AI risk assessment failed for PO {order.name}: {e}")
                order.ai_risk_score = 0.5  # Default neutral risk

    @api.depends('ai_risk_score')
    def _compute_requires_ai_approval(self):
        """Determine if AI approval is required"""
        settings = self.env['purchase.ai.settings'].get_settings()
        for order in self:
            order.requires_ai_approval = order.ai_risk_score > settings.auto_approve_threshold

    def _prepare_ai_risk_prompt(self):
        """Prepare comprehensive prompt for AI risk assessment"""
        # Get vendor information
        vendor_info = {
            'name': self.partner_id.name,
            'supplier_rank': self.partner_id.supplier_rank,
            'country': self.partner_id.country_id.name if self.partner_id.country_id else '',
            'payment_terms': self.partner_id.property_supplier_payment_term_id.name if self.partner_id.property_supplier_payment_term_id else '',
        }
        
        # Get order details
        order_info = {
            'total_amount': self.amount_total,
            'currency': self.currency_id.name,
            'order_date': self.date_order.isoformat() if self.date_order else '',
            'expected_delivery': self.date_planned.isoformat() if self.date_planned else '',
            'line_count': len(self.order_line),
        }
        
        # Get product details
        products_info = []
        for line in self.order_line:
            product_info = {
                'name': line.product_id.name,
                'category': line.product_id.categ_id.name if line.product_id.categ_id else '',
                'quantity': line.product_qty,
                'unit_price': line.price_unit,
                'total': line.price_subtotal,
            }
            products_info.append(product_info)
        
        # Get historical performance
        historical_data = self._get_vendor_historical_performance()
        
        # Get market context
        market_context = self._get_market_context()
        
        prompt = f"""
        Conduct a comprehensive risk assessment for the following purchase order:
        
        VENDOR INFORMATION:
        {json.dumps(vendor_info, indent=2)}
        
        ORDER DETAILS:
        {json.dumps(order_info, indent=2)}
        
        PRODUCTS:
        {json.dumps(products_info, indent=2)}
        
        HISTORICAL PERFORMANCE:
        {json.dumps(historical_data, indent=2)}
        
        MARKET CONTEXT:
        {json.dumps(market_context, indent=2)}
        
        Please assess the following risk factors and provide scores (0.0 to 1.0, where 1.0 is highest risk):
        
        1. Financial Risk: Vendor's financial stability and payment reliability
        2. Delivery Risk: Likelihood of delivery delays or failures
        3. Quality Risk: Risk of receiving substandard products
        4. Compliance Risk: Regulatory and compliance issues
        5. Price Risk: Risk of price volatility or overpricing
        6. Relationship Risk: Risk to ongoing vendor relationship
        
        Also provide:
        - Overall risk assessment and recommendation
        - Alternative vendor suggestions if risk is high
        - Price analysis and market comparison
        - Specific mitigation strategies
        - Approval recommendation (approve/reject/conditional)
        
        Return response in JSON format:
        {{
            "risk_breakdown": {{
                "financial_risk": 0.0-1.0,
                "delivery_risk": 0.0-1.0,
                "quality_risk": 0.0-1.0,
                "compliance_risk": 0.0-1.0,
                "price_risk": 0.0-1.0,
                "relationship_risk": 0.0-1.0
            }},
            "overall_risk_score": 0.0-1.0,
            "recommendation": "approve|reject|conditional",
            "risk_factors": ["list of key risk factors"],
            "mitigation_strategies": ["list of mitigation actions"],
            "alternative_vendors": ["list of alternative vendor names"],
            "price_analysis": {{
                "market_comparison": "text",
                "price_competitiveness": "text",
                "cost_savings_opportunities": ["list"]
            }},
            "approval_notes": "detailed explanation"
        }}
        """
        
        return prompt

    def _get_vendor_historical_performance(self):
        """Get historical performance data for the vendor"""
        # Get recent orders from this vendor
        recent_orders = self.env['purchase.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', 'in', ['purchase', 'done']),
            ('id', '!=', self.id),
        ], limit=20, order='date_order desc')
        
        if not recent_orders:
            return {'message': 'No historical data available'}
        
        # Calculate performance metrics
        total_orders = len(recent_orders)
        on_time_deliveries = 0
        total_amount = 0
        delivery_times = []
        
        for order in recent_orders:
            total_amount += order.amount_total
            
            if order.effective_date and order.date_planned:
                delivery_time = (order.effective_date - order.date_planned).days
                delivery_times.append(delivery_time)
                
                if delivery_time <= 0:  # On time or early
                    on_time_deliveries += 1
        
        performance_data = {
            'total_orders': total_orders,
            'total_value': total_amount,
            'avg_order_value': total_amount / total_orders if total_orders > 0 else 0,
            'on_time_delivery_rate': (on_time_deliveries / len(delivery_times)) * 100 if delivery_times else 0,
            'avg_delivery_delay': sum(delivery_times) / len(delivery_times) if delivery_times else 0,
            'relationship_duration_months': self._calculate_relationship_duration(),
        }
        
        return performance_data

    def _calculate_relationship_duration(self):
        """Calculate relationship duration with vendor in months"""
        first_order = self.env['purchase.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', 'in', ['purchase', 'done']),
        ], order='date_order asc', limit=1)
        
        if first_order and first_order.date_order:
            delta = fields.Datetime.now() - first_order.date_order
            return delta.days / 30.44  # Average days per month
        
        return 0

    def _get_market_context(self):
        """Get market context for the products in this order"""
        market_data = {}
        
        for line in self.order_line:
            # Get recent market prices for this product
            recent_lines = self.env['purchase.order.line'].search([
                ('product_id', '=', line.product_id.id),
                ('order_id.state', 'in', ['purchase', 'done']),
                ('create_date', '>=', fields.Datetime.now() - timedelta(days=90)),
            ], limit=50)
            
            if recent_lines:
                prices = recent_lines.mapped('price_unit')
                market_data[line.product_id.name] = {
                    'current_price': line.price_unit,
                    'market_avg_price': sum(prices) / len(prices),
                    'market_min_price': min(prices),
                    'market_max_price': max(prices),
                    'price_samples': len(prices),
                }
        
        return market_data

    def _process_ai_risk_response(self, ai_response):
        """Process AI risk assessment response"""
        try:
            content = ai_response.get('content', '{}')
            
            # Parse JSON response
            try:
                assessment = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    assessment = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in AI response")
            
            # Store risk breakdown
            self.ai_risk_breakdown = assessment.get('risk_breakdown', {})
            
            # Calculate overall risk score
            risk_breakdown = assessment.get('risk_breakdown', {})
            if risk_breakdown:
                risk_scores = list(risk_breakdown.values())
                self.ai_risk_score = sum(risk_scores) / len(risk_scores)
            else:
                self.ai_risk_score = assessment.get('overall_risk_score', 0.5)
            
            # Store AI recommendations
            self.ai_recommendations = assessment.get('approval_notes', '')
            
            # Store price analysis
            self.ai_price_analysis = assessment.get('price_analysis', {})
            
            # Find alternative vendors
            alternative_vendor_names = assessment.get('alternative_vendors', [])
            alternative_vendors = []
            
            for vendor_name in alternative_vendor_names:
                vendor = self.env['res.partner'].search([
                    ('name', 'ilike', vendor_name),
                    ('supplier_rank', '>', 0),
                    ('id', '!=', self.partner_id.id)
                ], limit=1)
                if vendor:
                    alternative_vendors.append(vendor.id)
            
            if alternative_vendors:
                self.ai_alternative_vendors = [(6, 0, alternative_vendors)]
            
            # Set approval status based on recommendation
            recommendation = assessment.get('recommendation', 'conditional')
            if recommendation == 'approve':
                self.ai_approval_status = 'approved'
            elif recommendation == 'reject':
                self.ai_approval_status = 'rejected'
            else:
                self.ai_approval_status = 'manual_review'
            
            # Store mitigation strategies
            mitigation_strategies = assessment.get('mitigation_strategies', [])
            if mitigation_strategies:
                self.risk_mitigation_actions = '\n'.join([
                    f"• {strategy}" for strategy in mitigation_strategies
                ])
            
        except Exception as e:
            _logger.error(f"Failed to process AI risk assessment: {e}")
            # Set default values
            self.ai_risk_score = 0.5
            self.ai_approval_status = 'manual_review'
            self.ai_recommendations = f"AI assessment processing failed: {str(e)}"

    def button_confirm(self):
        """Override confirm to include AI approval check"""
        for order in self:
            # Check AI approval requirements
            if order.requires_ai_approval and order.ai_approval_status not in ['approved', 'manual_review']:
                if order.ai_approval_status == 'rejected':
                    raise UserError(_(
                        "This purchase order has been rejected by AI risk assessment. "
                        "Risk score: %.2f\n\nReasons: %s"
                    ) % (order.ai_risk_score, order.ai_recommendations))
                else:
                    raise UserError(_(
                        "This purchase order requires AI approval before confirmation. "
                        "Current status: %s"
                    ) % order.ai_approval_status)
            
            # Check if manual approval is required for high-risk orders
            settings = self.env['purchase.ai.settings'].get_settings()
            if order.ai_risk_score > settings.risk_threshold:
                if not self.env.user.has_group('purchase.group_purchase_manager'):
                    raise UserError(_(
                        "This high-risk purchase order (risk score: %.2f) requires approval "
                        "from a Purchase Manager."
                    ) % order.ai_risk_score)
        
        # Call original confirm method
        result = super().button_confirm()
        
        # Create feedback records for learning
        for order in self:
            order._create_ai_feedback_records()
        
        return result

    def _create_ai_feedback_records(self):
        """Create feedback records for AI learning"""
        for line in self.order_line:
            # Find related vendor suggestion
            suggestion = self.env['purchase.vendor.suggestion'].search([
                ('vendor_id', '=', self.partner_id.id),
                ('product_id', '=', line.product_id.id),
            ], limit=1)
            
            if suggestion:
                # Mark that this suggestion was used
                suggestion.vendor_suggestion_used = self.id
                
                # Create initial feedback record (will be updated when order is completed)
                self.env['vendor.suggestion.feedback'].create({
                    'suggestion_id': suggestion.id,
                    'purchase_order_id': self.id,
                    'rating': 'neutral',  # Will be updated based on actual performance
                    'comment': f'Suggestion used in PO {self.name}',
                })

    def action_ai_reanalyze(self):
        """Rerun AI risk analysis"""
        self.ensure_one()
        
        # Clear existing AI data
        self.ai_risk_score = 0.0
        self.ai_risk_breakdown = {}
        self.ai_recommendations = ''
        self.ai_price_analysis = {}
        self.ai_alternative_vendors = [(5, 0, 0)]
        self.ai_approval_status = 'pending'
        
        # Trigger recomputation
        self._compute_ai_risk_score()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Analysis Complete'),
                'message': _('AI risk analysis has been updated. Risk score: %.2f') % self.ai_risk_score,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_view_vendor_suggestions(self):
        """View vendor suggestions for products in this order"""
        product_ids = self.order_line.mapped('product_id').ids
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Suggestions'),
            'res_model': 'purchase.vendor.suggestion',
            'view_mode': 'tree,form',
            'domain': [('product_id', 'in', product_ids)],
            'context': {'default_product_ids': product_ids}
        }

    def action_view_alternative_vendors(self):
        """View alternative vendors suggested by AI"""
        if not self.ai_alternative_vendors:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Alternatives'),
                    'message': _('No alternative vendors suggested by AI'),
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Alternative Vendors'),
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.ai_alternative_vendors.ids)],
        }

    def action_override_ai_approval(self):
        """Override AI approval (requires manager permissions)"""
        self.ensure_one()
        
        if not self.env.user.has_group('purchase.group_purchase_manager'):
            raise UserError(_("Only Purchase Managers can override AI approval"))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Override AI Approval'),
            'res_model': 'purchase.ai.override.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id}
        } 