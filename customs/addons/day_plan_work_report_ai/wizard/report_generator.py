# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json

class ReportGeneratorWizard(models.TransientModel):
    _name = 'day.plan.report.generator'
    _description = 'Day Plan Report Generator'

    date_from = fields.Date(string='From Date', required=True, default=fields.Date.context_today)
    date_to = fields.Date(string='To Date', required=True, default=fields.Date.context_today)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    include_ai_analysis = fields.Boolean(string='Include AI Analysis', default=True)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_("The 'From Date' must be before the 'To Date'."))

    def action_generate_report(self):
        self.ensure_one()
        # Redirect to the controller that will generate the PDF report
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'url': f"{base_url}/day_plan/generate_report?wizard_id={self.id}",
            'target': 'self',
        }
