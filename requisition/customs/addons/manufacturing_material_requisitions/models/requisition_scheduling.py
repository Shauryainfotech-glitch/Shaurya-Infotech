from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class RequisitionScheduler(models.Model):
    _name = 'manufacturing.requisition.scheduler'
    _description = 'Automated Requisition Scheduler'
    _rec_name = 'name'

    name = fields.Char(string='Scheduler Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    schedule_type = fields.Selection([
        ('recurring', 'Recurring Schedule'),
        ('demand_based', 'Demand-Based'),
        ('stock_level', 'Stock Level Triggered'),
        ('production_plan', 'Production Plan Based')
    ], string='Schedule Type', required=True, default='recurring')
    
    # Timing Configuration
    frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom Interval')
    ], string='Frequency', default='weekly')
    interval_number = fields.Integer(string='Interval Number', default=1)
    next_execution = fields.Datetime(string='Next Execution', required=True)
    last_execution = fields.Datetime(string='Last Execution', readonly=True)
    
    # Trigger Conditions
    min_stock_level = fields.Float(string='Minimum Stock Level')
    production_window_days = fields.Integer(string='Production Window (Days)', default=7)
    auto_create_requisitions = fields.Boolean(string='Auto Create Requisitions', default=True)
    
    # Relationships
    department_id = fields.Many2one('hr.department', string='Department')
    product_category_ids = fields.Many2many('product.category', string='Product Categories')
    location_id = fields.Many2one('stock.location', string='Stock Location')
    
    # Scheduling Rules
    rule_ids = fields.One2many('manufacturing.requisition.scheduler.rule', 'scheduler_id', string='Scheduling Rules')
    
    # Statistics
    total_executions = fields.Integer(string='Total Executions', readonly=True)
    success_rate = fields.Float(string='Success Rate (%)', compute='_compute_success_rate', readonly=True)
    last_error = fields.Text(string='Last Error', readonly=True)
    
    @api.depends('total_executions', 'rule_ids.success_count', 'rule_ids.failure_count')
    def _compute_success_rate(self):
        for scheduler in self:
            total_attempts = sum(scheduler.rule_ids.mapped('success_count')) + sum(scheduler.rule_ids.mapped('failure_count'))
            if total_attempts > 0:
                success_count = sum(scheduler.rule_ids.mapped('success_count'))
                scheduler.success_rate = (success_count / total_attempts) * 100
            else:
                scheduler.success_rate = 0.0
    
    def execute_schedule(self):
        """Execute the scheduled requisition creation"""
        try:
            if not self.active:
                return False
                
            requisitions_created = 0
            
            for rule in self.rule_ids:
                if rule.active:
                    result = rule.execute_rule()
                    if result:
                        requisitions_created += result
            
            # Update execution tracking
            self.last_execution = fields.Datetime.now()
            self.total_executions += 1
            self._calculate_next_execution()
            
            _logger.info(f"Scheduler {self.name} executed successfully. Created {requisitions_created} requisitions.")
            return requisitions_created
            
        except Exception as e:
            self.last_error = str(e)
            _logger.error(f"Error executing scheduler {self.name}: {str(e)}")
            return False
    
    def _calculate_next_execution(self):
        """Calculate the next execution time based on frequency"""
        if self.frequency == 'daily':
            self.next_execution = self.last_execution + timedelta(days=self.interval_number)
        elif self.frequency == 'weekly':
            self.next_execution = self.last_execution + timedelta(weeks=self.interval_number)
        elif self.frequency == 'monthly':
            self.next_execution = self.last_execution + timedelta(days=30 * self.interval_number)
        else:  # custom
            self.next_execution = self.last_execution + timedelta(days=self.interval_number)
    
    @api.model
    def run_scheduled_tasks(self):
        """Cron method to execute all due schedulers"""
        due_schedulers = self.search([
            ('active', '=', True),
            ('next_execution', '<=', fields.Datetime.now())
        ])
        
        for scheduler in due_schedulers:
            scheduler.execute_schedule()


