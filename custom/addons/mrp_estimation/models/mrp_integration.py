from odoo import models, fields, api


class MrpIntegration(models.Model):
    _name = 'mrp.mrp.integration'
    _description = 'Manufacturing Integration for Estimations'

    estimation_id = fields.Many2one('mrp.estimation', string="Estimation", required=True)
    manufacturing_order_id = fields.Many2one('mrp.production', string="Manufacturing Order")

    @api.model
    def create_manufacturing_order(self, estimation):
        manufacturing_order_vals = {
            'product_id': estimation.product_id.id,
            'product_qty': estimation.quantity,
            'bom_id': estimation.bom_id.id,  # Bill of Materials
            'partner_id': estimation.partner_id.id,
        }
        manufacturing_order = self.env['mrp.production'].create(manufacturing_order_vals)
        return manufacturing_order
