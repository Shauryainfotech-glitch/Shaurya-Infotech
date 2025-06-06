from odoo import models, api
import functools
import time

def profile(func):
    """Custom profiler decorator replacement"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

class EstimationPerformance(models.AbstractModel):
    _name = 'mrp.estimation.performance'
    _description = 'Performance Optimizations for Manufacturing Estimation'

    @api.model
    def _get_estimation_domain(self, partner_id=None, date_from=None, date_to=None):
        """Optimized domain builder for estimation queries."""
        domain = []
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        if date_from:
            domain.append(('estimation_date', '>=', date_from))
        if date_to:
            domain.append(('estimation_date', '<=', date_to))
        return domain

    @api.model
    @profile
    def get_estimation_statistics(self, partner_id=None, date_from=None, date_to=None):
        """Optimized statistics calculation using SQL."""
        # Build WHERE clause properly
        where_conditions = []
        params = []
        
        if partner_id:
            where_conditions.append("partner_id = %s")
            params.append(partner_id)
        if date_from:
            where_conditions.append("estimation_date >= %s")
            params.append(date_from)
        if date_to:
            where_conditions.append("estimation_date <= %s")
            params.append(date_to)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "TRUE"
        
        query = f"""
            SELECT 
                COUNT(*) as total_count,
                AVG(estimation_total) as avg_amount,
                SUM(estimation_total) as total_amount,
                COUNT(CASE WHEN state = 'approved' THEN 1 END) as approved_count
            FROM mrp_estimation
            WHERE {where_clause}
        """
        
        self.env.cr.execute(query, params)
        return self.env.cr.dictfetchone()

    @api.model
    def prefetch_estimation_data(self, estimation_ids):
        """Prefetch related records for better performance."""
        if not estimation_ids:
            return
            
        # Prefetch related records in a single query
        self.env['mrp.estimation'].browse(estimation_ids).read([
            'name', 'partner_id', 'estimation_date', 'state', 'estimation_total',
            'estimation_line_ids', 'user_id'
        ])
        
        # Prefetch line details
        line_ids = self.env['mrp.estimation.line'].search([
            ('estimation_id', 'in', estimation_ids)
        ])
        line_ids.read([
            'product_id', 'product_qty', 'product_cost',
            'subtotal'
        ])