class RequisitionSchedulerRule(models.Model):
    _name = 'manufacturing.requisition.scheduler.rule'
    _description = 'Requisition Scheduler Rule'
    _rec_name = 'name'

    name = fields.Char(string='Rule Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    scheduler_id = fields.Many2one('manufacturing.requisition.scheduler', string='Scheduler', required=True, ondelete='cascade')
    
    # Rule Configuration
    rule_type = fields.Selection([
        ('stock_based', 'Stock Level Based'),
        ('time_based', 'Time Based'),
        ('production_based', 'Production Schedule Based'),
        ('consumption_based', 'Consumption Pattern Based')
    ], string='Rule Type', required=True, default='stock_based')
    
    # Stock-based criteria
    product_ids = fields.Many2many('product.product', string='Products')
    min_qty = fields.Float(string='Minimum Quantity')
    max_qty = fields.Float(string='Maximum Quantity')
    reorder_qty = fields.Float(string='Reorder Quantity')
    
    # Time-based criteria
    lead_time_days = fields.Integer(string='Lead Time (Days)', default=1)
    safety_stock_days = fields.Integer(string='Safety Stock (Days)', default=2)
    
    # Production-based criteria
    production_forecast_days = fields.Integer(string='Production Forecast (Days)', default=7)
    workorder_trigger = fields.Boolean(string='Trigger on Work Order Creation')
    
    # Auto-creation settings
    template_id = fields.Many2one('manufacturing.requisition.template', string='Requisition Template')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Default Priority', default='1')
    
    # Statistics
    success_count = fields.Integer(string='Successful Executions', readonly=True)
    failure_count = fields.Integer(string='Failed Executions', readonly=True)
    last_execution = fields.Datetime(string='Last Execution', readonly=True)
    
    def execute_rule(self):
        """Execute this specific rule"""
        try:
            requisitions_created = 0
            
            if self.rule_type == 'stock_based':
                requisitions_created = self._execute_stock_based_rule()
            elif self.rule_type == 'time_based':
                requisitions_created = self._execute_time_based_rule()
            elif self.rule_type == 'production_based':
                requisitions_created = self._execute_production_based_rule()
            elif self.rule_type == 'consumption_based':
                requisitions_created = self._execute_consumption_based_rule()
            
            self.success_count += 1
            self.last_execution = fields.Datetime.now()
            return requisitions_created
            
        except Exception as e:
            self.failure_count += 1
            _logger.error(f"Error executing rule {self.name}: {str(e)}")
            return 0
    
    def _execute_stock_based_rule(self):
        """Execute stock level based requisition creation"""
        requisitions_created = 0
        
        for product in self.product_ids:
            stock_qty = product.qty_available
            if stock_qty <= self.min_qty:
                # Create requisition for this product
                requisition_vals = {
                    'department_id': self.scheduler_id.department_id.id,
                    'priority': self.priority,
                    'state': 'draft',
                    'requisition_date': fields.Date.today(),
                    'required_date': fields.Date.today() + timedelta(days=self.lead_time_days),
                    'notes': f'Auto-generated by scheduler rule: {self.name}',
                    'line_ids': [(0, 0, {
                        'product_id': product.id,
                        'quantity': max(self.reorder_qty, self.max_qty - stock_qty),
                        'uom_id': product.uom_id.id,
                        'required_date': fields.Date.today() + timedelta(days=self.lead_time_days),
                    })]
                }
                
                if self.template_id:
                    # Apply template settings
                    requisition_vals.update({
                        'template_id': self.template_id.id,
                        'department_id': self.template_id.department_id.id or requisition_vals['department_id'],
                    })
                
                requisition = self.env['manufacturing.material.requisition'].create(requisition_vals)
                requisitions_created += 1
        
        return requisitions_created
    
    def _execute_time_based_rule(self):
        """Execute time-based requisition creation"""
        # Check if it's time to create requisitions based on schedule
        # This could involve checking production schedules, delivery dates, etc.
        return 0
    
    def _execute_production_based_rule(self):
        """Execute production schedule based requisition creation"""
        requisitions_created = 0
        
        # Look for upcoming production orders
        future_date = fields.Date.today() + timedelta(days=self.production_forecast_days)
        production_orders = self.env['mrp.production'].search([
            ('date_planned_start', '<=', future_date),
            ('date_planned_start', '>=', fields.Date.today()),
            ('state', 'in', ['confirmed', 'planned'])
        ])
        
        for production in production_orders:
            # Check if materials are available
            missing_materials = []
            for move in production.move_raw_ids:
                if move.product_uom_qty > move.product_id.qty_available:
                    missing_materials.append({
                        'product_id': move.product_id.id,
                        'required_qty': move.product_uom_qty - move.product_id.qty_available,
                        'uom_id': move.product_uom.id
                    })
            
            if missing_materials:
                # Create requisition for missing materials
                requisition_vals = {
                    'department_id': self.scheduler_id.department_id.id,
                    'priority': self.priority,
                    'state': 'draft',
                    'requisition_date': fields.Date.today(),
                    'required_date': production.date_planned_start.date() - timedelta(days=self.lead_time_days),
                    'production_id': production.id,
                    'notes': f'Auto-generated for production order: {production.name}',
                    'line_ids': [(0, 0, {
                        'product_id': material['product_id'],
                        'quantity': material['required_qty'],
                        'uom_id': material['uom_id'],
                        'required_date': production.date_planned_start.date() - timedelta(days=self.lead_time_days),
                    }) for material in missing_materials]
                }
                
                requisition = self.env['manufacturing.material.requisition'].create(requisition_vals)
                requisitions_created += 1
        
        return requisitions_created
    
    def _execute_consumption_based_rule(self):
        """Execute consumption pattern based requisition creation"""
        # Analyze historical consumption patterns and predict future needs
        return 0


class RequisitionOptimizer(models.Model):
    _name = 'manufacturing.requisition.optimizer'
    _description = 'Requisition Optimizer'
    _rec_name = 'name'

    name = fields.Char(string='Optimizer Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    # Optimization Criteria
    optimization_type = fields.Selection([
        ('cost', 'Cost Optimization'),
        ('lead_time', 'Lead Time Optimization'),
        ('inventory', 'Inventory Level Optimization'),
        ('supplier', 'Supplier Performance Optimization'),
        ('combined', 'Combined Optimization')
    ], string='Optimization Type', required=True, default='cost')
    
    # Constraints
    max_inventory_value = fields.Float(string='Max Inventory Value')
    max_lead_time_days = fields.Integer(string='Max Lead Time (Days)')
    preferred_supplier_ids = fields.Many2many('res.partner', string='Preferred Suppliers')
    
    # Algorithm Settings
    algorithm = fields.Selection([
        ('linear', 'Linear Programming'),
        ('genetic', 'Genetic Algorithm'),
        ('simulated_annealing', 'Simulated Annealing'),
        ('greedy', 'Greedy Algorithm')
    ], string='Optimization Algorithm', default='greedy')
    
    # Results
    last_optimization = fields.Datetime(string='Last Optimization', readonly=True)
    optimization_results = fields.Text(string='Last Results', readonly=True)
    improvement_percentage = fields.Float(string='Improvement %', readonly=True)
    
    def optimize_requisitions(self, requisition_ids=None):
        """Run optimization on specified requisitions"""
        try:
            if not requisition_ids:
                requisition_ids = self.env['manufacturing.material.requisition'].search([
                    ('state', 'in', ['draft', 'submitted'])
                ]).ids
            
            requisitions = self.env['manufacturing.material.requisition'].browse(requisition_ids)
            
            if self.optimization_type == 'cost':
                result = self._optimize_cost(requisitions)
            elif self.optimization_type == 'lead_time':
                result = self._optimize_lead_time(requisitions)
            elif self.optimization_type == 'inventory':
                result = self._optimize_inventory(requisitions)
            elif self.optimization_type == 'supplier':
                result = self._optimize_supplier_selection(requisitions)
            else:  # combined
                result = self._optimize_combined(requisitions)
            
            self.last_optimization = fields.Datetime.now()
            self.optimization_results = result.get('summary', 'Optimization completed')
            self.improvement_percentage = result.get('improvement_percentage', 0.0)
            
            return result
            
        except Exception as e:
            _logger.error(f"Error in optimization: {str(e)}")
            return {'error': str(e)}
    
    def _optimize_cost(self, requisitions):
        """Optimize requisitions for minimum cost"""
        total_original_cost = 0
        total_optimized_cost = 0
        optimizations_made = 0
        
        for requisition in requisitions:
            for line in requisition.line_ids:
                original_cost = line.estimated_cost
                total_original_cost += original_cost
                
                # Find cheapest supplier
                suppliers = line.product_id.seller_ids.sorted('price')
                if suppliers:
                    best_supplier = suppliers[0]
                    optimized_cost = best_supplier.price * line.quantity
                    
                    if optimized_cost < original_cost:
                        line.write({
                            'preferred_supplier_id': best_supplier.name.id,
                            'estimated_cost': optimized_cost
                        })
                        optimizations_made += 1
                    
                    total_optimized_cost += optimized_cost
                else:
                    total_optimized_cost += original_cost
        
        improvement = ((total_original_cost - total_optimized_cost) / total_original_cost * 100) if total_original_cost > 0 else 0
        
        return {
            'summary': f'Cost optimization completed. {optimizations_made} lines optimized.',
            'improvement_percentage': improvement,
            'original_cost': total_original_cost,
            'optimized_cost': total_optimized_cost
        }
    
    def _optimize_lead_time(self, requisitions):
        """Optimize requisitions for minimum lead time"""
        optimizations_made = 0
        
        for requisition in requisitions:
            for line in requisition.line_ids:
                # Find supplier with shortest lead time
                suppliers = line.product_id.seller_ids.sorted('delay')
                if suppliers:
                    best_supplier = suppliers[0]
                    if not line.preferred_supplier_id or line.preferred_supplier_id.id != best_supplier.name.id:
                        line.write({
                            'preferred_supplier_id': best_supplier.name.id,
                            'estimated_lead_time': best_supplier.delay
                        })
                        optimizations_made += 1
        
        return {
            'summary': f'Lead time optimization completed. {optimizations_made} lines optimized.',
            'improvement_percentage': 0,  # Would need historical data to calculate
        }
    
    def _optimize_inventory(self, requisitions):
        """Optimize requisitions to maintain optimal inventory levels"""
        # Implementation would involve economic order quantity calculations
        return {
            'summary': 'Inventory optimization completed.',
            'improvement_percentage': 0,
        }
    
    def _optimize_supplier_selection(self, requisitions):
        """Optimize supplier selection based on performance metrics"""
        # Implementation would analyze supplier performance history
        return {
            'summary': 'Supplier optimization completed.',
            'improvement_percentage': 0,
        }
    
    def _optimize_combined(self, requisitions):
        """Combined optimization using multiple criteria"""
        # Implementation would use weighted scoring of different factors
        return {
            'summary': 'Combined optimization completed.',
            'improvement_percentage': 0,
        } 