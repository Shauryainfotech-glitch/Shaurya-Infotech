# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class DayPlanDashboardAlias(models.Model):
    """
    Alias model to handle frontend calls to day.plan.dashboard
    This is a completely standalone model that delegates to day.plan.dashboard.clean
    """
    _name = 'day.plan.dashboard'
    _description = 'Day Plan Dashboard (Alias)'
    # No inheritance - this is a completely standalone model to avoid test conflicts
    
    # Add minimum required fields for the dashboard alias model
    name = fields.Char(string="Name", default="Dashboard")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")
    
    # Prevent this model from creating database views during installation
    @api.model
    def init(self):
        _logger.info("Dashboard alias model initialized - no database views created")

    @api.model
    def get_dashboard_data(self, date_range='week', employee_id=False, department_id=False):
        """
        Redirect get_dashboard_data calls to the clean model implementation
        """
        _logger.info("Redirecting dashboard data request from alias model to implementation")
        return self.env['day.plan.dashboard.clean'].get_dashboard_data(
            date_range=date_range,
            employee_id=employee_id,
            department_id=department_id
        )
