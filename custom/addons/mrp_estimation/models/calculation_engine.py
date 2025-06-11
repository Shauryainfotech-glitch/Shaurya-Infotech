from odoo import models, fields, api

class EstimationCalculationEngine(models.Model):
    _name = 'mrp.estimation.calculation'
    _description = 'Advanced Estimation Calculation Engine'

    estimation_id = fields.Many2one('mrp.estimation', string="Estimation", required=True)
    material_cost = fields.Float(string="Material Cost", compute="_compute_material_cost")
    labor_cost = fields.Float(string="Labor Cost", compute="_compute_labor_cost")
    overhead_cost = fields.Float(string="Overhead Cost", compute="_compute_overhead_cost")
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost")

    @api.depends('estimation_id')
    def _compute_material_cost(self):
        for record in self:
            record.material_cost = sum(line.unit_cost * line.quantity for line in record.estimation_id.material_lines)

    @api.depends('estimation_id')
    def _compute_labor_cost(self):
        for record in self:
            record.labor_cost = sum(line.labor_cost for line in record.estimation_id.material_lines)

    @api.depends('estimation_id')
    def _compute_overhead_cost(self):
        for record in self:
            record.overhead_cost = sum(line.overhead_cost for line in record.estimation_id.material_lines)

    @api.depends('material_cost', 'labor_cost', 'overhead_cost')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.material_cost + record.labor_cost + record.overhead_cost
