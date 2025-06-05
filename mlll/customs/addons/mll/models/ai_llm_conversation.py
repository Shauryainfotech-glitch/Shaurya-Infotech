from odoo import models, fields, api
import json

class AiLlmConversation(models.Model):
    _name = 'ai.llm.conversation'
    _description = 'AI LLM Conversation'
    _order = 'create_date desc'
    _inherit = ['mail.thread']
    
    name = fields.Char(
        string='Conversation Title',
        compute='_compute_name',
        store=True
    )
    
    account_id = fields.Many2one(
        'ai.llm.account',
        string='AI Account',
        required=True,
        ondelete='cascade'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True
    )
    
    model_name = fields.Char(
        string='Source Model',
        help='The Odoo model this conversation relates to'
    )
    res_id = fields.Integer(
        string='Source Record ID',
        help='The record ID this conversation relates to'
    )
    
    message_ids = fields.One2many(
        'ai.llm.message',
        'conversation_id',
        string='Messages'
    )
    
    total_tokens = fields.Integer(
        string='Total Tokens Used',
        compute='_compute_total_tokens',
        store=True
    )
    
    context_data = fields.Text(
        string='Context Data',
        help='JSON data providing context for the conversation'
    )
    
    @api.depends('message_ids')
    def _compute_name(self):
        for record in self:
            if record.message_ids:
                first_message = record.message_ids[0]
                record.name = first_message.content[:50] + '...'
            else:
                record.name = f"Conversation {record.id}"
    
    @api.depends('message_ids.token_count')
    def _compute_total_tokens(self):
        for record in self:
            record.total_tokens = sum(record.message_ids.mapped('token_count'))
    
    def get_conversation_context(self):
        """Get the full conversation context"""
        self.ensure_one()
        messages = []
        
        # Add context if available
        if self.context_data:
            context = json.loads(self.context_data)
            messages.append({
                'role': 'system',
                'content': context.get('system_prompt', '')
            })
        
        # Add conversation messages
        for msg in self.message_ids:
            messages.append({
                'role': msg.role,
                'content': msg.content
            })
        
        return messages


class AiLlmMessage(models.Model):
    _name = 'ai.llm.message'
    _description = 'AI LLM Message'
    _order = 'create_date'
    
    conversation_id = fields.Many2one(
        'ai.llm.conversation',
        string='Conversation',
        required=True,
        ondelete='cascade'
    )
    
    role = fields.Selection([
        ('system', 'System'),
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ], string='Role', required=True)
    
    content = fields.Text(string='Content', required=True)
    token_count = fields.Integer(string='Token Count', default=0)
    
    metadata = fields.Text(
        string='Metadata',
        help='JSON metadata about the message'
    )
