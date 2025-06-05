import json
import time
import logging
import requests
import hashlib
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config
import threading
from collections import defaultdict

_logger = logging.getLogger(__name__)

class AIServiceManager(models.Model):
    _name = 'purchase.ai.service'
    _description = 'AI Service Manager with Multi-Provider Support'
    _order = 'priority desc, id'

    name = fields.Char('Service Name', required=True)
    provider = fields.Selection([
        ('claude', 'Claude AI (Anthropic)'),
        ('openai', 'OpenAI/ChatGPT'),
        ('gemini', 'Google Gemini'),
        ('azure_openai', 'Azure OpenAI'),
        ('huggingface', 'HuggingFace'),
    ], required=True, string='AI Provider')
    
    api_key = fields.Char('API Key', required=True)
    api_endpoint = fields.Char('API Endpoint', help="Custom endpoint URL if needed")
    model_name = fields.Char('Model Name', help="Specific model to use (e.g., gpt-4, claude-3-opus)")
    
    usage_type = fields.Selection([
        ('vendor_suggestion', 'Vendor Suggestions'),
        ('price_analysis', 'Price Analysis'),
        ('contract_review', 'Contract Review'),
        ('risk_assessment', 'Risk Assessment'),
        ('document_analysis', 'Document Analysis'),
        ('compliance_check', 'Compliance Checking'),
        ('market_analysis', 'Market Analysis'),
        ('negotiation_support', 'Negotiation Support'),
    ], required=True, string='Usage Type')
    
    active = fields.Boolean('Active', default=True)
    priority = fields.Integer('Priority', default=10, help="Higher priority services are used first")
    
    # Rate limiting and retry configuration
    max_retries = fields.Integer('Max Retries', default=3)
    retry_delay = fields.Float('Retry Delay (seconds)', default=1.0)
    rate_limit_per_minute = fields.Integer('Rate Limit per Minute', default=60)
    rate_limit_per_hour = fields.Integer('Rate Limit per Hour', default=1000)
    
    # Performance tracking
    total_requests = fields.Integer('Total Requests', readonly=True)
    successful_requests = fields.Integer('Successful Requests', readonly=True)
    failed_requests = fields.Integer('Failed Requests', readonly=True)
    avg_response_time = fields.Float('Avg Response Time (seconds)', readonly=True)
    last_used = fields.Datetime('Last Used', readonly=True)
    
    # Cost tracking
    cost_per_1k_tokens = fields.Float('Cost per 1K Tokens', default=0.0)
    total_tokens_used = fields.Integer('Total Tokens Used', readonly=True)
    total_cost = fields.Float('Total Cost', readonly=True)
    
    # Advanced configuration
    temperature = fields.Float('Temperature', default=0.1, help="Creativity level (0.0-1.0)")
    max_tokens = fields.Integer('Max Tokens', default=4000)
    timeout = fields.Integer('Timeout (seconds)', default=30)
    
    # Rate limiting tracking (in-memory)
    _rate_limit_tracker = defaultdict(list)
    _lock = threading.Lock()

    @api.constrains('temperature')
    def _check_temperature(self):
        for record in self:
            if not 0.0 <= record.temperature <= 1.0:
                raise ValidationError(_("Temperature must be between 0.0 and 1.0"))

    def _check_rate_limit(self):
        """Check if we're within rate limits"""
        with self._lock:
            now = time.time()
            key = f"{self.id}_{self.provider}"
            
            # Clean old entries
            self._rate_limit_tracker[key] = [
                timestamp for timestamp in self._rate_limit_tracker[key]
                if now - timestamp < 3600  # Keep last hour
            ]
            
            # Check minute limit
            minute_ago = now - 60
            recent_requests = [
                timestamp for timestamp in self._rate_limit_tracker[key]
                if timestamp > minute_ago
            ]
            
            if len(recent_requests) >= self.rate_limit_per_minute:
                raise UserError(_("Rate limit exceeded: %d requests per minute") % self.rate_limit_per_minute)
            
            # Check hour limit
            if len(self._rate_limit_tracker[key]) >= self.rate_limit_per_hour:
                raise UserError(_("Rate limit exceeded: %d requests per hour") % self.rate_limit_per_hour)
            
            # Record this request
            self._rate_limit_tracker[key].append(now)

    def _get_cache_key(self, prompt, context=None):
        """Generate cache key for request"""
        cache_data = {
            'provider': self.provider,
            'model': self.model_name,
            'prompt': prompt,
            'context': context or {},
            'temperature': self.temperature,
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()

    def _get_cached_response(self, cache_key):
        """Get cached response if available and not expired"""
        cache = self.env['ai.cache'].search([
            ('cache_key', '=', cache_key),
            ('expires_at', '>', fields.Datetime.now())
        ], limit=1)
        
        if cache:
            _logger.info(f"Using cached AI response for key: {cache_key}")
            cache.hit_count += 1
            return json.loads(cache.response_data)
        return None

    def _cache_response(self, cache_key, response_data):
        """Cache the AI response"""
        settings = self.env['purchase.ai.settings'].get_settings()
        if not settings.enable_response_caching:
            return
            
        expires_at = fields.Datetime.now() + timedelta(hours=settings.cache_expiry_hours)
        
        self.env['ai.cache'].create({
            'cache_key': cache_key,
            'response_data': json.dumps(response_data),
            'expires_at': expires_at,
            'ai_service_id': self.id,
        })

    @api.model
    def call_ai_service(self, usage_type, prompt, context=None, files=None):
        """Main entry point for AI service calls"""
        # Find best available service for this usage type
        service = self.search([
            ('usage_type', '=', usage_type),
            ('active', '=', True)
        ], order='priority desc', limit=1)
        
        if not service:
            raise UserError(_("No active AI service found for usage type: %s") % usage_type)
        
        return service.call_ai(prompt, context, files)

    def call_ai(self, prompt, context=None, files=None, attempt=1):
        """Call AI service with retry logic and caching"""
        start_time = time.time()
        
        try:
            # Check rate limits
            self._check_rate_limit()
            
            # Check cache first
            cache_key = self._get_cache_key(prompt, context)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
            
            # Make API call based on provider
            if self.provider == 'claude':
                response = self._call_claude(prompt, context, files)
            elif self.provider == 'openai':
                response = self._call_openai(prompt, context, files)
            elif self.provider == 'gemini':
                response = self._call_gemini(prompt, context, files)
            elif self.provider == 'azure_openai':
                response = self._call_azure_openai(prompt, context, files)
            elif self.provider == 'huggingface':
                response = self._call_huggingface(prompt, context, files)
            else:
                raise UserError(_("Unsupported AI provider: %s") % self.provider)
            
            # Update performance metrics
            response_time = time.time() - start_time
            self._update_metrics(True, response_time, response.get('tokens_used', 0))
            
            # Cache the response
            self._cache_response(cache_key, response)
            
            # Log the request
            self._log_request(prompt, context, response, True)
            
            return response
            
        except Exception as e:
            _logger.error(f"AI call failed on attempt {attempt} for {self.provider}: {e}")
            
            # Update failure metrics
            self._update_metrics(False, time.time() - start_time, 0)
            
            # Log the failed request
            self._log_request(prompt, context, {'error': str(e)}, False)
            
            # Retry logic
            if attempt < self.max_retries:
                time.sleep(self.retry_delay * attempt)  # Exponential backoff
                return self.call_ai(prompt, context, files, attempt + 1)
            else:
                # Try fallback service
                fallback = self._get_fallback_service()
                if fallback and fallback.id != self.id:
                    _logger.info(f"Trying fallback service: {fallback.name}")
                    return fallback.call_ai(prompt, context, files, 1)
                
                raise UserError(_("AI service failed after %d attempts: %s") % (self.max_retries, str(e)))

    def _get_fallback_service(self):
        """Get fallback service for this usage type"""
        return self.search([
            ('usage_type', '=', self.usage_type),
            ('active', '=', True),
            ('id', '!=', self.id)
        ], order='priority desc', limit=1)

    def _call_claude(self, prompt, context=None, files=None):
        """Call Claude AI API"""
        try:
            import anthropic
        except ImportError:
            raise UserError(_("anthropic package not installed. Run: pip install anthropic"))
        
        client = anthropic.Anthropic(api_key=self.api_key)
        
        messages = [{"role": "user", "content": prompt}]
        
        # Handle file uploads for Claude
        if files:
            # Claude supports image analysis
            for file_data in files:
                if file_data.get('type', '').startswith('image/'):
                    messages[0]["content"] = [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": file_data['type'],
                                "data": file_data['data']
                            }
                        }
                    ]
        
        response = client.messages.create(
            model=self.model_name or "claude-3-opus-20240229",
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=messages
        )
        
        return {
            'content': response.content[0].text,
            'tokens_used': response.usage.input_tokens + response.usage.output_tokens,
            'model': response.model,
            'provider': 'claude'
        }

    def _call_openai(self, prompt, context=None, files=None):
        """Call OpenAI API"""
        try:
            import openai
        except ImportError:
            raise UserError(_("openai package not installed. Run: pip install openai"))
        
        client = openai.OpenAI(api_key=self.api_key)
        
        messages = [{"role": "user", "content": prompt}]
        
        # Handle file uploads for OpenAI (vision models)
        if files and self.model_name and 'vision' in self.model_name:
            content = [{"type": "text", "text": prompt}]
            for file_data in files:
                if file_data.get('type', '').startswith('image/'):
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{file_data['type']};base64,{file_data['data']}"
                        }
                    })
            messages[0]["content"] = content
        
        response = client.chat.completions.create(
            model=self.model_name or "gpt-4",
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )
        
        return {
            'content': response.choices[0].message.content,
            'tokens_used': response.usage.total_tokens,
            'model': response.model,
            'provider': 'openai'
        }

    def _call_gemini(self, prompt, context=None, files=None):
        """Call Google Gemini API with multi-modal support"""
        try:
            import google.generativeai as genai
        except ImportError:
            raise UserError(_("google-generativeai package not installed. Run: pip install google-generativeai"))
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name or 'gemini-pro')
        
        # Handle multi-modal inputs
        if files:
            # Gemini supports various file types
            content = [prompt]
            for file_data in files:
                # Convert file data to appropriate format for Gemini
                content.append({
                    'mime_type': file_data['type'],
                    'data': file_data['data']
                })
            response = model.generate_content(content)
        else:
            response = model.generate_content(prompt)
        
        return {
            'content': response.text,
            'tokens_used': getattr(response, 'usage_metadata', {}).get('total_token_count', 0),
            'model': self.model_name or 'gemini-pro',
            'provider': 'gemini'
        }

    def _call_azure_openai(self, prompt, context=None, files=None):
        """Call Azure OpenAI API"""
        # Similar to OpenAI but with Azure-specific configuration
        headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key
        }
        
        data = {
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }
        
        response = requests.post(
            self.api_endpoint,
            headers=headers,
            json=data,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Azure OpenAI API error: {response.text}")
        
        result = response.json()
        return {
            'content': result['choices'][0]['message']['content'],
            'tokens_used': result.get('usage', {}).get('total_tokens', 0),
            'model': self.model_name,
            'provider': 'azure_openai'
        }

    def _call_huggingface(self, prompt, context=None, files=None):
        """Call HuggingFace API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'inputs': prompt,
            'parameters': {
                'max_new_tokens': self.max_tokens,
                'temperature': self.temperature
            }
        }
        
        api_url = self.api_endpoint or f"https://api-inference.huggingface.co/models/{self.model_name}"
        
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"HuggingFace API error: {response.text}")
        
        result = response.json()
        return {
            'content': result[0].get('generated_text', ''),
            'tokens_used': 0,  # HuggingFace doesn't always provide token count
            'model': self.model_name,
            'provider': 'huggingface'
        }

    def _update_metrics(self, success, response_time, tokens_used):
        """Update performance metrics"""
        self.total_requests += 1
        self.last_used = fields.Datetime.now()
        
        if success:
            self.successful_requests += 1
            self.total_tokens_used += tokens_used
            self.total_cost += (tokens_used / 1000) * self.cost_per_1k_tokens
        else:
            self.failed_requests += 1
        
        # Update average response time
        if self.total_requests > 1:
            self.avg_response_time = (
                (self.avg_response_time * (self.total_requests - 1) + response_time) / 
                self.total_requests
            )
        else:
            self.avg_response_time = response_time

    def _log_request(self, prompt, context, response, success):
        """Log AI request for audit trail"""
        self.env['purchase.ai.request.log'].create({
            'service_id': self.id,
            'request_payload': json.dumps({
                'prompt': prompt[:1000],  # Truncate for storage
                'context': context
            }),
            'response_payload': json.dumps(response),
            'success': success,
            'user_id': self.env.user.id,
            'timestamp': fields.Datetime.now()
        })

    def action_test_connection(self):
        """Test AI service connection"""
        try:
            test_prompt = "Hello, this is a test message. Please respond with 'Connection successful.'"
            response = self.call_ai(test_prompt)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test'),
                    'message': _('AI service connection successful! Response: %s') % response.get('content', '')[:100],
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test Failed'),
                    'message': _('Error: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_view_logs(self):
        """View AI request logs for this service"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('AI Request Logs'),
            'res_model': 'purchase.ai.request.log',
            'view_mode': 'tree,form',
            'domain': [('service_id', '=', self.id)],
            'context': {'default_service_id': self.id}
        } 