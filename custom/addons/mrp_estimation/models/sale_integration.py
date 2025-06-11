from odoo import models, fields, api


class SaleIntegration(models.Model):
    _name = 'mrp.sale.integration'
    _description = 'Sales Integration for Estimations'

    estimation_id = fields.Many2one('mrp.estimation', string="Estimation", required=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    @api.model
    def create_sale_order_from_estimation(self, estimation):
        sale_order_vals = {
            'partner_id': estimation.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_cost,
            }) for line in estimation.material_lines]
        }
        sale_order = self.env['sale.order'].create(sale_order_vals)
        return sale_order
