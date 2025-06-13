# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json


class ArchitectAIAssistant(models.Model):
    _name = 'architect.ai.assistant'
    _inherit = ['mail.thread']
    _description = 'AI Assistant for Architectural Projects'

    name = fields.Char(string='Session Name', required=True)
    project_id = fields.Many2one('architect.project', string='Project')
    user_id = fields.Many2one('res.users', string='User',
                              default=lambda self: self.env.user, required=True)

    # AI Session Details
    session_type = fields.Selection([
        ('design_assistance', 'Design Assistance'),
        ('code_compliance', 'Code Compliance Check'),
        ('cost_estimation', 'Cost Estimation'),
        ('sustainability', 'Sustainability Analysis'),
        ('risk_assessment', 'Risk Assessment'),
        ('material_selection', 'Material Selection'),
        ('general', 'General Consultation')
    ], string='Session Type', required=True, default='general')

    # Conversation
    conversation_ids = fields.One2many('architect.ai.conversation', 'session_id',
                                       string='Conversation History')
    temp_message = fields.Text(string='Temporary Message')
    # Context Information
    context_data = fields.Text(string='Context Data (JSON)')
    project_context = fields.Html(string='Project Context')

    # AI Configuration
    ai_model = fields.Selection([
        ('gpt4', 'GPT-4'),
        ('claude', 'Claude'),
        ('gemini', 'Gemini'),
        ('custom', 'Custom Model')
    ], string='AI Model', default='gpt4')

    temperature = fields.Float(string='Temperature', default=0.7,
                               help="Controls randomness in AI responses")
    max_tokens = fields.Integer(string='Max Tokens', default=2000)

    # Status
    active = fields.Boolean(string='Active Session', default=True)
    last_activity = fields.Datetime(string='Last Activity', default=fields.Datetime.now)

    # Analytics
    total_queries = fields.Integer(string='Total Queries', compute='_compute_analytics')
    avg_response_time = fields.Float(string='Avg Response Time (s)', compute='_compute_analytics')
    satisfaction_rating = fields.Float(string='Satisfaction Rating')

    @api.depends('conversation_ids')
    def _compute_analytics(self):
        for session in self:
            session.total_queries = len(session.conversation_ids.filtered(lambda c: c.message_type == 'user'))
            if session.conversation_ids:
                response_times = session.conversation_ids.mapped('response_time')
                session.avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            else:
                session.avg_response_time = 0

    def send_message(self, message, message_type='user'):
        """Send a message to AI and get response"""
        self.ensure_one()

        # Create user message
        user_msg = self.env['architect.ai.conversation'].create({
            'session_id': self.id,
            'message': message,
            'message_type': message_type,
            'timestamp': fields.Datetime.now()
        })

        # Generate AI response (placeholder - integrate with actual AI service)
        ai_response = self._generate_ai_response(message)

        # Create AI response message
        ai_msg = self.env['architect.ai.conversation'].create({
            'session_id': self.id,
            'message': ai_response,
            'message_type': 'assistant',
            'timestamp': fields.Datetime.now(),
            'response_time': 2.5  # Placeholder response time
        })

        self.last_activity = fields.Datetime.now()
        return ai_msg

    def action_send_message(self):
        """Action to send a message from the form view"""
        # This method would be called from a button, but since we don't have
        # a temp_message field defined in the view, we'll skip this implementation
        # In a real implementation, you'd add a temp field to store the message
        pass

    def _generate_ai_response(self, user_message):
        """Generate AI response based on user message and context"""
        # This is a placeholder - integrate with actual AI service
        context = self._prepare_context()

        # Sample responses based on session type
        responses = {
            'design_assistance': "Based on your project requirements, I recommend considering sustainable materials and energy-efficient design principles. Would you like me to elaborate on specific aspects?",
            'code_compliance': "I've reviewed the relevant building codes for your location. Here are the key compliance requirements you should consider...",
            'cost_estimation': "Based on current market rates and your project specifications, here's a preliminary cost breakdown...",
            'sustainability': "For improved sustainability, consider these eco-friendly alternatives and energy-efficient solutions...",
            'risk_assessment': "I've identified several potential risks in your project. Here's my analysis and recommended mitigation strategies...",
            'material_selection': "For your project type and location, I recommend these materials based on durability, cost, and sustainability factors...",
            'general': f"I understand you're asking about: {user_message}. Let me provide you with relevant architectural insights..."
        }

        return responses.get(self.session_type, responses['general'])

    def _prepare_context(self):
        """Prepare context data for AI processing"""
        context = {}

        if self.project_id:
            context.update({
                'project_name': self.project_id.name,
                'project_type': self.project_id.project_type,
                'location': self.project_id.location,
                'budget': self.project_id.budget,
                'client_type': self.project_id.client_type
            })

        if self.context_data:
            try:
                additional_context = json.loads(self.context_data)
                context.update(additional_context)
            except:
                pass

        return context


    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_ids.unlink()
        self.message_post(body=_("Conversation history cleared."))

    def export_conversation(self):
        """Export conversation to text file"""
        content = []
        for msg in self.conversation_ids.sorted('timestamp'):
            timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            role = 'User' if msg.message_type == 'user' else 'AI Assistant'
            content.append(f"[{timestamp}] {role}: {msg.message}\n")

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/architect.ai.assistant/{self.id}/export_conversation',
            'target': 'new'
        }


