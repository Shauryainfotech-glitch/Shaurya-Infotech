from odoo import models, fields, api


class AIPromptTemplate(models.Model):
    _name = "ai.prompt.template"
    _description = "AI Prompt Template"

    name = fields.Char(string="Template Name", required=True)
    analysis_type = fields.Selection([
        ('daily', 'Daily Plan'),
        ('work_report', 'Work Report'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Review'),
        ('trend', 'Trend Analysis')
    ], string="Analysis Type", required=True)

    template = fields.Text(string="Prompt Template", required=True)
    description = fields.Text(string="Description")
    is_default = fields.Boolean(string="Is Default Template")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def get_default_template(self, analysis_type):
        """Get default template for analysis type"""
        template = self.search([
            ('analysis_type', '=', analysis_type),
            ('is_default', '=', True),
            ('active', '=', True)
        ], limit=1)
        return template.template if template else ""