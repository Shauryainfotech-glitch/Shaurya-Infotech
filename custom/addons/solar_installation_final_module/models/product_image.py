from odoo import models, fields
class ProductImage(models.Model):
    _name = "solar.product.image"
    _description = "Product Images"

    product_id = fields.Many2one(
        comodel_name="solar.product.product",
        string="Product",
        required=True,
    )
    image = fields.Binary(string="Image", attachment=True)
    name = fields.Char(string="Image Name")
