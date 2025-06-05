from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpCosting(models.Model):
    _name = 'mrp.costing'
    _description = 'Manufacturing Costing Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Costing Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    
    mo_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        required=True,
        tracking=True
    )
    
    product_id = fields.Many2one(
        related='mo_id.product_id',
        string='Product',
        store=True,
        readonly=True
    )
    
    estimation_id = fields.Many2one(
        'mrp.estimation',
        string='Related Estimation',
        tracking=True
    )
    
    planned_cost = fields.Monetary(
        string='Planned Cost',
        currency_field='currency_id',
        tracking=True
    )
    
    actual_cost = fields.Monetary(
        string='Actual Cost',
        compute='_compute_actual_costs',
        store=True,
        currency_field='currency_id'
    )
    
    cost_variance = fields.Monetary(
        string='Cost Variance',
        compute='_compute_variances',
        store=True,
        currency_field='currency_id'
    )
    
    cost_variance_percentage = fields.Float(
        string='Variance %',
        compute='_compute_variances',
        store=True
    )
    
    # Cost breakdown
    raw_material_cost = fields.Monetary(string='Raw Material Cost', currency_field='currency_id')
    labor_cost_actual = fields.Monetary(string='Actual Labor Cost', currency_field='currency_id')
    overhead_cost = fields.Monetary(string='Overhead Cost', currency_field='currency_id')
    machine_cost = fields.Monetary(string='Machine Cost', currency_field='currency_id')
    quality_cost = fields.Monetary(string='Quality Control Cost', currency_field='currency_id')
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('mrp.costing') or _('New')
        return super().create(vals_list)

    @api.depends('raw_material_cost', 'labor_cost_actual', 'overhead_cost', 'machine_cost', 'quality_cost')
    def _compute_actual_costs(self):
        for record in self:
            record.actual_cost = (
                record.raw_material_cost + 
                record.labor_cost_actual + 
                record.overhead_cost + 
                record.machine_cost + 
                record.quality_cost
            )

    @api.depends('planned_cost', 'actual_cost')
    def _compute_variances(self):
        for record in self:
            record.cost_variance = record.actual_cost - record.planned_cost
            if record.planned_cost:
                record.cost_variance_percentage = (record.cost_variance / record.planned_cost) * 100
            else:
                record.cost_variance_percentage = 0.0
