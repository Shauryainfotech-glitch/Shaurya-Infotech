# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SolarProduct(models.Model):
    _name = "solar.product.product"
    _description = "Solar Product (Panel, Inverter, Battery, etc.)"
    _inherit = ['mail.thread']

    name = fields.Char(
        string="Product Name",
        required=True,
        tracking=True
    )
    product_code = fields.Char(
        string="Internal Product Code",
        help="Unique code or SKU",
        required=True,
        tracking=True
    )
    product_type = fields.Selection(
        selection=[
            ('panel', 'Solar Panel'),
            ('inverter', 'Inverter'),
            ('battery', 'Battery'),
            ('mounting', 'Mounting Structure'),
            ('accessory', 'Accessory'),
        ],
        string="Product Category",
        required=True,
        default='panel',
        tracking=True
    )
    brand = fields.Char(string="Brand/Manufacturer")
    model_number = fields.Char(string="Model Number")
    description = fields.Text(string="Description")

    # Technical Specifications
    capacity_watt = fields.Float(
        string="Capacity (Watt)",
        help="For panels/inverters: power output or rating"
    )
    voltage = fields.Float(string="Voltage (V)", help="Nominal voltage")
    current = fields.Float(string="Current (A)", help="Nominal current")
    efficiency_pct = fields.Float(string="Efficiency (%)")
    battery_type = fields.Selection(
        selection=[
            ('li_ion', 'Li-Ion'),
            ('lead_acid', 'Lead Acid'),
            ('gel', 'GEL'),
            ('flooded', 'Flooded Lead-Acid')
        ],
        string="Battery Chemistry",
        help="Applicable if product_type = 'battery'"
    )

    # Weight & Dimensions
    weight_kg = fields.Float(string="Weight (kg)")
    dimension_length_mm = fields.Float(string="Length (mm)")
    dimension_width_mm = fields.Float(string="Width (mm)")
    dimension_height_mm = fields.Float(string="Height (mm)")

    # Inventory & Pricing
    list_price = fields.Monetary(
        string="List Price",
        required=True
    )
    standard_price = fields.Monetary(
        string="Cost Price",
        help="Internal cost or procurement price"
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        required=True,
        default=lambda self: self.env.ref('uom.product_uom_unit')
    )
    uom_po_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Purchase UoM",
        help="Purchase unit of measure"
    )

    # Stock & Availability
    stock_quantity = fields.Float(
        string="On Hand Quantity",
        compute="_compute_stock_quantity",
        store=True
    )
    incoming_qty = fields.Float(
        string="Incoming Quantity",
        compute="_compute_stock_quantity",
        store=True
    )
    outgoing_qty = fields.Float(
        string="Outgoing Quantity",
        compute="_compute_stock_quantity",
        store=True
    )

    # Relationships
    quote_line_ids = fields.One2many(
        comodel_name="solar.quote.line",
        inverse_name="product_id",
        string="Used in Quote Lines",
        readonly=True
    )
    project_line_ids = fields.One2many(
        comodel_name="solar.project.product.line",
        inverse_name="product_id",
        string="Used in Project BOM Lines",
        readonly=True
    )

    active = fields.Boolean(string="Active", default=True)

    @api.depends()  # Removed invalid 'stock_move_ids', 'stock_quant_ids'
    def _compute_stock_quantity(self):
        for rec in self:
            # On-hand quantity
            quants = self.env['stock.quant'].search([('product_id', '=', rec.id)])
            rec.stock_quantity = sum(quants.mapped('quantity'))

            # Incoming: moves with destination in internal locations
            move_in = self.env['stock.move'].search([
                ('product_id', '=', rec.id),
                ('state', 'in', ['confirmed', 'assigned']),
                ('location_dest_id.usage', '=', 'internal')
            ])
            rec.incoming_qty = sum(move_in.mapped('product_uom_qty'))

            # Outgoing: moves from internal to customer
            move_out = self.env['stock.move'].search([
                ('product_id', '=', rec.id),
                ('state', 'in', ['confirmed', 'assigned']),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '=', 'customer')
            ])
            rec.outgoing_qty = sum(move_out.mapped('product_uom_qty'))
