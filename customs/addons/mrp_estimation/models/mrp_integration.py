from odoo import models, fields, api

class MrpEstimation(models.Model):
    _inherit = 'mrp.production'

    estimation_id = fields.Many2one('mrp.estimation', string='Estimation')
    estimated_cost = fields.Float(related='estimation_id.total_cost', string='Estimated Cost')
    cost_variance = fields.Float(compute='_compute_cost_variance', string='Cost Variance')

    @api.depends('estimated_cost', 'total_cost')
    def _compute_cost_variance(self):
        for production in self:
            production.cost_variance = production.total_cost - production.estimated_cost

    def action_view_estimation(self):
        self.ensure_one()
        return {
            'name': 'Estimation',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.estimation',
            'view_mode': 'form',
            'res_id': self.estimation_id.id,
        } 