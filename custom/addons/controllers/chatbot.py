from odoo import http
from odoo.http import request
import json

class FormioChatbotController(http.Controller):
    @http.route('/formio/chatbot/history/<int:form_id>', type='http', auth='user')
    def get_chat_history(self, form_id):
        """Get chat history for a specific form."""
        messages = request.env['formio.chat.message'].sudo().search([
            ('form_id', '=', form_id)
        ], order='create_date asc')
        
        return json.dumps({
            'status': 'success',
            'messages': [{
                'id': msg.id,
                'message': msg.message,
                'sender': msg.sender,
                'timestamp': msg.create_date.strftime('%Y-%m-%d %H:%M:%S')
            } for msg in messages]
        })

    @http.route('/formio/chatbot/message', type='json', auth='user')
    def process_message(self, form_id, message):
        """Process a new chat message."""
        try:
            form = request.env['formio.builder'].sudo().browse(form_id)
            if not form.exists():
                return {'status': 'error', 'message': 'Form not found'}

            response = form.process_chat_message(message)
            return {'status': 'success', 'message': response.get('message', 'No response')}
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @http.route('/formio/chatbot/settings/<int:form_id>', type='http', auth='user')
    def get_chatbot_settings(self, form_id):
        """Get chatbot settings for a specific form."""
        form = request.env['formio.builder'].sudo().browse(form_id)
        if not form.exists():
            return json.dumps({'status': 'error', 'message': 'Form not found'})

        return json.dumps({
            'status': 'success',
            'settings': {
                'enable_ai_chat': form.enable_ai_chat,
                'ai_model': form.ai_model if form.enable_ai_chat else None,
                'chat_prompt': form.chat_prompt if form.enable_ai_chat else None
            }
        }) 