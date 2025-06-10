from odoo import models, fields, api

class EstimationReportWizard(models.TransientModel):
    _name = 'mrp.estimation.report.wizard'

    estimation_id = fields.Many2one('mrp.estimation', string='Estimation')

    def generate_report(self):
        return self.env.ref('mrp_estimation.action_report_estimation').report_action(self)
