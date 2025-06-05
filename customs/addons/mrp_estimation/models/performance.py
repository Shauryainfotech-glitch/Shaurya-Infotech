from odoo import models, api


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
    def get_estimation_statistics(self, partner_id=None, date_from=None, date_to=None):
        """Optimized statistics calculation using SQL."""
        domain = self._get_estimation_domain(partner_id, date_from, date_to)
        
        query = """
            SELECT 
                COUNT(*) as total_count,
                AVG(estimation_total) as avg_amount,
                SUM(estimation_total) as total_amount,
                COUNT(CASE WHEN state = 'approved' THEN 1 END) as approved_count
            FROM mrp_estimation
            WHERE %s
        """
        
        where_clause = "TRUE"
        params = []
        
        if domain:
            where_clause = " AND ".join(["%s" for _ in domain])
            params = [d[2] for d in domain]
        
        self.env.cr.execute(query % where_clause, params)
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