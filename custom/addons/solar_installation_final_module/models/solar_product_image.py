from odoo import models, fields, api

class SolarProductImage(models.Model):
    _name = 'solar.product.image'
    _description = 'Images for Solar Products'

    product_id = fields.Many2one('solar.product.product', string="Product", required=True, ondelete='cascade')
    image = fields.Binary(string="Image", attachment=True)
    description = fields.Char(string="Description")
