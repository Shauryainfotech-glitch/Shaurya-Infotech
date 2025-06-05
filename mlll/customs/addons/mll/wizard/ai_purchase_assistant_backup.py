from odoo import models, fields, api
import json

class AiPurchaseAssistant(models.TransientModel):
    _name = 'ai.purchase.assistant'
    _description = 'AI Purchase Assistant'
    
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        required=True
    )
    
    analysis_type = fields.Selection([
        ('vendor_search', 'Find Alternative Vendors'),
        ('price_analysis', 'Price Analysis'),
        ('negotiation_strategy', 'Negotiation Strategy'),
        ('risk_assessment', 'Risk Assessment'),
        ('market_analysis', 'Market Analysis'),
    ], string='Analysis Type', required=True, default='vendor_search')
    
    product_categories = fields.Many2many(
        'product.category',
        string='Product Categories',
        help='Filter vendors by product categories'
    )
    
    budget_range_min = fields.Float(string='Minimum Budget')
    budget_range_max = fields.Float(string='Maximum Budget')
    
    delivery_urgency = fields.Selection([
        ('low', 'Low - Standard delivery'),
        ('medium', 'Medium - Expedited delivery'),
        ('high', 'High - Urgent delivery'),
    ], string='Delivery Urgency', default='medium')
    
    quality_requirements = fields.Selection([
        ('standard', 'Standard Quality'),
        ('premium', 'Premium Quality'),
        ('certified', 'Certified/Compliant'),
    ], string='Quality Requirements', default='standard')
    
    ai_response = fields.Text(
        string='AI Analysis',
        readonly=True
    )
    
    vendor_recommendations = fields.One2many(
        'ai.vendor.recommendation',
        'assistant_id',
        string='Vendor Recommendations'
    )
    
    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        if self.purchase_order_id:
            # Auto-populate categories from order lines
            categories = self.purchase_order_id.order_line.mapped('product_id.categ_id')
            self.product_categories = [(6, 0, categories.ids)]
            
            # Set budget range based on order total
            total = self.purchase_order_id.amount_total
            self.budget_range_min = total * 0.8  # 20% below current
            self.budget_range_max = total * 1.2  # 20% above current
    
    def action_analyze(self):
        """Perform AI analysis based on selected type"""
        self.ensure_one()
        
        if self.analysis_type == 'vendor_search':
            self._analyze_vendors()
        elif self.analysis_type == 'price_analysis':
            self._analyze_prices()
        elif self.analysis_type == 'negotiation_strategy':
            self._generate_negotiation_strategy()
        elif self.analysis_type == 'risk_assessment':
            self._assess_risks()
        elif self.analysis_type == 'market_analysis':
            self._analyze_market()
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ai.purchase.assistant',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'form_view_initial_mode': 'readonly'}
        }
    
    def _analyze_vendors(self):
        """Find and analyze alternative vendors"""
        # Get product categories from the purchase order
        categories = self.purchase_order_id.order_line.mapped('product_id.categ_id')
        
        # Search for vendors who supply similar products
        domain = [
            ('supplier_rank', '>', 0),  # Is a vendor
            ('is_company', '=', True),  # Company only
        ]
        
        if categories:
            # Find vendors through their supplied products
            products = self.env['product.template'].search([
                ('categ_id', 'in', categories.ids),
                ('seller_ids', '!=', False)
            ])
            vendor_ids = products.mapped('seller_ids.partner_id.id')
            domain.append(('id', 'in', vendor_ids))
        
        vendors = self.env['res.partner'].search(domain, limit=10)
        
        # Analyze each vendor
        recommendations = []
        for vendor in vendors:
            # Skip current vendor
            if vendor == self.purchase_order_id.partner_id:
                continue
                
            # Calculate vendor score
            score = self._calculate_vendor_score(vendor)
            
            # Get vendor's product offerings in relevant categories
            vendor_products = self.env['product.template'].search([
                ('categ_id', 'in', categories.ids),
                ('seller_ids.partner_id', '=', vendor.id)
            ])
            
            recommendation = {
                'vendor_id': vendor.id,
                'score': score,
                'products_count': len(vendor_products),
                'categories': vendor_products.mapped('categ_id.name'),
                'analysis': self._generate_vendor_analysis(vendor)
            }
            recommendations.append(recommendation)
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Create recommendation records
        self.vendor_recommendations.unlink()
        for rec in recommendations[:5]:  # Top 5 vendors
            self.env['ai.vendor.recommendation'].create({
                'assistant_id': self.id,
                'vendor_id': rec['vendor_id'],
                'score': rec['score'],
                'analysis': rec['analysis'],
                'products_count': rec['products_count'],
            })
        
        # Generate AI response
        self.ai_response = self._format_vendor_analysis(recommendations[:5])
    
    def _calculate_vendor_score(self, vendor):
        """Calculate vendor score based on various factors"""
        score = 50  # Base score
        
        # Historical performance
        purchase_orders = self.env['purchase.order'].search([
            ('partner_id', '=', vendor.id),
            ('state', '=', 'purchase')
        ])
        
        if purchase_orders:
            # On-time delivery rate
            on_time_orders = purchase_orders.filtered(lambda o: hasattr(o, 'on_time_delivery') and o.on_time_delivery)
            if purchase_orders:
                on_time_rate = len(on_time_orders) / len(purchase_orders)
                score += on_time_rate * 20
            
            # Order frequency (more orders = more reliable)
            order_frequency = len(purchase_orders)
            score += min(order_frequency, 10)  # Max 10 points
        
        # Geographic proximity (if same country)
        if vendor.country_id == self.purchase_order_id.company_id.country_id:
            score += 10
        
        # Vendor rating (if available)
        if hasattr(vendor, 'vendor_rating') and vendor.vendor_rating:
            score += vendor.vendor_rating * 2
        
        return min(score, 100)  # Cap at 100
    
    def _generate_vendor_analysis(self, vendor):
        """Generate detailed analysis for a vendor"""
        analysis = []
        
        # Basic info
        analysis.append(f"Company: {vendor.name}")
        if vendor.country_id:
            analysis.append(f"Location: {vendor.country_id.name}")
        
        # Historical data
        purchase_orders = self.env['purchase.order'].search([
            ('partner_id', '=', vendor.id),
            ('state', '=', 'purchase')
        ], limit=10)
        
        if purchase_orders:
            total_orders = len(purchase_orders)
            total_value = sum(purchase_orders.mapped('amount_total'))
            analysis.append(f"Historical Orders: {total_orders}")
            analysis.append(f"Total Business Value: {total_value:,.2f}")
            
            # Average order value
            avg_order = total_value / total_orders
            analysis.append(f"Average Order Value: {avg_order:,.2f}")
        else:
            analysis.append("No historical purchase data available")
        
        return "\n".join(analysis)
    
    def _format_vendor_analysis(self, recommendations):
        """Format the vendor analysis for display"""
        if not recommendations:
            return "No alternative vendors found for the specified criteria."
        
        response = "AI Vendor Analysis Results:\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            vendor = self.env['res.partner'].browse(rec['vendor_id'])
            response += f"{i}. {vendor.name} (Score: {rec['score']:.1f}/100)\n"
            response += f"   Products Available: {rec['products_count']}\n"
            response += f"   Categories: {', '.join(rec['categories'])}\n"
            response += f"   Analysis: {rec['analysis'][:100]}...\n\n"
        
        response += "\nRecommendation: Consider reaching out to the top-scored vendors for quotes."
        return response
    
    def _analyze_prices(self):
        """Analyze pricing trends and opportunities"""
        order = self.purchase_order_id
        analysis = []
        
        analysis.append("Price Analysis Report:\n")
        
        for line in order.order_line:
            product = line.product_id
            
            # Find historical prices for this product
            historical_lines = self.env['purchase.order.line'].search([
                ('product_id', '=', product.id),
                ('order_id.state', '=', 'purchase'),
                ('order_id.date_order', '>=', fields.Date.subtract(fields.Date.today(), days=365))
            ])
            
            if historical_lines:
                prices = historical_lines.mapped('price_unit')
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                analysis.append(f"\nProduct: {product.name}")
                analysis.append(f"Current Price: {line.price_unit:.2f}")
                analysis.append(f"Historical Average: {avg_price:.2f}")
                analysis.append(f"Best Price (12 months): {min_price:.2f}")
                analysis.append(f"Highest Price (12 months): {max_price:.2f}")
                
                if line.price_unit > avg_price:
                    savings = line.price_unit - avg_price
                    analysis.append(f"⚠️ Current price is {savings:.2f} above average")
                else:
                    analysis.append("✅ Current price is competitive")
        
        self.ai_response = "\n".join(analysis)
    
    def _generate_negotiation_strategy(self):
        """Generate negotiation strategy based on vendor history"""
        vendor = self.purchase_order_id.partner_id
        if not vendor:
            self.ai_response = "No vendor selected for negotiation analysis."
            return
        
        strategy = []
        strategy.append(f"Negotiation Strategy for {vendor.name}:\n")
        
        # Analyze historical relationship
        orders = self.env['purchase.order'].search([
            ('partner_id', '=', vendor.id),
            ('state', '=', 'purchase')
        ])
        
        if orders:
            total_business = sum(orders.mapped('amount_total'))
            strategy.append(f"💼 Relationship Value: {total_business:,.2f} ({len(orders)} orders)")
            strategy.append("   Leverage: Emphasize long-term partnership value\n")
        
        # Volume analysis
        current_total = self.purchase_order_id.amount_total
        if orders:
            avg_order = total_business / len(orders)
            if current_total > avg_order * 1.5:
                strategy.append("📈 Large Order Opportunity:")
                strategy.append("   - Request volume discounts")
                strategy.append("   - Negotiate better payment terms\n")
        
        # Seasonal patterns
        strategy.append("📅 Timing Considerations:")
        strategy.append("   - End of quarter/year: Better discounts possible")
        strategy.append("   - Consider bulk ordering for better rates\n")
        
        # Competition leverage
        strategy.append("🏆 Competitive Leverage:")
        strategy.append("   - Mention you're evaluating multiple vendors")
        strategy.append("   - Request price matching if you have better quotes\n")
        
        strategy.append("💡 Negotiation Tips:")
        strategy.append("   - Focus on total cost of ownership, not just unit price")
        strategy.append("   - Negotiate delivery terms and payment schedules")
        strategy.append("   - Consider long-term contracts for better rates")
        
        self.ai_response = "\n".join(strategy)
    
    def _assess_risks(self):
        """Assess procurement risks"""
        order = self.purchase_order_id
        risks = []
        
        risks.append("Risk Assessment Report:\n")
        
        # Vendor concentration risk
        vendor = order.partner_id
        if vendor:
            vendor_orders = self.env['purchase.order'].search([
                ('partner_id', '=', vendor.id),
                ('state', '=', 'purchase'),
                ('date_order', '>=', fields.Date.subtract(fields.Date.today(), days=365))
            ])
            
            total_vendor_spend = sum(vendor_orders.mapped('amount_total'))
            total_company_spend = sum(self.env['purchase.order'].search([
                ('state', '=', 'purchase'),
                ('date_order', '>=', fields.Date.subtract(fields.Date.today(), days=365))
            ]).mapped('amount_total'))
            
            if total_company_spend > 0:
                concentration = (total_vendor_spend / total_company_spend) * 100
                if concentration > 30:
                    risks.append(f"⚠️ HIGH RISK: Vendor concentration ({concentration:.1f}% of total spend)")
                    risks.append("   Recommendation: Diversify supplier base\n")
        
        # Single source risk
        for line in order.order_line:
            suppliers = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)
            ])
            
            if len(suppliers) <= 1:
                risks.append(f"⚠️ Single Source Risk: {line.product_id.name}")
                risks.append("   Recommendation: Identify alternative suppliers\n")
        
        # Delivery risk
        if order.date_planned:
            days_to_delivery = (order.date_planned - fields.Date.today()).days
            if days_to_delivery < 7:
                risks.append("⚠️ Delivery Risk: Very tight timeline")
                risks.append("   Recommendation: Confirm vendor capacity\n")
        
        # Quality risk
        risks.append("💡 Quality Assurance:")
        risks.append("   - Request quality certifications")
        risks.append("   - Define clear acceptance criteria")
        risks.append("   - Plan inspection procedures")
        
        self.ai_response = "\n".join(risks)
    
    def _analyze_market(self):
        """Analyze market conditions"""
        categories = self.purchase_order_id.order_line.mapped('product_id.categ_id')
        
        analysis = []
        analysis.append("Market Analysis:\n")
        
        for category in categories:
            analysis.append(f"\nCategory: {category.name}")
            
            # Find recent orders in this category
            recent_orders = self.env['purchase.order.line'].search([
                ('product_id.categ_id', '=', category.id),
                ('order_id.state', '=', 'purchase'),
                ('order_id.date_order', '>=', fields.Date.subtract(fields.Date.today(), days=90))
            ])
            
            if recent_orders:
                prices = recent_orders.mapped('price_unit')
                avg_market_price = sum(prices) / len(prices)
                analysis.append(f"Recent Market Average: {avg_market_price:.2f}")
                analysis.append(f"Number of Recent Orders: {len(recent_orders)}")
                
                # Price trend
                old_orders = self.env['purchase.order.line'].search([
                    ('product_id.categ_id', '=', category.id),
                    ('order_id.state', '=', 'purchase'),
                    ('order_id.date_order', '>=', fields.Date.subtract(fields.Date.today(), days=180)),
                    ('order_id.date_order', '<', fields.Date.subtract(fields.Date.today(), days=90))
                ])
                
                if old_orders:
                    old_avg = sum(old_orders.mapped('price_unit')) / len(old_orders)
                    trend = ((avg_market_price - old_avg) / old_avg) * 100
                    if trend > 5:
                        analysis.append(f"📈 Price Trend: Increasing ({trend:.1f}%)")
                    elif trend < -5:
                        analysis.append(f"📉 Price Trend: Decreasing ({trend:.1f}%)")
                    else:
                        analysis.append("📊 Price Trend: Stable")
        
        analysis.append("\n💡 Market Insights:")
        analysis.append("   - Monitor price trends for strategic timing")
        analysis.append("   - Consider forward contracts for volatile categories")
        analysis.append("   - Leverage market intelligence in negotiations")
        
        self.ai_response = "\n".join(analysis)


