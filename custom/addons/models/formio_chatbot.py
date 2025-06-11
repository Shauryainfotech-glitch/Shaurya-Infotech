from odoo import models, fields, api
import requests
import json
from datetime import datetime

class FormioChatMessage(models.Model):
    _name = 'formio.chat.message'
    _description = 'Form.io Chat Messages'
    _order = 'create_date asc'

    form_id = fields.Many2one('formio.builder', string='Form', required=True)
    message = fields.Text(string='Message', required=True)
    sender = fields.Selection([
        ('user', 'User'),
        ('bot', 'Bot')
    ], string='Sender', required=True)
    create_date = fields.Datetime(string='Created on', readonly=True)

class FormioBuilder(models.Model):
    _inherit = 'formio.builder'

    chat_message_ids = fields.One2many('formio.chat.message', 'form_id', string='Chat Messages')
    enable_ai_chat = fields.Boolean(string='Enable AI Chat', default=True)
    ai_model = fields.Selection([
        ('gpt-3.5-turbo', 'GPT-3.5'),
        ('gpt-4', 'GPT-4')
    ], string='AI Model', default='gpt-3.5-turbo')
    ai_api_key = fields.Char(string='AI API Key')
    chat_prompt = fields.Text(string='Chat System Prompt', 
        default="You are a helpful assistant that helps users with their form-related questions.")

    def action_open_chatbot(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'formio_chatbot',
            'target': 'new',
            'params': {
                'form_id': self.id,
            }
        }

    def process_chat_message(self, message):
        self.ensure_one()
        
        # Save user message
        self.env['formio.chat.message'].create({
            'form_id': self.id,
            'message': message,
            'sender': 'user'
        })

        if not self.enable_ai_chat:
            response = "AI chat is currently disabled. Please enable it in the form settings."
        else:
            try:
                # Get chat history for context
                history = self.chat_message_ids.mapped(lambda m: {
                    'role': 'assistant' if m.sender == 'bot' else 'user',
                    'content': m.message
                })

                # Prepare the API call
                headers = {
                    'Authorization': f'Bearer {self.ai_api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': self.ai_model,
                    'messages': [
                        {'role': 'system', 'content': self.chat_prompt},
                        *history[-5:],  # Last 5 messages for context
                        {'role': 'user', 'content': message}
                    ]
                }

                # Make API call
                api_response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data
                )
                
                if api_response.status_code == 200:
                    response = api_response.json()['choices'][0]['message']['content']
                else:
                    response = f"Error: Unable to get response from AI. Status code: {api_response.status_code}"
            
            except Exception as e:
                response = f"Error processing message: {str(e)}"

        # Save bot response
        self.env['formio.chat.message'].create({
            'form_id': self.id,
            'message': response,
            'sender': 'bot'
        })

        return {'message': response} 