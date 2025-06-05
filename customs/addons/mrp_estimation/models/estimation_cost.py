from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MrpEstimationCost(models.Model):
    _name = 'mrp.estimation.cost'
    _description = 'Manufacturing Estimation Cost'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    estimation_id = fields.Many2one('mrp.estimation', string='Estimation', required=True, ondelete='cascade')
    
    name = fields.Char(string='Description', required=True)
    cost_type = fields.Selection([
        ('operation', 'Operation Cost'),
        ('labor', 'Labor Cost'),
        ('overhead', 'Overhead Cost'),
        ('misc', 'Miscellaneous Cost'),
        ('document', 'Document Cost'),
    ], string='Cost Type', required=True)
    
    # Operation fields
    operation_id = fields.Many2one('mrp.routing.workcenter', string='Operation')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center')
    operation_time = fields.Float(string='Time (Hours)', default=0.0)
    hourly_rate = fields.Monetary(string='Hourly Rate', currency_field='currency_id')
    
    # Labor fields
    labor_hours = fields.Float(string='Labor Hours', default=0.0)
    labor_rate = fields.Monetary(string='Labor Rate', currency_field='currency_id')
    labor_overhead = fields.Float(string='Labor Overhead (%)', default=0.0)
    
    # Cost fields
    unit_cost = fields.Monetary(string='Unit Cost', currency_field='currency_id')
    quantity = fields.Float(string='Quantity', default=1.0)
    
    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_total_cost',
        store=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        related='estimation_id.currency_id',
        store=True,
        readonly=True
    )
    
    notes = fields.Text(string='Notes')

    @api.depends('cost_type', 'operation_time', 'hourly_rate', 'labor_hours', 
                 'labor_rate', 'labor_overhead', 'unit_cost', 'quantity')
    def _compute_total_cost(self):
        for cost in self:
            if cost.cost_type == 'operation':
                cost.total_cost = cost.operation_time * cost.hourly_rate
            elif cost.cost_type == 'labor':
                base_cost = cost.labor_hours * cost.labor_rate
                overhead_cost = base_cost * (cost.labor_overhead / 100)
                cost.total_cost = base_cost + overhead_cost
            else:
                cost.total_cost = cost.unit_cost * cost.quantity

    @api.onchange('operation_id')
    def _onchange_operation_id(self):
        if self.operation_id:
            self.workcenter_id = self.operation_id.workcenter_id
            self.hourly_rate = self.operation_id.workcenter_id.costs_hour

    @api.onchange('cost_type')
    def _onchange_cost_type(self):
        # Reset fields based on cost type
        if self.cost_type == 'operation':
            self.labor_hours = 0.0
            self.labor_rate = 0.0
            self.labor_overhead = 0.0
            self.unit_cost = 0.0
            self.quantity = 1.0
        elif self.cost_type == 'labor':
            self.operation_id = False
            self.workcenter_id = False
            self.operation_time = 0.0
            self.hourly_rate = 0.0
            self.unit_cost = 0.0
            self.quantity = 1.0
        else:
            self.operation_id = False
            self.workcenter_id = False
            self.operation_time = 0.0
            self.hourly_rate = 0.0
            self.labor_hours = 0.0
            self.labor_rate = 0.0
            self.labor_overhead = 0.0

    @api.constrains('labor_overhead')
    def _check_labor_overhead(self):
        for record in self:
            if record.labor_overhead < 0 or record.labor_overhead > 100:
                raise ValidationError(_("Labor overhead percentage must be between 0 and 100."))

    @api.constrains('operation_time', 'labor_hours', 'quantity')
    def _check_positive_values(self):
        for record in self:
            if record.operation_time < 0:
                raise ValidationError(_("Operation time cannot be negative."))
            if record.labor_hours < 0:
                raise ValidationError(_("Labor hours cannot be negative."))
            if record.quantity < 0:
                raise ValidationError(_("Quantity cannot be negative."))
