import requests
import json
from odoo import models, api
from odoo.exceptions import UserError

class AiLlmClient(models.AbstractModel):
    _name = 'ai.llm.client'
    _description = 'AI LLM Client'
    
    @api.model
    def send_request(self, account_id, messages, **kwargs):
        """Send request to AI provider"""
        account = self.env['ai.llm.account'].browse(account_id)
        if not account or account.state != 'active':
            raise UserError("No active AI account available")
        
        provider = account.provider_id
        
        # Route to appropriate provider method
        if provider.code == 'openai':
            return self._send_openai_request(account, messages, **kwargs)
        elif provider.code == 'anthropic':
            return self._send_anthropic_request(account, messages, **kwargs)
        else:
            raise UserError(f"Provider {provider.name} not implemented")
    
    def _send_openai_request(self, account, messages, **kwargs):
        """Send request to OpenAI API"""
        headers = {
            'Authorization': f'Bearer {account.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': account.provider_id.model_name,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', account.provider_id.max_tokens),
            'temperature': kwargs.get('temperature', account.provider_id.temperature),
        }
        
        try:
            response = requests.post(
                account.provider_id.api_endpoint,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'content': result['choices'][0]['message']['content'],
                'usage': result.get('usage', {}),
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _send_anthropic_request(self, account, messages, **kwargs):
        """Send request to Anthropic API"""
        headers = {
            'x-api-key': account.api_key,
            'Content-Type': 'application/json'
        }
        
        # Convert messages to Anthropic format
        prompt = self._convert_to_anthropic_format(messages)
        
        data = {
            'model': account.provider_id.model_name,
            'prompt': prompt,
            'max_tokens_to_sample': kwargs.get('max_tokens', account.provider_id.max_tokens),
            'temperature': kwargs.get('temperature', account.provider_id.temperature),
        }
        
        try:
            response = requests.post(
                account.provider_id.api_endpoint,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'content': result['completion'],
                'usage': result.get('usage', {}),
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _convert_to_anthropic_format(self, messages):
        """Convert messages to Anthropic's expected format"""
        prompt = ""
        for message in messages:
            role = message['role']
            content = message['content']
            
            if role == 'system':
                prompt += f"\n\nHuman: System instruction: {content}"
            elif role == 'user':
                prompt += f"\n\nHuman: {content}"
            elif role == 'assistant':
                prompt += f"\n\nAssistant: {content}"
        
        prompt += "\n\nAssistant:"
        return prompt.strip()
