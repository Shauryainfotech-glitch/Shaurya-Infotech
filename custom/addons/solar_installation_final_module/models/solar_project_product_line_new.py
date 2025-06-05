# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SolarProjectProductLine(models.Model):
    _name = "solar.project.product.line"
    _description = "Project BOM / Product Line"
    _order = "sequence, id"

    project_id = fields.Many2one(
        comodel_name="solar.project",
        string="Project",
        required=True,
        ondelete="cascade",
        index=True
    )
    sequence = fields.Integer(string="Sequence", default=10)
    product_id = fields.Many2one(
        comodel_name="solar.product.product",
        string="Product",
        required=True,
        domain="[('active', '=', True)]"
    )
    name = fields.Char(
        string="Description",
        required=True
    )
    quantity = fields.Float(
        string="Quantity", 
        default=1.0,
        digits='Product Unit of Measure'
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        related="product_id.uom_id",
        readonly=True,
        store=True
    )
    unit_cost = fields.Monetary(
        string="Unit Cost",
        related="product_id.standard_price",
        readonly=True
    )
    manual_unit_cost = fields.Monetary(
        string="Manual Cost Override",
        help="If empty, uses product's standard_price"
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

    # Additional tracking fields
    product_type = fields.Selection(
        related="product_id.product_type",
        string="Product Type",
        readonly=True,
        store=True
    )
    capacity_watt = fields.Float(
        related="product_id.capacity_watt",
        string="Capacity (W)",
        readonly=True,
        store=True
    )
    
    # Installation tracking
    installed_quantity = fields.Float(
        string="Installed Quantity",
        default=0.0,
        help="Quantity actually installed"
    )
    remaining_quantity = fields.Float(
        string="Remaining Quantity",
        compute="_compute_remaining_quantity",
        store=True
    )
    installation_status = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partially Installed'),
        ('complete', 'Fully Installed')
    ], string="Installation Status", compute="_compute_installation_status", store=True)

    # Stock availability
    stock_available = fields.Float(
        related="product_id.stock_quantity",
        string="Stock Available",
        readonly=True
    )
    stock_sufficient = fields.Boolean(
        string="Stock Sufficient",
        compute="_compute_stock_sufficient",
        store=True
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0!")

    @api.constrains('installed_quantity')
    def _check_installed_quantity(self):
        for line in self:
            if line.installed_quantity < 0:
                raise ValidationError("Installed quantity cannot be negative!")
            if line.installed_quantity > line.quantity:
                raise ValidationError("Installed quantity cannot exceed planned quantity!")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Update fields when product changes"""
        if self.product_id:
            self.name = self.product_id.name
            if self.product_id.description:
                self.name = f"{self.product_id.name} - {self.product_id.description}"

    @api.depends('quantity', 'unit_cost', 'manual_unit_cost')
    def _compute_subtotal(self):
        for rec in self:
            cost = rec.manual_unit_cost if rec.manual_unit_cost else rec.unit_cost
            rec.subtotal = rec.quantity * cost

    @api.depends('quantity', 'installed_quantity')
    def _compute_remaining_quantity(self):
        for line in self:
            line.remaining_quantity = line.quantity - line.installed_quantity

    @api.depends('quantity', 'installed_quantity')
    def _compute_installation_status(self):
        for line in self:
            if line.installed_quantity == 0:
                line.installation_status = 'pending'
            elif line.installed_quantity < line.quantity:
                line.installation_status = 'partial'
            else:
                line.installation_status = 'complete'

    @api.depends('quantity', 'stock_available')
    def _compute_stock_sufficient(self):
        for line in self:
            line.stock_sufficient = line.stock_available >= line.quantity

    def action_update_installed_quantity(self):
        """Action to update installed quantity"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Installed Quantity',
            'res_model': 'solar.project.product.line',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'form_view_initial_mode': 'edit'}
        }

    def mark_as_installed(self):
        """Mark the entire quantity as installed"""
        for line in self:
            line.installed_quantity = line.quantity

    def reset_installation(self):
        """Reset installation status"""
        for line in self:
            line.installed_quantity = 0.0

    def _prepare_procurement_vals(self):
        """Prepare values for procurement/purchase"""
        self.ensure_one()
        return {
            'product_id': self.product_id.id,
            'product_qty': self.quantity,
            'product_uom': self.uom_id.id,
            'location_id': self.project_id.warehouse_id.lot_stock_id.id if self.project_id.warehouse_id else False,
            'name': f"Project {self.project_id.name} - {self.product_id.name}",
            'origin': self.project_id.name,
            'company_id': self.project_id.company_id.id,
        }
