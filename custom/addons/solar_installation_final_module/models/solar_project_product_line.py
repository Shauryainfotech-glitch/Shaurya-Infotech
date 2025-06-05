# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SolarProjectProductLine(models.Model):
    _name = "solar.project.product.line"
    _description = "Project BOM / Product Line"

    project_id = fields.Many2one(
        comodel_name="solar.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True
    )
    sequence = fields.Integer(string="Sequence")
    product_id = fields.Many2one(
        comodel_name="solar.product.product",
        string="Product",
        required=True,
        domain="[('active', '=', True)]"
    )
    product_description = fields.Text(
        string="Product Description",
        related="product_id.description",
        readonly=True
    )
    quantity = fields.Float(string="Quantity", default=1.0)
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        related="product_id.uom_id",
        readonly=True
    )
    unit_cost = fields.Monetary(
        string="Unit Cost",
        related="product_id.standard_price",
        readonly=True
    )
    manual_unit_cost = fields.Monetary(
        string="Manual Cost Override",
        help="If empty, uses product’s standard_price"
    )
    subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related="project_id.currency_id",
        readonly=True
    )

    @api.depends('quantity', 'unit_cost', 'manual_unit_cost')
    def _compute_subtotal(self):
        for rec in self:
            cost = rec.manual_unit_cost if rec.manual_unit_cost else rec.unit_cost
            rec.subtotal = rec.quantity * cost
