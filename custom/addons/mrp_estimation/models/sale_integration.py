from odoo import models, fields, api

class SaleEstimation(models.Model):
    _inherit = 'sale.order'

    estimation_ids = fields.One2many('mrp.estimation', 'sale_order_id', string='Estimations')
    estimation_count = fields.Integer(compute='_compute_estimation_count')

    @api.depends('estimation_ids')
    def _compute_estimation_count(self):
        for order in self:
            order.estimation_count = len(order.estimation_ids)

    def action_view_estimations(self):
        self.ensure_one()
        return {
            'name': 'Estimations',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.estimation',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        } 