from odoo import models, fields, api
import math

class CalculationEngine(models.AbstractModel):
    _name = 'estimation.calculation.engine'
    _description = 'Estimation Calculation Engine'

    def calculate_material_cost(self, product, quantity):
        return product.standard_price * quantity

    def calculate_labor_cost(self, operation_time, labor_rate):
        return operation_time * labor_rate

    def calculate_overhead(self, direct_cost, overhead_rate):
        return direct_cost * (overhead_rate / 100)

    def calculate_total_cost(self, material_cost, labor_cost, overhead):
        return material_cost + labor_cost + overhead

    def calculate_markup(self, total_cost, markup_percentage):
        return total_cost * (1 + markup_percentage / 100)

    def calculate_profit_margin(self, selling_price, total_cost):
        if selling_price == 0:
            return 0
        return ((selling_price - total_cost) / selling_price) * 100 