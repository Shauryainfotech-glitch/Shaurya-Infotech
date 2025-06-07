# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AvfAiAssistant(models.Model):
    _name = 'avf.ai.assistant'
    _description = 'AI Assistant for Architectural Design Support'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Query Title', required=True)
    query = fields.Text(string='User Query', required=True)
    response = fields.Html(string='AI Response')

    # Project context
    project_id = fields.Many2one('project.project', string='Related Project', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)

    # Query type
    query_type = fields.Selection([
        ('design', 'Design Assistance'),
        ('compliance', 'Compliance Check'),
        ('estimation', 'Cost Estimation'),
        ('planning', 'Project Planning'),
        ('code', 'Building Code Query'),
        ('material', 'Material Suggestion'),
        ('structural', 'Structural Analysis'),
        ('environmental', 'Environmental Impact'),
        ('general', 'General Query')
    ], string='Query Type', required=True, default='general')

    # Status
    state = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ], string='Status', default='pending', tracking=True)

    # AI Model details
    ai_model = fields.Char(string='AI Model Used')
    processing_time = fields.Float(string='Processing Time (seconds)')
    confidence_score = fields.Float(string='Confidence Score (%)')

    # Attachments and references
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    reference_documents = fields.Text(string='Reference Documents')

    # Feedback
    user_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='User Rating')
    feedback = fields.Text(string='User Feedback')

    # Follow-up
    follow_up_needed = fields.Boolean(string='Follow-up Needed')
    follow_up_notes = fields.Text(string='Follow-up Notes')

    @api.constrains('confidence_score')
    def _check_confidence_score(self):
        for record in self:
            if record.confidence_score and not 0 <= record.confidence_score <= 100:
                raise ValidationError(_('Confidence score must be between 0 and 100.'))

    def action_process_query(self):
        """Process the AI query - placeholder for AI integration"""
        self.state = 'processing'
        # Here you would integrate with actual AI services
        # For now, just mark as completed
        self.state = 'completed'
        self.ai_model = 'GPT-4 (Placeholder)'
        self.processing_time = 2.5
        self.confidence_score = 85.0

    def action_mark_helpful(self):
        """Mark response as helpful"""
        self.user_rating = '4'

    def action_request_follow_up(self):
        """Request follow-up for the query"""
        self.follow_up_needed = True