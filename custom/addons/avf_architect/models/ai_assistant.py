# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class AIAssistant(models.Model):
    _name = 'avf.ai.assistant'
    _description = 'AI Assistant for Architectural Projects'
    _rec_name = 'name'

    name = fields.Char(string='Assistant Name', required=True)
    project_id = fields.Many2one('project.project', string='Related Project')
    query = fields.Text(string='Query', required=True)
    response = fields.Text(string='AI Response')
    ai_model = fields.Selection([
        ('gpt', 'GPT Model'),
        ('claude', 'Claude Model'),
        ('local', 'Local Model')
    ], string='AI Model', default='gpt')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ], string='Status', default='draft')
    created_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)
    processed_date = fields.Datetime(string='Processed Date')

class ArchitectAIAssistant(models.Model):
    _name = 'architect.ai.assistant'
    _description = 'AI Assistant for Architectural Projects'
    _order = 'create_date desc'

    name = fields.Char(string='Query Title', required=True)
    query = fields.Text(string='User Query', required=True)
    response = fields.Text(string='AI Response')
    project_id = fields.Many2one('architect.project', string='Related Project')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    # AI Context
    context_type = fields.Selection([
        ('design', 'Design Assistance'),
        ('compliance', 'Compliance Check'),
        ('estimation', 'Cost Estimation'),
        ('dpr', 'DPR Generation'),
        ('general', 'General Query')
    ], string='Context Type', default='general')

    # Status
    state = fields.Selection([
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('error', 'Error')
    ], string='Status', default='pending')

    # Metadata
    processing_time = fields.Float(string='Processing Time (seconds)')
    confidence_score = fields.Float(string='Confidence Score')
    tokens_used = fields.Integer(string='Tokens Used')

    def process_query(self):
        """Process AI query - placeholder for actual AI integration"""
        self.state = 'processed'
        self.response = f"AI response for: {self.query}"
        return True

class ArchitectAIConversation(models.Model):
    _name = 'architect.ai.conversation'
    _description = 'AI Conversation History'
    _order = 'sequence, create_date'

    assistant_id = fields.Many2one('architect.ai.assistant', string='AI Session', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    message_type = fields.Selection([
        ('user', 'User Message'),
        ('ai', 'AI Response')
    ], string='Message Type', required=True)
    content = fields.Html(string='Content', required=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

    # Metadata
    tokens_used = fields.Integer(string='Tokens Used')
    model_version = fields.Char(string='Model Version')

class ArchitectAITemplate(models.Model):
    _name = 'architect.ai.template'
    _description = 'AI Prompt Templates'

    name = fields.Char(string='Template Name', required=True)
    model_type = fields.Selection([
        ('design', 'Design Assistant'),
        ('compliance', 'Compliance Checker'),
        ('estimation', 'Cost Estimation'),
        ('planning', 'Project Planning'),
        ('dpr', 'DPR Generator')
    ], string='Model Type', required=True)

    prompt_template = fields.Text(string='Prompt Template', required=True)
    variables = fields.Text(string='Variables (JSON)')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

class ArchitectAIKnowledge(models.Model):
    _name = 'architect.ai.knowledge'
    _description = 'AI Knowledge Base'

    name = fields.Char(string='Knowledge Item', required=True)
    category = fields.Selection([
        ('building_codes', 'Building Codes'),
        ('design_standards', 'Design Standards'),
        ('compliance_rules', 'Compliance Rules'),
        ('best_practices', 'Best Practices'),
        ('material_specs', 'Material Specifications')
    ], string='Category', required=True)

    content = fields.Html(string='Content', required=True)
    source = fields.Char(string='Source')
    region = fields.Char(string='Applicable Region')
    last_updated = fields.Date(string='Last Updated', default=fields.Date.today)
    active = fields.Boolean(string='Active', default=True)