from odoo import models, fields, api

class EstimationAutomation(models.Model):
    _name = 'mrp.estimation.automation'
    _description = 'Automated Actions for Estimations'

    estimation_id = fields.Many2one('mrp.estimation', string="Estimation", required=True)
    action_type = fields.Selection([('approve', 'Approve'), ('reject', 'Reject')], string="Action Type", required=True)

    @api.model
    def automate_estimation_action(self, estimation, action_type):
        if action_type == 'approve':
            estimation.write({'state': 'approved'})
        elif action_type == 'reject':
            estimation.write({'state': 'rejected'})
        return True
