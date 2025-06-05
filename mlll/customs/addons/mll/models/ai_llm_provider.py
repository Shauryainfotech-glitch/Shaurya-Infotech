from odoo import models, fields, api

class AiLlmProvider(models.Model):
    _name = 'ai.llm.provider'
    _description = 'AI LLM Provider'
    _order = 'sequence, name'
    
    name = fields.Char(string='Provider Name', required=True)
    code = fields.Selection([
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google AI'),
        ('custom', 'Custom Provider'),
    ], string='Provider Code', required=True)
    
    api_endpoint = fields.Char(string='API Endpoint', required=True)
    model_name = fields.Char(
        string='Model Name', 
        required=True,
        help='e.g., gpt-4, claude-3, etc.'
    )
    
    max_tokens = fields.Integer(
        string='Max Tokens',
        default=4096,
        help='Maximum tokens for response'
    )
    temperature = fields.Float(
        string='Temperature',
        default=0.7,
        help='Controls randomness (0-1)'
    )
    
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Authentication
    auth_type = fields.Selection([
        ('api_key', 'API Key'),
        ('oauth2', 'OAuth 2.0'),
        ('custom', 'Custom Authentication'),
    ], string='Authentication Type', default='api_key', required=True)
    
    @api.model
    def get_default_provider(self):
        """Get the default AI provider"""
        return self.search([('active', '=', True)], limit=1)
