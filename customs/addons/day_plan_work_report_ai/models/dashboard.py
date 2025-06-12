import logging
import json
from datetime import datetime, timedelta

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class DayPlanDashboard(models.Model):
    _name = 'day.plan.dashboard'
    _description = 'Day Plan Dashboard'

    name = fields.Char(string="Dashboard Name", default="Productivity Dashboard")
    date_from = fields.Date(string="Date From", default=lambda self: fields.Date.today() - timedelta(days=7))
    date_to = fields.Date(string="Date To", default=fields.Date.today)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")

    # KPI Fields
    total_plans = fields.Integer(string="Total Plans", compute='_compute_dashboard_data')
    completion_rate = fields.Float(string="Completion Rate", compute='_compute_dashboard_data')
    avg_productivity = fields.Float(string="Average Productivity", compute='_compute_dashboard_data')

    # Chart Data
    chart_data = fields.Text(string="Chart Data", compute='_compute_dashboard_data')

    @api.depends('date_from', 'date_to', 'employee_id', 'department_id')
    def _compute_dashboard_data(self):
        for dashboard in self:
            domain = [
                ('date', '>=', dashboard.date_from),
                ('date', '<=', dashboard.date_to)
            ]

            if dashboard.employee_id:
                domain.append(('employee_id', '=', dashboard.employee_id.id))
            elif dashboard.department_id:
                employees = self.env['hr.employee'].search([('department_id', '=', dashboard.department_id.id)])
                domain.append(('employee_id', 'in', employees.ids))

            # Get plans
            plans = self.env['day.plan'].search(domain)

            # Calculate KPIs
            dashboard.total_plans = len(plans)
            if plans:
                total_completion = sum(plans.mapped('completion_ratio'))
                dashboard.completion_rate = total_completion / len(plans)

                # Get AI analysis data
                analyses = self.env['ai.analysis'].search([('day_plan_id', 'in', plans.ids)])
                if analyses:
                    dashboard.avg_productivity = sum(analyses.mapped('productivity_score')) / len(analyses)
                else:
                    dashboard.avg_productivity = 0.0
            else:
                dashboard.completion_rate = 0.0
                dashboard.avg_productivity = 0.0

            # Generate chart data
            chart_data = {
                'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'datasets': [{
                    'label': 'Completed Tasks',
                    'data': [5, 7, 4, 6, 8, 3, 5],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                }]
            }
            dashboard.chart_data = json.dumps(chart_data)

    @api.model
    def get_dashboard_data(self, date_range='week', employee_id=False, department_id=False):
        """Get dashboard data for API calls"""
        today = fields.Date.today()

        if date_range == 'week':
            date_from = today - timedelta(days=7)
        elif date_range == 'month':
            date_from = today - timedelta(days=30)
        else:
            date_from = today - timedelta(days=7)

        dashboard = self.create({
            'date_from': date_from,
            'date_to': today,
            'employee_id': employee_id,
            'department_id': department_id
        })

        return {
            'total_plans': dashboard.total_plans,
            'completion_rate': dashboard.completion_rate,
            'avg_productivity': dashboard.avg_productivity,
            'chart_data': dashboard.chart_data
        }