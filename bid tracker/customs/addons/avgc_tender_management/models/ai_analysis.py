from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import requests
import json
import base64
import logging

_logger = logging.getLogger(__name__)


class AIAnalysis(models.Model):
    _name = 'avgc.ai.analysis'
    _description = 'AI Document Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    name = fields.Char('Analysis Name', required=True, default='New Analysis')
    
    # Related Records
    tender_id = fields.Many2one('avgc.tender', string='Tender', ondelete='cascade')
    gem_bid_id = fields.Many2one('avgc.gem.bid', string='GeM Bid', ondelete='cascade')
    document_id = fields.Many2one('avgc.tender.document', string='Document')
    
    # AI Configuration
    ai_provider = fields.Selection([
        ('claude', 'Claude (Anthropic)'),
        ('gpt', 'GPT (OpenAI)'),
        ('gemini', 'Gemini (Google)'),
    ], string='AI Provider', required=True, default='claude', tracking=True)
    
    analysis_type = fields.Selection([
        ('document_summary', 'Document Summary'),
        ('compliance_check', 'Compliance Check'),
        ('risk_assessment', 'Risk Assessment'),
        ('bid_optimization', 'Bid Optimization'),
        ('tender_response', 'Tender Response Generation'),
        ('ocr_extraction', 'OCR Text Extraction'),
        ('gem_bid_analysis', 'GeM Bid Analysis'),
    ], string='Analysis Type', required=True, tracking=True)
    
    # Input Data
    input_text = fields.Text('Input Text')
    input_file = fields.Binary('Input File')
    input_filename = fields.Char('Input Filename')
    
    # Processing Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Results
    extracted_text = fields.Text('Extracted Text (OCR)')
    summary = fields.Text('AI Summary')
    analysis_result = fields.Text('Analysis Result')
    compliance_score = fields.Float('Compliance Score', digits=(5, 2))
    risk_score = fields.Float('Risk Score', digits=(5, 2))
    confidence_score = fields.Float('Confidence Score', digits=(5, 2))
    
    # Structured Results (JSON)
    structured_result = fields.Text('Structured Result (JSON)')
    key_insights = fields.Text('Key Insights')
    recommendations = fields.Text('Recommendations')
    
    # Processing Details
    processing_time = fields.Float('Processing Time (seconds)', digits=(10, 2))
    api_response_raw = fields.Text('Raw API Response')
    error_message = fields.Text('Error Message')
    
    # Metadata
    processed_by = fields.Many2one('res.users', string='Processed By', default=lambda self: self.env.user)
    processing_start = fields.Datetime('Processing Started')
    processing_end = fields.Datetime('Processing Completed')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New Analysis') == 'New Analysis':
            sequence = self.env['ir.sequence'].next_by_code('avgc.ai.analysis')
            vals['name'] = f"AI Analysis {sequence}" if sequence else 'New Analysis'
        return super(AIAnalysis, self).create(vals)
    
    def action_process(self):
        """Start AI analysis processing"""
        for record in self:
            record.status = 'queued'
            record._process_analysis()
    
    def _process_analysis(self):
        """Process the AI analysis"""
        self.ensure_one()
        
        try:
            self.status = 'processing'
            self.processing_start = fields.Datetime.now()
            self.message_post(body=_('AI analysis processing started.'))
            
            # Call appropriate AI service based on provider
            if self.ai_provider == 'claude':
                result = self._process_with_claude()
            elif self.ai_provider == 'gpt':
                result = self._process_with_gpt()
            elif self.ai_provider == 'gemini':
                result = self._process_with_gemini()
            else:
                raise UserError(_('Unsupported AI provider: %s') % self.ai_provider)
            
            # Store results
            self._store_results(result)
            
            self.status = 'completed'
            self.processing_end = fields.Datetime.now()
            
            # Calculate processing time
            if self.processing_start and self.processing_end:
                delta = self.processing_end - self.processing_start
                self.processing_time = delta.total_seconds()
            
            self.message_post(body=_('AI analysis completed successfully.'))
            
        except Exception as e:
            self.status = 'failed'
            self.error_message = str(e)
            self.processing_end = fields.Datetime.now()
            self.message_post(body=_('AI analysis failed: %s') % str(e))
            _logger.error(f"AI Analysis failed for record {self.id}: {str(e)}")
    
    def _process_with_claude(self):
        """Process analysis using Claude API"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('avgc.claude_api_key')
        if not api_key:
            raise UserError(_('Claude API key not configured. Please configure it in system parameters.'))
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
        
        # Prepare prompt based on analysis type
        prompt = self._prepare_prompt()
        
        data = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 4000,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise UserError(_('Claude API error: %s') % response.text)
        
        return response.json()
    
    def _process_with_gpt(self):
        """Process analysis using OpenAI GPT API"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('avgc.openai_api_key')
        if not api_key:
            raise UserError(_('OpenAI API key not configured. Please configure it in system parameters.'))
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        prompt = self._prepare_prompt()
        
        data = {
            'model': 'gpt-4',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert tender and procurement analyst.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 4000,
            'temperature': 0.1
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code != 200:
            raise UserError(_('OpenAI API error: %s') % response.text)
        
        return response.json()
    
    def _process_with_gemini(self):
        """Process analysis using Google Gemini API"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('avgc.gemini_api_key')
        if not api_key:
            raise UserError(_('Gemini API key not configured. Please configure it in system parameters.'))
        
        prompt = self._prepare_prompt()
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}'
        
        data = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': prompt
                        }
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.1,
                'maxOutputTokens': 4000
            }
        }
        
        response = requests.post(url, json=data, timeout=120)
        
        if response.status_code != 200:
            raise UserError(_('Gemini API error: %s') % response.text)
        
        return response.json()
    
    def _prepare_prompt(self):
        """Prepare prompt based on analysis type"""
        base_text = self.input_text or ""
        
        if self.analysis_type == 'document_summary':
            return f"""
            Please provide a comprehensive summary of the following tender/bid document:
            
            {base_text}
            
            Include:
            1. Key requirements and specifications
            2. Important dates and deadlines
            3. Financial information
            4. Evaluation criteria
            5. Compliance requirements
            
            Format the response as structured JSON with sections for each category.
            """
        
        elif self.analysis_type == 'compliance_check':
            return f"""
            Analyze the following document for compliance with standard tender requirements:
            
            {base_text}
            
            Check for:
            1. Required certifications and qualifications
            2. Financial requirements and EMD
            3. Technical specifications compliance
            4. Legal and regulatory compliance
            5. Documentation completeness
            
            Provide a compliance score (0-100) and detailed findings.
            """
        
        elif self.analysis_type == 'risk_assessment':
            return f"""
            Conduct a risk assessment for the following tender/bid:
            
            {base_text}
            
            Analyze:
            1. Financial risks
            2. Technical delivery risks
            3. Compliance risks
            4. Market competition risks
            5. Timeline and execution risks
            
            Provide risk scores and mitigation strategies.
            """
        
        elif self.analysis_type == 'bid_optimization':
            return f"""
            Provide bid optimization recommendations for:
            
            {base_text}
            
            Focus on:
            1. Competitive pricing strategies
            2. Technical solution optimization
            3. Value proposition enhancement
            4. Risk mitigation approaches
            5. Winning probability improvement
            
            Provide actionable recommendations.
            """
        
        elif self.analysis_type == 'gem_bid_analysis':
            return f"""
            Analyze this GeM bid for strategic insights:
            
            {base_text}
            
            Provide:
            1. Market analysis and competition assessment
            2. Pricing strategy recommendations
            3. Technical requirement analysis
            4. Delivery capability assessment
            5. Success probability and key factors
            
            Format as structured analysis with scores and recommendations.
            """
        
        else:
            return base_text
    
    def _store_results(self, api_result):
        """Store API results in appropriate fields"""
        self.api_response_raw = json.dumps(api_result, indent=2)
        
        try:
            if self.ai_provider == 'claude':
                content = api_result.get('content', [{}])[0].get('text', '')
            elif self.ai_provider == 'gpt':
                content = api_result.get('choices', [{}])[0].get('message', {}).get('content', '')
            elif self.ai_provider == 'gemini':
                content = api_result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            else:
                content = str(api_result)
            
            self.analysis_result = content
            
            # Try to parse structured results
            try:
                # Look for JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_content = content[start_idx:end_idx]
                    parsed_result = json.loads(json_content)
                    self.structured_result = json.dumps(parsed_result, indent=2)
                    
                    # Extract specific fields if available
                    if 'summary' in parsed_result:
                        self.summary = parsed_result['summary']
                    if 'compliance_score' in parsed_result:
                        self.compliance_score = parsed_result['compliance_score']
                    if 'risk_score' in parsed_result:
                        self.risk_score = parsed_result['risk_score']
                    if 'recommendations' in parsed_result:
                        self.recommendations = parsed_result['recommendations']
                    if 'key_insights' in parsed_result:
                        self.key_insights = parsed_result['key_insights']
                        
            except (json.JSONDecodeError, KeyError):
                # If JSON parsing fails, use the raw content
                self.summary = content[:1000] if len(content) > 1000 else content
                
        except Exception as e:
            _logger.error(f"Error storing AI analysis results: {str(e)}")
            self.analysis_result = str(api_result)


class AIConfiguration(models.Model):
    _name = 'avgc.ai.configuration'
    _description = 'AI Service Configuration'
    
    name = fields.Char('Configuration Name', required=True)
    ai_provider = fields.Selection([
        ('claude', 'Claude (Anthropic)'),
        ('gpt', 'GPT (OpenAI)'),
        ('gemini', 'Gemini (Google)'),
    ], string='AI Provider', required=True)
    
    # API Configuration
    api_endpoint = fields.Char('API Endpoint')
    model_name = fields.Char('Model Name', required=True)
    max_tokens = fields.Integer('Max Tokens', default=4000)
    temperature = fields.Float('Temperature', default=0.1, digits=(3, 2))
    
    # Usage Limits
    daily_limit = fields.Integer('Daily Request Limit', default=1000)
    monthly_limit = fields.Integer('Monthly Request Limit', default=30000)
    cost_per_request = fields.Float('Cost per Request', digits=(10, 4))
    
    # Status
    is_active = fields.Boolean('Active', default=True)
    is_default = fields.Boolean('Default Configuration', default=False)
    
    # Usage Statistics
    requests_today = fields.Integer('Requests Today', default=0)
    requests_month = fields.Integer('Requests This Month', default=0)
    total_cost = fields.Float('Total Cost', digits=(10, 2))
    
    last_used = fields.Datetime('Last Used')
    
    @api.model
    def get_default_config(self, provider):
        """Get default configuration for a provider"""
        config = self.search([
            ('ai_provider', '=', provider),
            ('is_active', '=', True),
            ('is_default', '=', True)
        ], limit=1)
        
        if not config:
            config = self.search([
                ('ai_provider', '=', provider),
                ('is_active', '=', True)
            ], limit=1)
        
        return config
    
    def increment_usage(self):
        """Increment usage counters"""
        self.ensure_one()
        self.requests_today += 1
        self.requests_month += 1
        self.total_cost += self.cost_per_request
        self.last_used = fields.Datetime.now()


class OCRService(models.Model):
    _name = 'avgc.ocr.service'
    _description = 'OCR Document Processing Service'
    
    name = fields.Char('Service Name', required=True)
    document_id = fields.Many2one('avgc.tender.document', string='Document')
    
    # Input
    input_file = fields.Binary('Input File', required=True)
    input_filename = fields.Char('Input Filename')
    
    # Processing
    status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Status', default='pending')
    
    # Results
    extracted_text = fields.Text('Extracted Text')
    confidence_score = fields.Float('OCR Confidence Score', digits=(5, 2))
    page_count = fields.Integer('Page Count')
    
    # Error Handling
    error_message = fields.Text('Error Message')
    processing_time = fields.Float('Processing Time (seconds)', digits=(10, 2))
    
    def action_process_ocr(self):
        """Process OCR extraction"""
        for record in self:
            record.status = 'processing'
            try:
                # Use Tesseract.js or similar OCR service
                # This is a placeholder - implement actual OCR processing
                record._process_with_tesseract()
                record.status = 'completed'
            except Exception as e:
                record.status = 'failed'
                record.error_message = str(e)
    
    def _process_with_tesseract(self):
        """Process document with Tesseract OCR"""
        # Placeholder for actual OCR implementation
        # In real implementation, this would integrate with Tesseract.js or similar
        self.extracted_text = "OCR processing completed - implement actual OCR service"
        self.confidence_score = 95.0
        self.page_count = 1