class ArchitectAIConversation(models.Model):
    _name = 'architect.ai.conversation'
    _description = 'AI Conversation Message'
    _order = 'timestamp asc'

    session_id = fields.Many2one('architect.ai.assistant', string='Session',
                                 required=True, ondelete='cascade')
    message = fields.Text(string='Message', required=True)
    message_type = fields.Selection([
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
        ('system', 'System')
    ], string='Message Type', required=True)

    timestamp = fields.Datetime(string='Timestamp', required=True)
    response_time = fields.Float(string='Response Time (seconds)')

    # Message Metadata
    tokens_used = fields.Integer(string='Tokens Used')
    confidence_score = fields.Float(string='Confidence Score')

    # User Feedback
    helpful = fields.Boolean(string='Helpful Response')
    rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='Rating')
    feedback = fields.Text(string='Feedback')


class ArchitectAITemplate(models.Model):
    _name = 'architect.ai.template'
    _description = 'AI Response Template'

    name = fields.Char(string='Template Name', required=True)
    category = fields.Selection([
        ('design', 'Design Guidelines'),
        ('compliance', 'Compliance Checks'),
        ('estimation', 'Cost Estimation'),
        ('sustainability', 'Sustainability'),
        ('safety', 'Safety Guidelines'),
        ('materials', 'Material Recommendations')
    ], string='Category', required=True)

    prompt_template = fields.Text(string='Prompt Template', required=True)
    response_template = fields.Html(string='Response Template')

    # Context Variables
    variables = fields.Text(string='Template Variables (JSON)',
                            help="JSON object defining template variables")

    # Usage
    usage_count = fields.Integer(string='Usage Count', default=0)
    active = fields.Boolean(string='Active', default=True)

    def use_template(self, context_vars=None):
        """Use template with provided context variables"""
        self.usage_count += 1

        if context_vars and self.variables:
            try:
                template_vars = json.loads(self.variables)
                # Process template with variables
                processed_template = self.prompt_template
                for var, value in context_vars.items():
                    if var in template_vars:
                        processed_template = processed_template.replace(f"{{{var}}}", str(value))
                return processed_template
            except:
                pass

        return self.prompt_template


class ArchitectAIKnowledgeBase(models.Model):
    _name = 'architect.ai.knowledge'
    _description = 'AI Knowledge Base'

    name = fields.Char(string='Knowledge Item', required=True)
    category = fields.Selection([
        ('building_codes', 'Building Codes'),
        ('materials', 'Materials Database'),
        ('best_practices', 'Best Practices'),
        ('case_studies', 'Case Studies'),
        ('regulations', 'Regulations'),
        ('standards', 'Standards')
    ], string='Category', required=True)

    content = fields.Html(string='Content', required=True)
    tags = fields.Char(string='Tags')

    # Metadata
    source = fields.Char(string='Source')
    last_updated = fields.Date(string='Last Updated', default=fields.Date.today)
    verified = fields.Boolean(string='Verified', default=False)

    # Usage Analytics
    access_count = fields.Integer(string='Access Count', default=0)
    relevance_score = fields.Float(string='Relevance Score', default=1.0)

    active = fields.Boolean(string='Active', default=True)

    def mark_accessed(self):
        """Mark knowledge item as accessed"""
        self.access_count += 1