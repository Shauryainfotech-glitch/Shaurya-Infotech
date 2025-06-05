from odoo import models, fields, api
from odoo.exceptions import UserError
import json

class AiContentGenerator(models.TransientModel):
    _name = 'ai.content.generator'
    _description = 'AI Content Generator'
    
    # Context fields
    model_name = fields.Char(string='Model', readonly=True)
    res_id = fields.Integer(string='Record ID', readonly=True)
    context_data = fields.Text(string='Context Data')
    
    # Input fields
    prompt_type = fields.Selection([
        ('summary', 'Generate Summary'),
        ('email', 'Draft Email'),
        ('description', 'Write Description'),
        ('analysis', 'Analyze Data'),
        ('custom', 'Custom Prompt'),
    ], string='Request Type', default='custom', required=True)
    
    custom_prompt = fields.Text(
        string='Your Request',
        help='What would you like AI to help you with?'
    )
    
    # Configuration
    account_id = fields.Many2one(
        'ai.llm.account',
        string='AI Account',
        compute='_compute_account_id',
        store=True,
        readonly=False
    )
    
    max_tokens = fields.Integer(
        string='Max Response Length',
        default=1000
    )
    
    # Output
    ai_response = fields.Text(
        string='AI Response',
        readonly=True
    )
    
    @api.depends('model_name')
    def _compute_account_id(self):
        for wizard in self:
            wizard.account_id = self.env['ai.llm.account'].get_available_account()
    
    def action_generate(self):
        """Generate content using AI"""
        self.ensure_one()
        
        # Prepare context
        context = self._prepare_context()
        
        # Build messages
        messages = self._build_messages(context)
        
        # Send request
        client = self.env['ai.llm.client']
        response = client.send_request(
            self.account_id.id,
            messages,
            max_tokens=self.max_tokens
        )
        
        if response['success']:
            self.ai_response = response['content']
            
            # Create conversation record
            self._create_conversation(messages, response)
            
            # Return action to show response
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
        else:
            raise UserError(f"AI Error: {response.get('error', 'Unknown error')}")
    
    def _prepare_context(self):
        """Prepare context for AI request"""
        context = {}
        
        if self.context_data:
            context = json.loads(self.context_data)
        
        if self.model_name and self.res_id:
            record = self.env[self.model_name].browse(self.res_id)
            if record.exists():
                context['record_data'] = self._extract_record_data(record)
        
        return context
    
    def _extract_record_data(self, record):
        """Extract relevant data from record"""
        # Basic implementation - override for specific models
        data = {
            'model': record._name,
            'id': record.id,
        }
        
        # Add common fields if they exist
        for field in ['name', 'display_name', 'reference', 'state']:
            if hasattr(record, field):
                data[field] = getattr(record, field)
        
        return data
    
    def _build_messages(self, context):
        """Build messages for AI request"""
        system_prompt = self._get_system_prompt(context)
        user_prompt = self._get_user_prompt(context)
        
        return [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    
    def _get_system_prompt(self, context):
        """Get system prompt based on type"""
        prompts = {
            'summary': "You are a helpful assistant that creates concise summaries of business data.",
            'email': "You are a professional email writer. Write clear, polite business emails.",
            'description': "You are a content writer. Create engaging and informative descriptions.",
            'analysis': "You are a data analyst. Provide insights and recommendations based on the data.",
            'custom': "You are a helpful AI assistant integrated with Odoo ERP system.",
        }
        
        base_prompt = prompts.get(self.prompt_type, prompts['custom'])
        
        if context:
            base_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
        
        return base_prompt
    
    def _get_user_prompt(self, context):
        """Get user prompt"""
        if self.prompt_type == 'custom':
            return self.custom_prompt
        
        # Build automatic prompts based on type
        if self.prompt_type == 'summary':
            return f"Please summarize the following data: {json.dumps(context.get('record_data', {}))}"
        
        # Add more prompt templates as needed
        return self.custom_prompt or "Please provide assistance."
    
    def _create_conversation(self, messages, response):
        """Create conversation record"""
        conversation = self.env['ai.llm.conversation'].create({
            'account_id': self.account_id.id,
            'model_name': self.model_name,
            'res_id': self.res_id,
            'context_data': self.context_data,
        })
        
        # Create message records
        for msg in messages:
            self.env['ai.llm.message'].create({
                'conversation_id': conversation.id,
                'role': msg['role'],
                'content': msg['content'],
            })
        
        # Add AI response
        self.env['ai.llm.message'].create({
            'conversation_id': conversation.id,
            'role': 'assistant',
            'content': response['content'],
            'token_count': response.get('usage', {}).get('total_tokens', 0),
        })
    
    def action_apply_response(self):
        """Apply AI response to source record"""
        self.ensure_one()
        
        if not self.model_name or not self.res_id:
            return {'type': 'ir.actions.act_window_close'}
        
        # Implementation depends on model and prompt type
        # This is a placeholder for specific implementations
        
        return {'type': 'ir.actions.act_window_close'}
