from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class HRAIChat(models.Model):
    _name = 'hr.ai.chat'
    _description = 'HR AI Chat Sessions'
    _rec_name = 'session_name'
    _order = 'create_date desc'
    
    session_name = fields.Char('Session Name', compute='_compute_session_name', store=True)
    user_id = fields.Many2one('res.users', 'User', required=True, default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee', 'Employee', related='user_id.employee_id', store=True)
    
    # Session Details
    session_type = fields.Selection([
        ('general_hr', 'General HR Inquiry'),
        ('policy_question', 'Policy Question'),
        ('benefits_info', 'Benefits Information'),
        ('leave_request', 'Leave Request'),
        ('performance_query', 'Performance Query'),
        ('career_guidance', 'Career Guidance'),
        ('training_info', 'Training Information'),
        ('complaint_report', 'Complaint/Report'),
        ('technical_support', 'Technical Support'),
    ], 'Session Type', default='general_hr')
    
    session_status = fields.Selection([
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ], 'Session Status', default='active')
    
    # AI Configuration
    ai_model_used = fields.Char('AI Model Used')
    conversation_context = fields.Text('Conversation Context')
    session_summary = fields.Text('Session Summary')
    
    # Metrics
    total_messages = fields.Integer('Total Messages', compute='_compute_message_stats')
    user_satisfaction = fields.Selection([
        ('1', 'Very Dissatisfied'),
        ('2', 'Dissatisfied'),
        ('3', 'Neutral'),
        ('4', 'Satisfied'),
        ('5', 'Very Satisfied'),
    ], 'User Satisfaction')
    
    resolution_time = fields.Float('Resolution Time (minutes)', compute='_compute_resolution_time')
    escalation_reason = fields.Text('Escalation Reason')
    
    # Messages
    message_ids = fields.One2many('hr.ai.chat.message', 'chat_session_id', 'Messages')
    
    @api.depends('create_date', 'session_type')
    def _compute_session_name(self):
        for record in self:
            if record.create_date:
                date_str = record.create_date.strftime('%Y-%m-%d %H:%M')
                session_type_label = dict(record._fields['session_type'].selection).get(record.session_type, 'Chat')
                record.session_name = f"{session_type_label} - {date_str}"
            else:
                record.session_name = "New Chat Session"
    
    @api.depends('message_ids')
    def _compute_message_stats(self):
        for record in self:
            record.total_messages = len(record.message_ids)
    
    @api.depends('create_date', 'session_status')
    def _compute_resolution_time(self):
        for record in self:
            if record.session_status in ['resolved', 'closed'] and record.create_date:
                # Find the last message timestamp
                last_message = record.message_ids.sorted('timestamp', reverse=True)[:1]
                if last_message:
                    delta = last_message.timestamp - record.create_date
                    record.resolution_time = delta.total_seconds() / 60  # Convert to minutes
                else:
                    record.resolution_time = 0
            else:
                record.resolution_time = 0
    
    def send_message(self, message_content, message_type='user'):
        """Send a message in the chat session"""
        # Create user message
        user_message = self.env['hr.ai.chat.message'].create({
            'chat_session_id': self.id,
            'message_type': message_type,
            'content': message_content,
            'sender_id': self.user_id.id,
        })
        
        if message_type == 'user':
            # Generate AI response
            ai_response = self._generate_ai_response(message_content)
            
            # Create AI response message
            ai_message = self.env['hr.ai.chat.message'].create({
                'chat_session_id': self.id,
                'message_type': 'ai',
                'content': ai_response['content'],
                'ai_confidence': ai_response.get('confidence', 0),
                'processing_time': ai_response.get('processing_time', 0),
            })
            
            # Update conversation context
            self._update_conversation_context(message_content, ai_response['content'])
            
            return {
                'user_message': user_message.read()[0],
                'ai_message': ai_message.read()[0],
            }
        
        return {'user_message': user_message.read()[0]}
    
    def _generate_ai_response(self, user_message):
        """Generate AI response to user message"""
        try:
            start_time = datetime.now()
            
            # Get AI orchestrator service
            ai_orchestrator = self.env['hr.ai.orchestrator']
            
            # Prepare context for AI
            context = {
                'user_id': self.user_id.id,
                'employee_id': self.employee_id.id if self.employee_id else None,
                'session_type': self.session_type,
                'conversation_history': self._get_conversation_history(),
                'user_profile': self._get_user_profile(),
                'company_policies': self._get_relevant_policies(),
            }
            
            # Generate response using AI
            response = ai_orchestrator.generate_chat_response(
                message=user_message,
                context=context,
                session_type=self.session_type
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Check if escalation is needed
            if response.get('requires_escalation', False):
                self._escalate_session(response.get('escalation_reason', ''))
            
            return {
                'content': response.get('response', 'I apologize, but I encountered an error processing your request.'),
                'confidence': response.get('confidence', 0),
                'processing_time': processing_time,
                'suggested_actions': response.get('suggested_actions', []),
            }
            
        except Exception as e:
            _logger.error(f"AI response generation failed: {str(e)}")
            return {
                'content': 'I apologize, but I encountered an error. Please try again or contact HR support.',
                'confidence': 0,
                'processing_time': 0,
            }
    
    def _get_conversation_history(self):
        """Get conversation history for context"""
        messages = self.message_ids.sorted('timestamp')
        history = []
        
        for message in messages[-10:]:  # Last 10 messages for context
            history.append({
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
            })
        
        return history
    
    def _get_user_profile(self):
        """Get user profile information for personalized responses"""
        profile = {
            'name': self.user_id.name,
            'email': self.user_id.email,
        }
        
        if self.employee_id:
            profile.update({
                'department': self.employee_id.department_id.name if self.employee_id.department_id else '',
                'job_title': self.employee_id.job_title or '',
                'manager': self.employee_id.parent_id.name if self.employee_id.parent_id else '',
                'work_location': self.employee_id.work_location or '',
            })
        
        return profile
    
    def _get_relevant_policies(self):
        """Get relevant company policies for AI context"""
        # This would integrate with a policy management system
        return {
            'leave_policy': 'Standard leave policy information...',
            'remote_work_policy': 'Remote work guidelines...',
            'benefits_overview': 'Employee benefits summary...',
        }
    
    def _update_conversation_context(self, user_message, ai_response):
        """Update conversation context for better AI responses"""
        context = json.loads(self.conversation_context or '{}')
        
        # Add latest exchange
        context['last_exchange'] = {
            'user_message': user_message,
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Update session type if it can be inferred
        inferred_type = self._infer_session_type(user_message)
        if inferred_type and inferred_type != self.session_type:
            context['inferred_type'] = inferred_type
        
        self.conversation_context = json.dumps(context)
    
    def _infer_session_type(self, message):
        """Infer session type from message content"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['leave', 'vacation', 'time off', 'pto']):
            return 'leave_request'
        elif any(word in message_lower for word in ['benefits', 'insurance', 'health', 'dental']):
            return 'benefits_info'
        elif any(word in message_lower for word in ['performance', 'review', 'evaluation', 'goals']):
            return 'performance_query'
        elif any(word in message_lower for word in ['training', 'course', 'learning', 'development']):
            return 'training_info'
        elif any(word in message_lower for word in ['career', 'promotion', 'growth', 'advancement']):
            return 'career_guidance'
        elif any(word in message_lower for word in ['policy', 'rule', 'guideline', 'procedure']):
            return 'policy_question'
        elif any(word in message_lower for word in ['complaint', 'harassment', 'discrimination', 'report']):
            return 'complaint_report'
        
        return None
    
    def _escalate_session(self, reason):
        """Escalate session to human HR representative"""
        self.session_status = 'escalated'
        self.escalation_reason = reason
        
        # Create escalation notification
        self.env['mail.mail'].create({
            'subject': f'HR Chat Escalation - {self.session_name}',
            'body_html': f'''
                <p>Chat session has been escalated to human support.</p>
                <p><strong>User:</strong> {self.user_id.name}</p>
                <p><strong>Session Type:</strong> {self.session_type}</p>
                <p><strong>Reason:</strong> {reason}</p>
                <p><strong>Messages:</strong> {self.total_messages}</p>
                <p><a href="/web#id={self.id}&model=hr.ai.chat">View Chat Session</a></p>
            ''',
            'email_to': 'hr@company.com',  # Configure HR email
        }).send()
    
    def close_session(self):
        """Close the chat session"""
        self.session_status = 'closed'
        
        # Generate session summary
        self._generate_session_summary()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Chat session closed successfully'),
                'type': 'success'
            }
        }
    
    def _generate_session_summary(self):
        """Generate AI-powered session summary"""
        try:
            ai_orchestrator = self.env['hr.ai.orchestrator']
            
            conversation_data = {
                'messages': self._get_conversation_history(),
                'session_type': self.session_type,
                'resolution_status': self.session_status,
                'user_satisfaction': self.user_satisfaction,
            }
            
            summary = ai_orchestrator.generate_session_summary(conversation_data)
            self.session_summary = summary.get('summary', '')
            
        except Exception as e:
            _logger.error(f"Session summary generation failed: {str(e)}")
            self.session_summary = f"Session with {self.total_messages} messages. Type: {self.session_type}"


class HRAIChatMessage(models.Model):
    _name = 'hr.ai.chat.message'
    _description = 'HR AI Chat Messages'
    _rec_name = 'content'
    _order = 'timestamp asc'
    
    chat_session_id = fields.Many2one('hr.ai.chat', 'Chat Session', required=True, ondelete='cascade')
    
    # Message Details
    message_type = fields.Selection([
        ('user', 'User Message'),
        ('ai', 'AI Response'),
        ('system', 'System Message'),
        ('escalation', 'Escalation Message'),
    ], 'Message Type', required=True)
    
    content = fields.Text('Message Content', required=True)
    timestamp = fields.Datetime('Timestamp', default=fields.Datetime.now)
    
    # Sender Information
    sender_id = fields.Many2one('res.users', 'Sender')
    sender_name = fields.Char('Sender Name')
    
    # AI-specific fields
    ai_confidence = fields.Float('AI Confidence Score')
    processing_time = fields.Float('Processing Time (seconds)')
    ai_model_version = fields.Char('AI Model Version')
    
    # Message Metadata
    message_intent = fields.Char('Detected Intent')
    entities_extracted = fields.Text('Extracted Entities')
    sentiment_score = fields.Float('Message Sentiment')
    
    # User Feedback
    user_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent'),
    ], 'User Rating')
    
    feedback_comment = fields.Text('Feedback Comment')
    
    def rate_message(self, rating, comment=None):
        """Rate an AI message"""
        if self.message_type != 'ai':
            raise UserError(_('Only AI messages can be rated'))
        
        self.user_rating = rating
        self.feedback_comment = comment or ''
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Thank you for your feedback!'),
                'type': 'success'
            }
        } 