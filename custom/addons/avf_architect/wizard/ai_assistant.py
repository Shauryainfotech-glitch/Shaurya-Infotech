# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AiAssistantWizard(models.TransientModel):
    _name = 'architect.ai.assistant.wizard'
    _description = 'AI Assistant Wizard'

    project_id = fields.Many2one('architect.project', string='Project', required=True)
    query_type = fields.Selection([
        ('design', 'Design Assistance'),
        ('compliance', 'Compliance Check'),
        ('cost', 'Cost Estimation'),
        ('sustainability', 'Sustainability Analysis')
    ], string='Query Type', required=True)
    user_query = fields.Text(string='Your Question', required=True)
    response = fields.Html(string='AI Response', readonly=True)

    def generate_response(self):
        # This would integrate with an AI service in production
        self.response = f"<p>Here's a sample response for your {self.query_type} query:</p>" + \
                       f"<p>Based on project {self.project_id.name}, I recommend considering...</p>" + \
                       "<ul><li>Sample recommendation 1</li>" + \
                       "<li>Sample recommendation 2</li>" + \
                       "<li>Sample recommendation 3</li></ul>"
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'architect.ai.assistant.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }
