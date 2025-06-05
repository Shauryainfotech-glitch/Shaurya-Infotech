# -*- coding: utf-8 -*-

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class DayPlanDashboardAlias(models.Model):
    """
    Alias model to handle frontend calls to day.plan.dashboard
    This redirects all calls to the actual implementation in day.plan.dashboard.clean
    """
    _name = 'day.plan.dashboard'
    _description = 'Day Plan Dashboard (Alias)'
    _inherit = ['day.plan.dashboard.clean']
    _table = 'day_plan_dashboard_clean'  # Use same table as the original model

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
