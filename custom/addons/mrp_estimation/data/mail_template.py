from odoo import models, fields

class MailTemplate(models.Model):
    _inherit = 'mail.template'

    report_template = fields.Many2one('ir.actions.report', string='Report Template')
