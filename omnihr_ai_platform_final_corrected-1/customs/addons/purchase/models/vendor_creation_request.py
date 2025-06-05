import json
import logging
import requests
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)

class VendorCreationRequest(models.Model):
    _name = 'vendor.creation.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'AI-Powered Vendor Creation Request Pipeline'
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char('Reference', required=True, copy=False, readonly=True, 
                      default=lambda self: self.env['ir.sequence'].next_by_code('vendor.creation.request'))
    requested_by = fields.Many2one('res.users', string='Requested By', 
                                  default=lambda self: self.env.user, readonly=True)
    vendor_name = fields.Char('Vendor Name', required=True, tracking=True)
    vendor_email = fields.Char('Vendor Email')
    vendor_phone = fields.Char('Vendor Phone')
    vendor_website = fields.Char('Vendor Website')
    vendor_address = fields.Text('Vendor Address')
    
    # Raw input data
    raw_vendor_input = fields.Text('Raw Vendor Data', help="Initial vendor information provided")
    additional_notes = fields.Text('Additional Notes')
    
    # Enriched data from AI and external sources
    enriched_data = fields.Json('Enriched Vendor Data', readonly=True)
    financial_data = fields.Json('Financial Data', readonly=True)
    compliance_data = fields.Json('Compliance Data', readonly=True)
    market_data = fields.Json('Market Intelligence', readonly=True)
    
    # AI Analysis Results
    ai_risk_score = fields.Float('AI Risk Score', compute='_compute_ai_risk_score', store=True)
    risk_components = fields.Json('Risk Components Breakdown', readonly=True)
    compliance_check = fields.Json('Compliance Check Results', readonly=True)
    ai_recommendations = fields.Text('AI Recommendations', readonly=True)
    
    # Workflow state
    state = fields.Selection([
        ('draft', 'Draft'),
        ('data_enrichment', 'Data Enrichment'),
        ('ai_review', 'AI Review'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status')
    
    # Approval workflow
    approval_required = fields.Boolean('Approval Required', compute='_compute_approval_required', store=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approval_date = fields.Datetime('Approval Date', readonly=True)
    rejection_reason = fields.Text('Rejection Reason')
    
    # Created vendor
    approved_vendor_id = fields.Many2one('res.partner', string='Created Vendor', readonly=True)
    
    # Processing tracking
    enrichment_progress = fields.Float('Enrichment Progress (%)', default=0.0)
    enrichment_status = fields.Text('Enrichment Status')
    last_ai_analysis = fields.Datetime('Last AI Analysis')
    
    # Document attachments
    document_ids = fields.One2many('ir.attachment', 'res_id', 
                                  domain=[('res_model', '=', 'vendor.creation.request')],
                                  string='Documents')
    
    # Priority and categorization
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium', tracking=True)
    
    vendor_category = fields.Selection([
        ('supplier', 'Supplier'),
        ('service_provider', 'Service Provider'),
        ('contractor', 'Contractor'),
        ('consultant', 'Consultant'),
        ('other', 'Other'),
    ], string='Vendor Category')
    
    expected_annual_spend = fields.Monetary('Expected Annual Spend', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)

    @api.depends('ai_risk_score')
    def _compute_approval_required(self):
        """Determine if approval is required based on risk score and settings"""
        settings = self.env['purchase.ai.settings'].get_settings()
        for record in self:
            record.approval_required = record.ai_risk_score > settings.auto_approve_threshold

    @api.depends('risk_components')
    def _compute_ai_risk_score(self):
        """Compute overall risk score from components"""
        for record in self:
            if record.risk_components:
                components = record.risk_components
                # Weighted average of risk components
                weights = {
                    'financial_risk': 0.25,
                    'compliance_risk': 0.25,
                    'operational_risk': 0.20,
                    'reputation_risk': 0.15,
                    'security_risk': 0.15,
                }
                
                total_score = 0.0
                total_weight = 0.0
                
                for component, weight in weights.items():
                    if component in components:
                        total_score += components[component] * weight
                        total_weight += weight
                
                record.ai_risk_score = total_score / total_weight if total_weight > 0 else 0.0
            else:
                record.ai_risk_score = 0.0

    def action_start_data_enrichment(self):
        """Start the data enrichment process"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Can only start enrichment from draft state"))
        
        self.state = 'data_enrichment'
        self.enrichment_progress = 0.0
        self.enrichment_status = "Starting data enrichment..."
        
        # Queue async enrichment job
        self.with_delay()._async_enrich_vendor_data()
        
        self.message_post(
            body=_("Data enrichment process started"),
            message_type='notification'
        )

    @job
    def _async_enrich_vendor_data(self):
        """Async job to enrich vendor data from multiple sources"""
        try:
            self.enrichment_status = "Enriching basic company information..."
            self.enrichment_progress = 10.0
            
            # Step 1: Basic company information enrichment
            basic_data = self._enrich_basic_company_info()
            
            self.enrichment_status = "Gathering financial information..."
            self.enrichment_progress = 30.0
            
            # Step 2: Financial data enrichment
            financial_data = self._enrich_financial_data()
            
            self.enrichment_status = "Checking compliance and certifications..."
            self.enrichment_progress = 50.0
            
            # Step 3: Compliance and certification data
            compliance_data = self._enrich_compliance_data()
            
            self.enrichment_status = "Analyzing market intelligence..."
            self.enrichment_progress = 70.0
            
            # Step 4: Market intelligence
            market_data = self._enrich_market_data()
            
            self.enrichment_status = "Consolidating enriched data..."
            self.enrichment_progress = 90.0
            
            # Consolidate all enriched data
            self.enriched_data = {
                'basic_info': basic_data,
                'financial_info': financial_data,
                'compliance_info': compliance_data,
                'market_info': market_data,
                'enrichment_timestamp': fields.Datetime.now().isoformat(),
            }
            
            self.financial_data = financial_data
            self.compliance_data = compliance_data
            self.market_data = market_data
            
            self.enrichment_progress = 100.0
            self.enrichment_status = "Data enrichment completed successfully"
            
            # Automatically proceed to AI review
            self.action_submit_to_ai_review()
            
        except Exception as e:
            _logger.error(f"Vendor data enrichment failed for {self.name}: {e}")
            self.enrichment_status = f"Enrichment failed: {str(e)}"
            self.message_post(
                body=_("Data enrichment failed: %s") % str(e),
                message_type='notification'
            )

    def _enrich_basic_company_info(self):
        """Enrich basic company information using AI and web scraping"""
        prompt = f"""
        Analyze and enrich the following vendor information:
        
        Company Name: {self.vendor_name}
        Website: {self.vendor_website or 'Not provided'}
        Email: {self.vendor_email or 'Not provided'}
        Phone: {self.vendor_phone or 'Not provided'}
        Address: {self.vendor_address or 'Not provided'}
        
        Additional Info: {self.raw_vendor_input or 'None'}
        
        Please provide enriched information in JSON format including:
        - Full company name and legal name
        - Industry classification
        - Company size (employees)
        - Year established
        - Business description
        - Key products/services
        - Geographic presence
        - Contact information validation
        
        Return only valid JSON.
        """
        
        try:
            response = self.env['purchase.ai.service'].call_ai_service(
                'vendor_suggestion', prompt
            )
            
            # Parse AI response
            content = response.get('content', '{}')
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback: extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return {}
                
        except Exception as e:
            _logger.warning(f"AI enrichment failed for {self.vendor_name}: {e}")
            return {}

    def _enrich_financial_data(self):
        """Enrich financial data from external APIs and AI analysis"""
        financial_data = {}
        
        try:
            # Try to get financial data from external APIs
            # This would integrate with services like Dun & Bradstreet, etc.
            
            # For now, use AI to analyze available information
            prompt = f"""
            Analyze the financial stability and creditworthiness of:
            Company: {self.vendor_name}
            Website: {self.vendor_website or 'Not available'}
            
            Based on publicly available information, provide a financial assessment including:
            - Estimated annual revenue range
            - Credit risk assessment
            - Financial stability indicators
            - Payment history reputation
            - Business growth trends
            
            Return assessment in JSON format with risk scores (0-1, where 1 is highest risk).
            """
            
            response = self.env['purchase.ai.service'].call_ai_service(
                'risk_assessment', prompt
            )
            
            content = response.get('content', '{}')
            try:
                financial_data = json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    financial_data = json.loads(json_match.group())
                    
        except Exception as e:
            _logger.warning(f"Financial data enrichment failed: {e}")
            
        return financial_data

    def _enrich_compliance_data(self):
        """Enrich compliance and certification data"""
        compliance_data = {}
        
        try:
            # Analyze documents if provided
            document_analysis = ""
            if self.document_ids:
                document_analysis = self._analyze_vendor_documents()
            
            prompt = f"""
            Analyze compliance and certification status for:
            Company: {self.vendor_name}
            Industry: {self.vendor_category or 'Unknown'}
            
            Document Analysis: {document_analysis}
            
            Assess compliance with:
            - Industry-specific regulations
            - Quality certifications (ISO, etc.)
            - Environmental standards
            - Labor compliance
            - Data protection regulations
            - Anti-corruption policies
            
            Return compliance assessment in JSON format with:
            - Compliance scores by category (0-1)
            - Missing certifications
            - Risk areas
            - Recommendations
            """
            
            response = self.env['purchase.ai.service'].call_ai_service(
                'compliance_check', prompt
            )
            
            content = response.get('content', '{}')
            try:
                compliance_data = json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    compliance_data = json.loads(json_match.group())
                    
        except Exception as e:
            _logger.warning(f"Compliance data enrichment failed: {e}")
            
        return compliance_data

    def _enrich_market_data(self):
        """Enrich market intelligence data"""
        market_data = {}
        
        try:
            prompt = f"""
            Provide market intelligence for:
            Company: {self.vendor_name}
            Industry: {self.vendor_category or 'Unknown'}
            
            Analyze:
            - Market position and reputation
            - Competitive landscape
            - Customer reviews and feedback
            - Recent news and developments
            - Market share and growth
            - Key competitors
            - Pricing competitiveness
            
            Return market analysis in JSON format.
            """
            
            response = self.env['purchase.ai.service'].call_ai_service(
                'market_analysis', prompt
            )
            
            content = response.get('content', '{}')
            try:
                market_data = json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    market_data = json.loads(json_match.group())
                    
        except Exception as e:
            _logger.warning(f"Market data enrichment failed: {e}")
            
        return market_data

    def _analyze_vendor_documents(self):
        """Analyze uploaded vendor documents using AI"""
        analysis_results = []
        
        for document in self.document_ids:
            try:
                # Prepare file data for AI analysis
                file_data = {
                    'name': document.name,
                    'type': document.mimetype,
                    'data': document.datas.decode('utf-8') if document.datas else ''
                }
                
                prompt = f"""
                Analyze the following vendor document: {document.name}
                
                Extract key information including:
                - Certifications and licenses
                - Compliance statements
                - Financial information
                - Contact details
                - Business capabilities
                - Quality standards
                
                Provide a structured summary of findings.
                """
                
                response = self.env['purchase.ai.service'].call_ai_service(
                    'document_analysis', prompt, files=[file_data]
                )
                
                analysis_results.append({
                    'document': document.name,
                    'analysis': response.get('content', '')
                })
                
            except Exception as e:
                _logger.warning(f"Document analysis failed for {document.name}: {e}")
                
        return analysis_results

    def action_submit_to_ai_review(self):
        """Submit vendor for AI risk assessment and review"""
        self.ensure_one()
        if self.state != 'data_enrichment':
            raise UserError(_("Can only submit to AI review from data enrichment state"))
        
        self.state = 'ai_review'
        self.last_ai_analysis = fields.Datetime.now()
        
        try:
            # Prepare comprehensive AI prompt
            prompt = self._prepare_ai_risk_assessment_prompt()
            
            # Get AI risk assessment
            response = self.env['purchase.ai.service'].call_ai_service(
                'risk_assessment', prompt
            )
            
            # Process AI response
            self._process_ai_risk_assessment(response)
            
            # Determine next step based on risk score
            if self.approval_required:
                self.action_submit_for_approval()
            else:
                self.action_auto_approve()
                
        except Exception as e:
            _logger.error(f"AI review failed for {self.name}: {e}")
            self.message_post(
                body=_("AI review failed: %s") % str(e),
                message_type='notification'
            )

    def _prepare_ai_risk_assessment_prompt(self):
        """Prepare comprehensive prompt for AI risk assessment"""
        enriched_summary = ""
        if self.enriched_data:
            enriched_summary = json.dumps(self.enriched_data, indent=2)
        
        return f"""
        Conduct a comprehensive risk assessment for the following vendor:
        
        BASIC INFORMATION:
        - Company Name: {self.vendor_name}
        - Category: {self.vendor_category or 'Unknown'}
        - Expected Annual Spend: {self.expected_annual_spend or 'Not specified'}
        - Priority: {self.priority}
        
        ENRICHED DATA:
        {enriched_summary}
        
        ASSESSMENT REQUIREMENTS:
        Please provide a detailed risk assessment including:
        
        1. Risk Component Scores (0.0 to 1.0, where 1.0 is highest risk):
           - financial_risk: Financial stability and creditworthiness
           - compliance_risk: Regulatory and certification compliance
           - operational_risk: Delivery and performance capabilities
           - reputation_risk: Market reputation and customer feedback
           - security_risk: Data security and cybersecurity posture
        
        2. Overall Risk Assessment:
           - Summary of key risk factors
           - Mitigation recommendations
           - Approval recommendation (approve/reject/conditional)
        
        3. Vendor Strengths and Weaknesses
        
        4. Recommended Contract Terms and Conditions
        
        Return response in JSON format with the following structure:
        {{
            "risk_components": {{
                "financial_risk": 0.0-1.0,
                "compliance_risk": 0.0-1.0,
                "operational_risk": 0.0-1.0,
                "reputation_risk": 0.0-1.0,
                "security_risk": 0.0-1.0
            }},
            "overall_assessment": "text",
            "recommendation": "approve|reject|conditional",
            "strengths": ["list of strengths"],
            "weaknesses": ["list of weaknesses"],
            "mitigation_strategies": ["list of strategies"],
            "contract_recommendations": ["list of recommendations"]
        }}
        """

    def _process_ai_risk_assessment(self, ai_response):
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
            
            # Store risk components
            self.risk_components = assessment.get('risk_components', {})
            
            # Store AI recommendations
            recommendations = []
            if assessment.get('overall_assessment'):
                recommendations.append(f"Overall Assessment: {assessment['overall_assessment']}")
            if assessment.get('strengths'):
                recommendations.append(f"Strengths: {', '.join(assessment['strengths'])}")
            if assessment.get('weaknesses'):
                recommendations.append(f"Weaknesses: {', '.join(assessment['weaknesses'])}")
            if assessment.get('mitigation_strategies'):
                recommendations.append(f"Mitigation Strategies: {', '.join(assessment['mitigation_strategies'])}")
            if assessment.get('contract_recommendations'):
                recommendations.append(f"Contract Recommendations: {', '.join(assessment['contract_recommendations'])}")
            
            self.ai_recommendations = '\n\n'.join(recommendations)
            
            # Store compliance check results
            self.compliance_check = {
                'recommendation': assessment.get('recommendation', 'conditional'),
                'assessment_date': fields.Datetime.now().isoformat(),
                'ai_confidence': ai_response.get('confidence', 0.8),
            }
            
        except Exception as e:
            _logger.error(f"Failed to process AI risk assessment: {e}")
            # Fallback: set default values
            self.risk_components = {
                'financial_risk': 0.5,
                'compliance_risk': 0.5,
                'operational_risk': 0.5,
                'reputation_risk': 0.5,
                'security_risk': 0.5,
            }
            self.ai_recommendations = f"AI assessment processing failed: {str(e)}"

    def action_submit_for_approval(self):
        """Submit vendor for manual approval"""
        self.ensure_one()
        if self.state != 'ai_review':
            raise UserError(_("Can only submit for approval from AI review state"))
        
        self.state = 'pending_approval'
        
        # Create approval activity
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=f'Vendor Approval Required: {self.vendor_name}',
            note=f'AI Risk Score: {self.ai_risk_score:.2f}\n\nAI Recommendations:\n{self.ai_recommendations}',
            user_id=self.env.ref('purchase.group_purchase_manager').users[0].id if self.env.ref('purchase.group_purchase_manager').users else self.env.user.id
        )
        
        self.message_post(
            body=_("Vendor submitted for approval. Risk score: %.2f") % self.ai_risk_score,
            message_type='notification'
        )

    def action_auto_approve(self):
        """Auto-approve vendor based on low risk score"""
        self.ensure_one()
        if self.state != 'ai_review':
            raise UserError(_("Can only auto-approve from AI review state"))
        
        settings = self.env['purchase.ai.settings'].get_settings()
        if self.ai_risk_score > settings.auto_approve_threshold:
            raise UserError(_("Risk score too high for auto-approval"))
        
        self.action_approve()

    def action_approve(self):
        """Approve vendor and create partner record"""
        self.ensure_one()
        if self.state not in ['pending_approval', 'ai_review']:
            raise UserError(_("Can only approve from pending approval or AI review state"))
        
        # Create vendor partner record
        vendor_vals = self._prepare_vendor_vals()
        vendor = self.env['res.partner'].create(vendor_vals)
        
        self.approved_vendor_id = vendor.id
        self.approved_by = self.env.user.id
        self.approval_date = fields.Datetime.now()
        self.state = 'approved'
        
        # Complete any pending activities
        self.activity_ids.action_done()
        
        self.message_post(
            body=_("Vendor approved and created: %s") % vendor.name,
            message_type='notification'
        )
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Vendor'),
            'res_model': 'res.partner',
            'res_id': vendor.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_reject(self):
        """Reject vendor creation request"""
        self.ensure_one()
        if self.state not in ['pending_approval', 'ai_review']:
            raise UserError(_("Can only reject from pending approval or AI review state"))
        
        # Open rejection reason wizard
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rejection Reason'),
            'res_model': 'vendor.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_id': self.id}
        }

    def _prepare_vendor_vals(self):
        """Prepare values for creating vendor partner record"""
        vals = {
            'name': self.vendor_name,
            'is_company': True,
            'supplier_rank': 1,
            'customer_rank': 0,
            'email': self.vendor_email,
            'phone': self.vendor_phone,
            'website': self.vendor_website,
            'street': self.vendor_address,
            'category_id': [(6, 0, self._get_vendor_categories())],
        }
        
        # Add enriched data if available
        if self.enriched_data:
            basic_info = self.enriched_data.get('basic_info', {})
            vals.update({
                'comment': basic_info.get('business_description', ''),
                'industry_id': self._get_industry_id(basic_info.get('industry_classification')),
            })
        
        return vals

    def _get_vendor_categories(self):
        """Get or create vendor categories based on enriched data"""
        categories = []
        
        # Create category based on vendor_category
        if self.vendor_category:
            category = self.env['res.partner.category'].search([
                ('name', '=', self.vendor_category.title())
            ], limit=1)
            if not category:
                category = self.env['res.partner.category'].create({
                    'name': self.vendor_category.title()
                })
            categories.append(category.id)
        
        # Add AI-suggested categories from enriched data
        if self.enriched_data:
            basic_info = self.enriched_data.get('basic_info', {})
            if basic_info.get('industry_classification'):
                industry_category = self.env['res.partner.category'].search([
                    ('name', '=', basic_info['industry_classification'])
                ], limit=1)
                if not industry_category:
                    industry_category = self.env['res.partner.category'].create({
                        'name': basic_info['industry_classification']
                    })
                categories.append(industry_category.id)
        
        return categories

    def _get_industry_id(self, industry_name):
        """Get or create industry record"""
        if not industry_name:
            return False
        
        # This would map to res.partner.industry if available
        # For now, we'll store in comment field
        return False

    def action_view_vendor(self):
        """View created vendor"""
        self.ensure_one()
        if not self.approved_vendor_id:
            raise UserError(_("No vendor has been created yet"))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor'),
            'res_model': 'res.partner',
            'res_id': self.approved_vendor_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_rerun_ai_analysis(self):
        """Rerun AI analysis with current data"""
        self.ensure_one()
        if self.state in ['approved', 'rejected']:
            raise UserError(_("Cannot rerun analysis for completed requests"))
        
        self.action_submit_to_ai_review() 