from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpEstimationLine(models.Model):
    _name = 'mrp.estimation.line'
    _description = 'Manufacturing Estimation Line'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    estimation_id = fields.Many2one('mrp.estimation', string='Estimation', required=True, ondelete='cascade')

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('type', 'in', ['product', 'consu'])]
    )

    product_qty = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        digits='Product Unit of Measure'
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True
    )

    product_cost = fields.Monetary(
        string='Unit Cost',
        currency_field='currency_id',
        default=0.0
    )

    subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id'
    )

    existing_material = fields.Boolean(
        string='Material Available',
        default=False,
        help="Check if material is available in stock"
    )

    supplier_id = fields.Many2one(
        'res.partner',
        string='Preferred Supplier',
        domain=[('is_company', '=', True), ('supplier_rank', '>', 0)]
    )

    lead_time = fields.Float(
        string='Lead Time (Days)',
        default=0.0,
        help="Lead time for this material in days"
    )

    markup_percentage = fields.Float(
        string='Markup (%)',
        default=0.0,
        help="Markup percentage for this material"
    )

    marked_up_cost = fields.Monetary(
        string='Cost After Markup',
        compute='_compute_marked_up_cost',
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        related='estimation_id.currency_id',
        store=True,
        readonly=True
    )

    notes = fields.Text(string='Notes')

    # ======================
    # CONSTRAINTS & VALIDATION
    # ======================

    @api.constrains('product_qty')
    def _check_product_qty(self):
        for record in self:
            if record.product_qty <= 0:
                raise ValidationError(_("Product quantity must be greater than zero."))

    @api.constrains('product_cost')
    def _check_product_cost(self):
        for record in self:
            if record.product_cost < 0:
                raise ValidationError(_("Product cost cannot be negative."))

    @api.constrains('markup_percentage')
    def _check_markup_percentage(self):
        for record in self:
            if record.markup_percentage < -100:
                raise ValidationError(_("Markup percentage cannot be less than -100%."))

    @api.constrains('lead_time')
    def _check_lead_time(self):
        for record in self:
            if record.lead_time < 0:
                raise ValidationError(_("Lead time cannot be negative."))

    # ======================
    # COMPUTED METHODS
    # ======================

    @api.depends('product_qty', 'marked_up_cost')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.product_qty * line.marked_up_cost

    @api.depends('product_cost', 'markup_percentage')
    def _compute_marked_up_cost(self):
        for line in self:
            line.marked_up_cost = line.product_cost * (1 + line.markup_percentage / 100)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
            self.product_cost = self.product_id.standard_price

            # Check stock availability
            stock_quant = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id.usage', '=', 'internal')
            ])
            self.existing_material = sum(stock_quant.mapped('quantity')) > 0

            # Get preferred supplier
            supplier_info = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                ('company_id', 'in', [self.env.company.id, False])
            ], order='sequence', limit=1)
            if supplier_info:
                self.supplier_id = supplier_info.partner_id
                self.lead_time = supplier_info.delay
                self.product_cost = supplier_info.price