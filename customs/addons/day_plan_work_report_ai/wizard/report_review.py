# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ReportReviewWizard(models.TransientModel):
    _name = 'day.plan.report.review'
    _description = 'Day Plan Report Review'
    
    report_text = fields.Html(string='Report Content')
    report_data = fields.Text(string='Report Data')
    
    def action_approve_report(self):
        self.ensure_one()
        # Add logic to handle report approval
        return {'type': 'ir.actions.act_window_close'}
    
    def action_reject_report(self):
        self.ensure_one()
        # Add logic to handle report rejection
        return {'type': 'ir.actions.act_window_close'}
