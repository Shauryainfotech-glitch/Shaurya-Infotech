from odoo import models, fields, api

class EstimationPerformance(models.Model):
    _name = 'mrp.estimation.performance'
    _description = 'Performance Optimizations for Estimations'

    estimation_id = fields.Many2one('mrp.estimation', string="Estimation", required=True)
    estimated_time = fields.Float(string="Estimated Time (hrs)")
    actual_time = fields.Float(string="Actual Time (hrs)")
    performance_ratio = fields.Float(string="Performance Ratio", compute='_compute_performance_ratio')

    @api.depends('estimated_time', 'actual_time')
    def _compute_performance_ratio(self):
        for record in self:
            if record.estimated_time and record.actual_time:
                record.performance_ratio = record.actual_time / record.estimated_time
            else:
                record.performance_ratio = 0.0
