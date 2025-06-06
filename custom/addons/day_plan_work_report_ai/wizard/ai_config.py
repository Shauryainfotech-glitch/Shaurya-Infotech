# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AIConfigWizard(models.TransientModel):
    _name = 'ai.config.wizard'
    _description = 'AI Configuration Wizard'
    
    api_key = fields.Char(string='API Key', required=True)
    model_name = fields.Selection([
        ('gpt-4', 'GPT-4'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
    ], string='AI Model', default='gpt-3.5-turbo', required=True)
    temperature = fields.Float(string='Temperature', default=0.7, help="Controls randomness in the AI's output.")
    max_tokens = fields.Integer(string='Max Tokens', default=1000, help="Maximum number of tokens to generate.")
    
    def action_save_config(self):
        self.ensure_one()
        # Save the configuration to the company settings
        company = self.env.company
        company.write({
            'ai_api_key': self.api_key,
            'ai_model_name': self.model_name,
            'ai_temperature': self.temperature,
            'ai_max_tokens': self.max_tokens,
        })
        return {'type': 'ir.actions.act_window_close'}
