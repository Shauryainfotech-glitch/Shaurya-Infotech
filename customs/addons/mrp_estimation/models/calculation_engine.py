from odoo import models, api
from odoo.tools import float_round


class EstimationCalculationEngine(models.AbstractModel):
    _name = 'mrp.estimation.calculation'
    _description = 'Manufacturing Estimation Calculation Engine'

    @api.model
    def calculate_material_cost(self, estimation_line):
        """Calculate the total material cost including wastage and overhead."""
        base_cost = estimation_line.quantity * estimation_line.unit_price
        wastage_cost = base_cost * (estimation_line.wastage_percentage / 100)
        overhead_cost = base_cost * (estimation_line.overhead_percentage / 100)

        return float_round(base_cost + wastage_cost + overhead_cost, precision_digits=2)

    @api.model
    def calculate_labor_cost(self, estimation_line):
        """Calculate labor cost based on operation time and labor rate."""
        labor_hours = estimation_line.operation_time
        labor_rate = estimation_line.labor_rate
        efficiency_factor = estimation_line.efficiency_factor or 1.0

        return float_round(labor_hours * labor_rate * efficiency_factor, precision_digits=2)

    @api.model
    def calculate_total_cost(self, estimation):
        """Calculate the total cost of the estimation including all factors."""
        material_cost = sum(line.material_cost for line in estimation.line_ids)
        labor_cost = sum(line.labor_cost for line in estimation.line_ids)
        overhead_cost = material_cost * (estimation.overhead_percentage / 100)

        subtotal = material_cost + labor_cost + overhead_cost
        profit_margin = subtotal * (estimation.profit_margin / 100)

        return {
            'material_cost': float_round(material_cost, precision_digits=2),
            'labor_cost': float_round(labor_cost, precision_digits=2),
            'overhead_cost': float_round(overhead_cost, precision_digits=2),
            'subtotal': float_round(subtotal, precision_digits=2),
            'profit_margin': float_round(profit_margin, precision_digits=2),
            'total': float_round(subtotal + profit_margin, precision_digits=2)
        }