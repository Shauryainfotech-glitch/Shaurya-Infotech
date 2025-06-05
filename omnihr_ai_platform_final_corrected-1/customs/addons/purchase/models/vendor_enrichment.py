# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
import requests
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class VendorEnrichment(models.Model):
    _name = 'vendor.enrichment'
    _description = 'Vendor Data Enrichment'
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(string='Enrichment Name', required=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('is_company', '=', True)])
    
    # Enrichment Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='State', default='draft', required=True)
    
    # Progress Tracking
    progress = fields.Float(string='Progress (%)', default=0.0)
    progress_message = fields.Char(string='Progress Message')
    
    # Enrichment Sources
    web_scraping_enabled = fields.Boolean(string='Web Scraping', default=True)
    api_enrichment_enabled = fields.Boolean(string='API Enrichment', default=True)
    ai_analysis_enabled = fields.Boolean(string='AI Analysis', default=True)
    financial_data_enabled = fields.Boolean(string='Financial Data', default=True)
    compliance_check_enabled = fields.Boolean(string='Compliance Check', default=True)
    
    # Enriched Data
    company_info = fields.Text(string='Company Information (JSON)')
    financial_data = fields.Text(string='Financial Data (JSON)')
    compliance_data = fields.Text(string='Compliance Data (JSON)')
    market_data = fields.Text(string='Market Data (JSON)')
    contact_data = fields.Text(string='Contact Data (JSON)')
    social_media_data = fields.Text(string='Social Media Data (JSON)')
    
    # AI Analysis Results
    ai_summary = fields.Text(string='AI Summary')
    risk_indicators = fields.Text(string='Risk Indicators (JSON)')
    recommendations = fields.Text(string='AI Recommendations')
    confidence_score = fields.Float(string='Confidence Score', default=0.0)
    
    # Timing
    started_date = fields.Datetime(string='Started Date')
    completed_date = fields.Datetime(string='Completed Date')
    processing_time = fields.Float(string='Processing Time (seconds)', compute='_compute_processing_time', store=True)
    
    # User Context
    user_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('started_date', 'completed_date')
    def _compute_processing_time(self):
        for record in self:
            if record.started_date and record.completed_date:
                delta = record.completed_date - record.started_date
                record.processing_time = delta.total_seconds()
            else:
                record.processing_time = 0.0

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            vendor = self.env['res.partner'].browse(vals.get('vendor_id'))
            vals['name'] = f"Enrichment: {vendor.name}"
        return super().create(vals)

    def action_start_enrichment(self):
        """Start the vendor enrichment process"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft enrichments can be started'))
        
        self.write({
            'state': 'in_progress',
            'started_date': fields.Datetime.now(),
            'progress': 0.0,
            'progress_message': 'Starting enrichment process...'
        })
        
        # Queue the enrichment process
        self.env['ai.processing.queue'].create({
            'name': f'Vendor Enrichment: {self.vendor_id.name}',
            'request_type': 'vendor_enrichment',
            'priority': 'medium',
            'input_data': json.dumps({'vendor_id': self.vendor_id.id}),
            'model_name': 'vendor.enrichment',
            'record_id': self.id,
            'method_name': 'process_enrichment',
        })

    def process_enrichment(self):
        """Process the vendor enrichment"""
        self.ensure_one()
        
        try:
            # Step 1: Basic company information
            self.update_progress(10, 'Gathering basic company information...')
            self._enrich_company_info()
            
            # Step 2: Financial data
            if self.financial_data_enabled:
                self.update_progress(25, 'Collecting financial data...')
                self._enrich_financial_data()
            
            # Step 3: Compliance data
            if self.compliance_check_enabled:
                self.update_progress(40, 'Checking compliance status...')
                self._enrich_compliance_data()
            
            # Step 4: Market data
            self.update_progress(55, 'Analyzing market position...')
            self._enrich_market_data()
            
            # Step 5: Contact enrichment
            self.update_progress(70, 'Enriching contact information...')
            self._enrich_contact_data()
            
            # Step 6: Social media presence
            self.update_progress(80, 'Analyzing social media presence...')
            self._enrich_social_media_data()
            
            # Step 7: AI analysis
            if self.ai_analysis_enabled:
                self.update_progress(90, 'Running AI analysis...')
                self._run_ai_analysis()
            
            # Step 8: Apply enriched data to vendor
            self.update_progress(95, 'Applying enriched data...')
            self._apply_enriched_data()
            
            # Complete
            self.write({
                'state': 'completed',
                'completed_date': fields.Datetime.now(),
                'progress': 100.0,
                'progress_message': 'Enrichment completed successfully'
            })
            
        except Exception as e:
            _logger.error(f"Error in vendor enrichment: {str(e)}")
            self.write({
                'state': 'failed',
                'completed_date': fields.Datetime.now(),
                'progress_message': f'Enrichment failed: {str(e)}'
            })
            raise

    def _enrich_company_info(self):
        """Enrich basic company information"""
        vendor = self.vendor_id
        company_info = {
            'name': vendor.name,
            'website': vendor.website,
            'email': vendor.email,
            'phone': vendor.phone,
            'industry': vendor.industry_id.name if vendor.industry_id else None,
            'country': vendor.country_id.name if vendor.country_id else None,
        }
        
        # Web scraping for additional info
        if self.web_scraping_enabled and vendor.website:
            try:
                scraped_data = self._scrape_website_info(vendor.website)
                company_info.update(scraped_data)
            except Exception as e:
                _logger.warning(f"Web scraping failed for {vendor.website}: {str(e)}")
        
        self.company_info = json.dumps(company_info, default=str)

    def _enrich_financial_data(self):
        """Enrich financial data"""
        vendor = self.vendor_id
        financial_data = {
            'credit_limit': vendor.credit_limit,
            'payment_term': vendor.property_supplier_payment_term_id.name if vendor.property_supplier_payment_term_id else None,
        }
        
        # Try to get financial data from external APIs
        if self.api_enrichment_enabled:
            try:
                external_financial = self._get_external_financial_data(vendor)
                financial_data.update(external_financial)
            except Exception as e:
                _logger.warning(f"External financial data fetch failed: {str(e)}")
        
        self.financial_data = json.dumps(financial_data, default=str)

    def _enrich_compliance_data(self):
        """Enrich compliance and certification data"""
        vendor = self.vendor_id
        compliance_data = {
            'vat': vendor.vat,
            'company_registry': vendor.company_registry,
            'certifications': [],
            'licenses': [],
        }
        
        # Check for compliance documents
        documents = self.env['ir.attachment'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', vendor.id),
            ('name', 'ilike', 'certificate')
        ])
        
        for doc in documents:
            compliance_data['certifications'].append({
                'name': doc.name,
                'create_date': doc.create_date.isoformat() if doc.create_date else None,
            })
        
        self.compliance_data = json.dumps(compliance_data, default=str)

    def _enrich_market_data(self):
        """Enrich market and competitive data"""
        vendor = self.vendor_id
        market_data = {
            'industry_sector': vendor.industry_id.name if vendor.industry_id else None,
            'market_presence': 'unknown',
            'competitors': [],
            'market_share': 'unknown',
        }
        
        # Analyze purchase history for market insights
        purchase_orders = self.env['purchase.order'].search([
            ('partner_id', '=', vendor.id),
            ('state', '=', 'done')
        ], limit=50)
        
        if purchase_orders:
            total_amount = sum(purchase_orders.mapped('amount_total'))
            avg_order_value = total_amount / len(purchase_orders)
            market_data.update({
                'total_purchase_volume': total_amount,
                'average_order_value': avg_order_value,
                'order_frequency': len(purchase_orders),
                'last_order_date': max(purchase_orders.mapped('date_order')).isoformat(),
            })
        
        self.market_data = json.dumps(market_data, default=str)

    def _enrich_contact_data(self):
        """Enrich contact information"""
        vendor = self.vendor_id
        contact_data = {
            'primary_contact': {
                'name': vendor.name,
                'email': vendor.email,
                'phone': vendor.phone,
            },
            'additional_contacts': []
        }
        
        # Get child contacts
        child_contacts = self.env['res.partner'].search([
            ('parent_id', '=', vendor.id),
            ('is_company', '=', False)
        ])
        
        for contact in child_contacts:
            contact_data['additional_contacts'].append({
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'function': contact.function,
            })
        
        self.contact_data = json.dumps(contact_data, default=str)

    def _enrich_social_media_data(self):
        """Enrich social media presence data"""
        vendor = self.vendor_id
        social_data = {
            'website': vendor.website,
            'social_profiles': [],
            'online_presence_score': 0,
        }
        
        # Basic social media presence check
        if vendor.website:
            social_data['online_presence_score'] += 30
        if vendor.email:
            social_data['online_presence_score'] += 20
        if vendor.phone:
            social_data['online_presence_score'] += 10
        
        self.social_media_data = json.dumps(social_data, default=str)

    def _run_ai_analysis(self):
        """Run AI analysis on enriched data"""
        # Prepare data for AI analysis
        all_data = {
            'company_info': json.loads(self.company_info or '{}'),
            'financial_data': json.loads(self.financial_data or '{}'),
            'compliance_data': json.loads(self.compliance_data or '{}'),
            'market_data': json.loads(self.market_data or '{}'),
            'contact_data': json.loads(self.contact_data or '{}'),
            'social_media_data': json.loads(self.social_media_data or '{}'),
        }
        
        # Get AI service
        ai_service = self.env['purchase.ai.service'].get_service_for_usage('vendor_enrichment')
        if not ai_service:
            _logger.warning("No AI service available for vendor enrichment")
            return
        
        prompt = f"""
        Analyze the following vendor data and provide insights:
        
        Vendor: {self.vendor_id.name}
        Data: {json.dumps(all_data, indent=2)}
        
        Please provide:
        1. A comprehensive summary of the vendor
        2. Risk indicators and concerns
        3. Recommendations for engagement
        4. Confidence score (0-1) for the analysis
        
        Format your response as JSON with keys: summary, risk_indicators, recommendations, confidence_score
        """
        
        try:
            response = ai_service.call_ai_service(
                prompt=prompt,
                context={'vendor_id': self.vendor_id.id}
            )
            
            if response.get('success'):
                ai_result = response.get('response', {})
                self.ai_summary = ai_result.get('summary', '')
                self.risk_indicators = json.dumps(ai_result.get('risk_indicators', []))
                self.recommendations = ai_result.get('recommendations', '')
                self.confidence_score = ai_result.get('confidence_score', 0.0)
            
        except Exception as e:
            _logger.error(f"AI analysis failed: {str(e)}")

    def _apply_enriched_data(self):
        """Apply enriched data to the vendor record"""
        vendor = self.vendor_id
        
        # Update vendor with enriched data
        company_info = json.loads(self.company_info or '{}')
        financial_data = json.loads(self.financial_data or '{}')
        
        update_vals = {}
        
        # Update basic info if missing
        if not vendor.website and company_info.get('website'):
            update_vals['website'] = company_info['website']
        
        if not vendor.email and company_info.get('email'):
            update_vals['email'] = company_info['email']
        
        if not vendor.phone and company_info.get('phone'):
            update_vals['phone'] = company_info['phone']
        
        # Update financial info
        if financial_data.get('credit_limit') and not vendor.credit_limit:
            update_vals['credit_limit'] = financial_data['credit_limit']
        
        if update_vals:
            vendor.write(update_vals)
        
        # Add enrichment note
        vendor.message_post(
            body=f"Vendor data enriched on {fields.Datetime.now()}. "
                 f"Confidence score: {self.confidence_score:.2f}",
            subject="Vendor Data Enrichment Completed"
        )

    def update_progress(self, progress, message=None):
        """Update enrichment progress"""
        self.ensure_one()
        values = {'progress': min(100.0, max(0.0, progress))}
        if message:
            values['progress_message'] = message
        self.write(values)

    def _scrape_website_info(self, website_url):
        """Scrape basic information from website"""
        # Placeholder for web scraping logic
        # In a real implementation, you would use libraries like BeautifulSoup
        return {
            'scraped_description': 'Website content analysis would go here',
            'scraped_date': fields.Datetime.now().isoformat(),
        }

    def _get_external_financial_data(self, vendor):
        """Get financial data from external APIs"""
        # Placeholder for external API integration
        # In a real implementation, you would integrate with services like:
        # - Dun & Bradstreet
        # - Experian
        # - ClearBit
        return {
            'external_rating': 'A',
            'credit_score': 750,
            'annual_revenue': 'Not available',
        }

    @api.model
    def enrich_vendor_data(self, vendor_id):
        """Public method to enrich vendor data"""
        vendor = self.env['res.partner'].browse(vendor_id)
        if not vendor.exists():
            raise UserError(_('Vendor not found'))
        
        # Check if enrichment already exists
        existing = self.search([
            ('vendor_id', '=', vendor_id),
            ('state', 'in', ['in_progress', 'completed'])
        ], limit=1)
        
        if existing:
            return existing
        
        # Create new enrichment
        enrichment = self.create({
            'vendor_id': vendor_id,
        })
        
        enrichment.action_start_enrichment()
        return enrichment 