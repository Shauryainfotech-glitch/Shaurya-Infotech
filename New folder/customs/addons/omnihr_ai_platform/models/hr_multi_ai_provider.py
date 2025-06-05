from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import datetime, timedelta
import json

_logger = logging.getLogger(__name__)

class HRMultiAIProvider(models.Model):
    _name = 'hr.multi.ai.provider'
    _description = 'Multi-AI Provider Configuration'
    _rec_name = 'name'
    
    name = fields.Char('Provider Name', required=True)
    provider_type = fields.Selection([
        ('openai', 'OpenAI'),
        ('claude', 'Claude (Anthropic)'),
        ('gemini', 'Google Gemini'),
    ], 'Provider Type', required=True)
    
    active = fields.Boolean('Active', default=True)
    priority = fields.Integer('Priority', default=10, help='Lower number = higher priority')
    
    # API Configuration
    api_key = fields.Char('API Key', required=True)
    api_endpoint = fields.Char('API Endpoint')
    model_name = fields.Char('Model Name', required=True)
    
    # Provider-specific settings
    max_tokens = fields.Integer('Max Tokens', default=4000)
    temperature = fields.Float('Temperature', default=0.7)
    timeout = fields.Integer('Timeout (seconds)', default=30)
    
    # Performance Metrics
    total_requests = fields.Integer('Total Requests', readonly=True)
    successful_requests = fields.Integer('Successful Requests', readonly=True)
    failed_requests = fields.Integer('Failed Requests', readonly=True)
    avg_response_time = fields.Float('Average Response Time (s)', readonly=True)
    total_cost = fields.Float('Total Cost ($)', readonly=True)
    
    # Status
    last_health_check = fields.Datetime('Last Health Check', readonly=True)
    health_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('offline', 'Offline'),
    ], 'Health Status', default='offline', readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('provider_type') == 'openai' and not vals.get('model_name'):
                vals['model_name'] = 'gpt-4-turbo'
            elif vals.get('provider_type') == 'claude' and not vals.get('model_name'):
                vals['model_name'] = 'claude-3-sonnet-20240229'
            elif vals.get('provider_type') == 'gemini' and not vals.get('model_name'):
                vals['model_name'] = 'gemini-pro'
        return super().create(vals_list)
    
    def test_connection(self):
        """Test connection to AI provider"""
        try:
            if self.provider_type == 'openai':
                success = self._test_openai_connection()
            elif self.provider_type == 'claude':
                success = self._test_claude_connection()
            elif self.provider_type == 'gemini':
                success = self._test_gemini_connection()
            else:
                raise Exception(f"Unsupported provider type: {self.provider_type}")
            
            if success:
                self.health_status = 'healthy'
                self.last_health_check = fields.Datetime.now()
                return {'type': 'ir.actions.client', 'tag': 'display_notification',
                        'params': {'message': _('Connection successful!'), 'type': 'success'}}
            else:
                raise Exception("No response received")
                
        except Exception as e:
            self.health_status = 'error'
            self.last_health_check = fields.Datetime.now()
            _logger.error(f"AI Provider {self.name} connection test failed: {str(e)}")
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'message': _('Connection failed: %s') % str(e), 'type': 'danger'}}
    
    def _test_openai_connection(self):
        """Test OpenAI connection"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            return bool(response.choices)
        except ImportError:
            raise Exception("OpenAI library not installed. Please install: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI connection failed: {str(e)}")
    
    def _test_claude_connection(self):
        """Test Claude connection"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test connection"}]
            )
            return bool(response.content)
        except ImportError:
            raise Exception("Anthropic library not installed. Please install: pip install anthropic")
        except Exception as e:
            raise Exception(f"Claude connection failed: {str(e)}")
    
    def _test_gemini_connection(self):
        """Test Gemini connection"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content("Test connection")
            return bool(response.text)
        except ImportError:
            raise Exception("Google Generative AI library not installed. Please install: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Gemini connection failed: {str(e)}")
    
    def execute_request(self, prompt, system_prompt=None, **kwargs):
        """Execute AI request with error handling and metrics tracking"""
        start_time = datetime.now()
        
        try:
            if self.provider_type == 'openai':
                response = self._execute_openai_request(prompt, system_prompt, **kwargs)
            elif self.provider_type == 'claude':
                response = self._execute_claude_request(prompt, system_prompt, **kwargs)
            elif self.provider_type == 'gemini':
                response = self._execute_gemini_request(prompt, system_prompt, **kwargs)
            else:
                raise UserError(_('Unsupported provider type: %s') % self.provider_type)
            
            # Update metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_success_metrics(response_time, kwargs.get('estimated_cost', 0))
            
            return response
            
        except Exception as e:
            self._update_failure_metrics()
            _logger.error(f"AI request failed for provider {self.name}: {str(e)}")
            raise UserError(_('AI request failed: %s') % str(e))
    
    def _execute_openai_request(self, prompt, system_prompt=None, **kwargs):
        """Execute OpenAI request"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, timeout=self.timeout)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
            )
            
            return {
                'content': response.choices[0].message.content,
                'model': response.model,
                'usage': response.usage._asdict() if response.usage else {},
                'finish_reason': response.choices[0].finish_reason,
            }
        except ImportError:
            raise Exception("OpenAI library not installed")
    
    def _execute_claude_request(self, prompt, system_prompt=None, **kwargs):
        """Execute Claude request"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key, timeout=self.timeout)
            
            response = client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'content': response.content[0].text if response.content else "",
                'model': response.model,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                },
                'stop_reason': response.stop_reason,
            }
        except ImportError:
            raise Exception("Anthropic library not installed")
    
    def _execute_gemini_request(self, prompt, system_prompt=None, **kwargs):
        """Execute Gemini request"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_prompt
            )
            
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            
            return {
                'content': response.text,
                'model': self.model_name,
                'usage': {
                    'prompt_token_count': response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                    'candidates_token_count': response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
                },
                'finish_reason': response.candidates[0].finish_reason if response.candidates else None,
            }
        except ImportError:
            raise Exception("Google Generative AI library not installed")
    
    def _update_success_metrics(self, response_time, cost):
        """Update success metrics"""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_cost += cost
        
        # Update average response time
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time + response_time) / 2
    
    def _update_failure_metrics(self):
        """Update failure metrics"""
        self.total_requests += 1
        self.failed_requests += 1 