from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SolarQuoteLine(models.Model):
    _name = "solar.quote.line"
    _description = "Solar Quote Line"
    _order = "sequence, id"

    quote_id = fields.Many2one(
        comodel_name="solar.quote",
        string="Quotation Reference",
        required=True,
        ondelete="cascade"
    )
    sequence = fields.Integer(string="Sequence", default=10)
    product_id = fields.Many2one(
        comodel_name="solar.product.product",
        string="Product",
        required=True,
        domain="[('active', '=', True)]"
    )
    description = fields.Char(string="Description", required=True)  # Add the description field here
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
        digits='Product Unit of Measure'
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        related="product_id.uom_id",
        readonly=True,
        store=True
    )
    unit_price = fields.Monetary(
        string="Unit Price",
        required=True
    )
    discount_pct = fields.Float(
        string="Discount (%)",
        default=0.0,
        help="Line-level discount"
    )
    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_price_subtotal",
        store=True
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related="quote_id.currency_id",
        readonly=True
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0!")

    @api.constrains('discount_pct')
    def _check_discount(self):
        for line in self:
            if line.discount_pct < 0 or line.discount_pct > 100:
                raise ValidationError("Discount percentage must be between 0 and 100!")

    @api.constrains('unit_price')
    def _check_unit_price(self):
        for line in self:
            if line.unit_price < 0:
                raise ValidationError("Unit price cannot be negative!")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Update fields when product changes"""
        if self.product_id:
            self.name = self.product_id.name
            self.unit_price = self.product_id.list_price
            if self.product_id.description:
                self.name = f"{self.product_id.name} - {self.product_id.description}"

    @api.depends('quantity', 'unit_price', 'discount_pct')
    def _compute_price_subtotal(self):
        for line in self:
            price = line.quantity * line.unit_price
            discount = price * (line.discount_pct / 100.0)
            line.price_subtotal = price - discount
