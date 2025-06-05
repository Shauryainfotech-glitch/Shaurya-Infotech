from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class OmniHRAIController(http.Controller):
    
    @http.route('/omnihr/ai/chat', type='json', auth='user', methods=['POST'])
    def ai_chat(self, **kwargs):
        """Handle AI chat requests"""
        try:
            message = kwargs.get('message', '')
            session_id = kwargs.get('session_id')
            
            if not message:
                return {'error': 'Message is required'}
            
            # Get or create chat session
            chat_session = request.env['hr.ai.chat']
            if session_id:
                session = chat_session.browse(int(session_id))
            else:
                session = chat_session.create({
                    'user_id': request.env.user.id,
                    'session_type': kwargs.get('session_type', 'general_hr'),
                })
            
            # Send message and get response
            result = session.send_message(message)
            
            return {
                'success': True,
                'session_id': session.id,
                'response': result
            }
            
        except Exception as e:
            _logger.error(f"AI Chat error: {str(e)}")
            return {'error': str(e)}
    
    @http.route('/omnihr/ai/dashboard', type='http', auth='user')
    def ai_dashboard(self, **kwargs):
        """Render AI dashboard"""
        return request.render('omnihr_ai_platform.ai_dashboard_template', {
            'user': request.env.user,
        }) 