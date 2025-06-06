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

    # Stock Integration
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
        auto_join=True,
        index=True
    )
    default_code = fields.Char(
        string='Internal Reference',
        index=True
    )
    barcode = fields.Char(
        string='Barcode',
        copy=False,
        index=True
    )
    stock_quantity = fields.Float(
        string='Quantity On Hand',
        related='product_tmpl_id.qty_available',
        store=True
    )
    incoming_qty = fields.Float(
        string='Incoming',
        related='product_tmpl_id.incoming_qty',
        store=True
    )
    outgoing_qty = fields.Float(
        string='Outgoing',
        related='product_tmpl_id.outgoing_qty',
        store=True
    )
    virtual_available = fields.Float(
        string='Forecast Quantity',
        related='product_tmpl_id.virtual_available',
        store=True
    )

    # Stock Locations
    location_ids = fields.Many2many(
        'stock.location',
        compute='_compute_location_ids',
        string='Locations',
        help='Locations where this product is stored'
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

    project_id = fields.Many2one(
        comodel_name="solar.project",
        string="Related Project",
        required=True,
        ondelete="cascade",
        tracking=True
    )
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, vals):
        """Create corresponding product.template when creating solar product"""
        if not vals.get('product_tmpl_id'):
            product_vals = {
                'name': vals.get('name'),
                'type': 'product',  # Storable product
                'standard_price': vals.get('standard_price', 0.0),
                'list_price': vals.get('list_price', 0.0),
                'uom_id': vals.get('uom_id'),
                'uom_po_id': vals.get('uom_po_id'),
                'default_code': vals.get('product_code'),
                'barcode': vals.get('barcode'),
            }
            product_tmpl = self.env['product.template'].create(product_vals)
            vals['product_tmpl_id'] = product_tmpl.id
        return super().create(vals)

    @api.depends('product_tmpl_id')
    def _compute_location_ids(self):
        """Compute all stock locations where this product is stored"""
        for record in self:
            quants = self.env['stock.quant'].search([
                ('product_id.product_tmpl_id', '=', record.product_tmpl_id.id),
                ('location_id.usage', '=', 'internal')
            ])
            record.location_ids = quants.mapped('location_id')

    def action_view_stock_moves(self):
        """Smart button action to view stock moves"""
        self.ensure_one()
        action = self.env.ref('stock.stock_move_action').read()[0]
        action['domain'] = [('product_id.product_tmpl_id', '=', self.product_tmpl_id.id)]
        action['context'] = {'search_default_product_id': self.product_tmpl_id.id}
        return action

    def action_update_quantity_on_hand(self):
        """Smart button action to update quantity"""
        self.ensure_one()
        return self.product_tmpl_id.action_update_quantity_on_hand()

    def _sync_product_template(self):
        """Sync changes to product.template"""
        for record in self:
            if record.product_tmpl_id:
                record.product_tmpl_id.write({
                    'name': record.name,
                    'standard_price': record.standard_price,
                    'list_price': record.list_price,
                    'uom_id': record.uom_id.id,
                    'uom_po_id': record.uom_po_id.id,
                    'default_code': record.product_code,
                    'barcode': record.barcode,
                })

    def write(self, vals):
        """Update product.template when solar product is updated"""
        res = super().write(vals)
        if any(field in vals for field in ['name', 'standard_price', 'list_price', 'uom_id', 'uom_po_id', 'product_code', 'barcode']):
            self._sync_product_template()
        return res
