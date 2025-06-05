from odoo import models, fields, api
import json

class AiLlmMixin(models.AbstractModel):
    _name = 'ai.llm.mixin'
    _description = 'AI LLM Mixin'
    
    ai_conversation_ids = fields.One2many(
        'ai.llm.conversation',
        'res_id',  # Missing relation field
        compute='_compute_ai_conversations',
        string='AI Conversations',
        groups='mll.group_ai_user'
    )
    
    ai_suggestions = fields.Text(
        string='AI Suggestions',
        compute='_compute_ai_suggestions',
        groups='mll.group_ai_user'
    )
    
    def _compute_ai_conversations(self):
        """Compute related AI conversations"""
        Conversation = self.env['ai.llm.conversation']
        for record in self:
            record.ai_conversation_ids = Conversation.search([
                ('model_name', '=', record._name),
                ('res_id', '=', record.id)
            ])
    
    def _compute_ai_suggestions(self):
        """Compute AI suggestions for the record"""
        for record in self:
            record.ai_suggestions = False  # Placeholder
    
    def action_open_ai_assistant(self):
        """Open AI Assistant for this record"""
        self.ensure_one()
        return {
            'name': 'AI Assistant',
            'type': 'ir.actions.act_window',
            'res_model': 'ai.content.generator',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model_name': self._name,
                'default_res_id': self.id,
                'default_context_data': self._get_ai_context()
            }
        }
    
    def _get_ai_context(self):
        """Get context data for AI assistant"""
        # Override in specific models to provide context
        return json.dumps({
            'model': self._name,
            'record_id': self.id,
            'record_name': self.display_name if hasattr(self, 'display_name') else str(self.id)
        })
    
    @api.model
    def ai_analyze_data(self, domain=None, fields_list=None):
        """Analyze model data using AI"""
        # Implementation for data analysis
        pass
