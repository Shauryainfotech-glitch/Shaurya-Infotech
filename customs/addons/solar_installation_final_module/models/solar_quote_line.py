# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SolarQuoteLine(models.Model):
    _name = "solar.quote.line"
    _description = "Solar Quote Line"

    quote_id = fields.Many2one(
        comodel_name="solar.quote",
        string="Quotation Reference",
        required=True,
        ondelete="cascade"
    )
    sequence = fields.Integer(string="Sequence")
    product_id = fields.Many2one(
        comodel_name="solar.product.product",
        string="Product",
        required=True,
        domain="[('active', '=', True)]"
    )
    description = fields.Text(
        string="Description",
        compute="_compute_description",
        store=True
    )
    quantity = fields.Float(string="Quantity", default=1.0)
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        related="product_id.uom_id",
        readonly=True,
        store=True
    )
    unit_price = fields.Monetary(
        string="Unit Price",
        related="product_id.list_price",
        readonly=True
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

    @api.depends('product_id')
    def _compute_description(self):
        for line in self:
            line.description = line.product_id.description or ''

    @api.depends('product_id', 'quantity', 'unit_price', 'discount_pct')
    def _compute_price_subtotal(self):
        for line in self:
            price = line.quantity * line.unit_price
            discount = price * (line.discount_pct / 100.0)
            line.price_subtotal = price - discount
