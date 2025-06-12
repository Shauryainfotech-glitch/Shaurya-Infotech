import json
import logging
from datetime import datetime, timedelta

from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class DashboardController(http.Controller):

    @http.route('/day_plan/dashboard', type='http', auth='user', website=False)
    def dashboard_view(self, **kwargs):
        """Render dashboard page"""
        try:
            # Get dashboard data
            dashboard_model = request.env['day.plan.dashboard']
            dashboard_data = dashboard_model.get_dashboard_data()

            # Get recent activities
            recent_plans = request.env['day.plan'].search(
                [('employee_id.user_id', '=', request.env.user.id)],
                order='date desc',
                limit=5
            )

            # Get recent work reports
            recent_reports = request.env['work.report'].search(
                [('employee_id.user_id', '=', request.env.user.id)],
                order='date desc',
                limit=5
            )

            values = {
                'dashboard_data': dashboard_data,
                'recent_plans': recent_plans,
                'recent_reports': recent_reports,
                'user': request.env.user,
                'employee': request.env.user.employee_id
            }

            return request.render('day_plan_work_report_ai.dashboard_template', values)

        except Exception as e:
            _logger.error("Error rendering dashboard: %s", str(e))
            return request.render('web.http_error', {
                'status_code': 500,
                'status_message': 'Internal Server Error'
            })

    @http.route('/day_plan/dashboard/kpi', type='json', auth='user')
    def get_kpi_data(self, date_range='week', employee_id=None):
        """Get KPI data for dashboard widgets"""
        try:
            today = fields.Date.today()

            if date_range == 'week':
                date_from = today - timedelta(days=7)
            elif date_range == 'month':
                date_from = today - timedelta(days=30)
            elif date_range == 'quarter':
                date_from = today - timedelta(days=90)
            else:
                date_from = today - timedelta(days=7)

            domain = [
                ('date', '>=', date_from),
                ('date', '<=', today)
            ]

            if employee_id:
                domain.append(('employee_id', '=', employee_id))
            else:
                domain.append(('employee_id.user_id', '=', request.env.user.id))

            # Get plans and tasks
            plans = request.env['day.plan'].search(domain)
            tasks = request.env['day.plan.task'].search([('day_plan_id', 'in', plans.ids)])

            # Calculate KPIs
            total_plans = len(plans)
            completed_plans = len(plans.filtered(lambda p: p.state == 'completed'))
            total_tasks = len(tasks)
            completed_tasks = len(tasks.filtered(lambda t: t.status == 'done'))

            # AI Analysis scores
            analyses = request.env['ai.analysis'].search([
                ('day_plan_id', 'in', plans.ids),
                ('state', '=', 'completed')
            ])

            avg_productivity = sum(analyses.mapped('productivity_score')) / len(analyses) if analyses else 0
            avg_efficiency = sum(analyses.mapped('efficiency_rating')) / len(analyses) if analyses else 0
            avg_wellbeing = sum(analyses.mapped('wellbeing_assessment')) / len(analyses) if analyses else 0

            return {
                'status': 'success',
                'data': {
                    'total_plans': total_plans,
                    'completed_plans': completed_plans,
                    'plan_completion_rate': (completed_plans / total_plans * 100) if total_plans else 0,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'task_completion_rate': (completed_tasks / total_tasks * 100) if total_tasks else 0,
                    'avg_productivity': round(avg_productivity, 1),
                    'avg_efficiency': round(avg_efficiency, 1),
                    'avg_wellbeing': round(avg_wellbeing, 1),
                    'date_range': date_range,
                    'date_from': date_from.strftime('%Y-%m-%d'),
                    'date_to': today.strftime('%Y-%m-%d')
                }
            }

        except Exception as e:
            _logger.error("Error getting KPI data: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/day_plan/dashboard/charts', type='json', auth='user')
    def get_chart_data(self, chart_type='productivity', date_range='week'):
        """Get chart data for dashboard"""
        try:
            today = fields.Date.today()

            if date_range == 'week':
                date_from = today - timedelta(days=7)
                period_days = 7
            elif date_range == 'month':
                date_from = today - timedelta(days=30)
                period_days = 30
            else:
                date_from = today - timedelta(days=7)
                period_days = 7

            # Generate date labels
            labels = []
            dates = []
            for i in range(period_days):
                date = date_from + timedelta(days=i)
                dates.append(date)
                labels.append(date.strftime('%m/%d'))

            # Get data based on chart type
            if chart_type == 'productivity':
                data = self._get_productivity_chart_data(dates)
            elif chart_type == 'tasks':
                data = self._get_tasks_chart_data(dates)
            elif chart_type == 'wellbeing':
                data = self._get_wellbeing_chart_data(dates)
            else:
                data = {'datasets': []}

            return {
                'status': 'success',
                'data': {
                    'labels': labels,
                    **data
                }
            }

        except Exception as e:
            _logger.error("Error getting chart data: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    def _get_productivity_chart_data(self, dates):
        """Get productivity chart data"""
        productivity_scores = []
        efficiency_scores = []

        for date in dates:
            plans = request.env['day.plan'].search([
                ('date', '=', date),
                ('employee_id.user_id', '=', request.env.user.id)
            ])

            if plans:
                analyses = request.env['ai.analysis'].search([
                    ('day_plan_id', 'in', plans.ids),
                    ('state', '=', 'completed')
                ])

                avg_prod = sum(analyses.mapped('productivity_score')) / len(analyses) if analyses else 0
                avg_eff = sum(analyses.mapped('efficiency_rating')) / len(analyses) if analyses else 0
            else:
                avg_prod = 0
                avg_eff = 0

            productivity_scores.append(avg_prod)
            efficiency_scores.append(avg_eff)

        return {
            'datasets': [
                {
                    'label': 'Productivity Score',
                    'data': productivity_scores,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.1
                },
                {
                    'label': 'Efficiency Score',
                    'data': efficiency_scores,
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'tension': 0.1
                }
            ]
        }

    def _get_tasks_chart_data(self, dates):
        """Get tasks chart data"""
        planned_tasks = []
        completed_tasks = []

        for date in dates:
            plans = request.env['day.plan'].search([
                ('date', '=', date),
                ('employee_id.user_id', '=', request.env.user.id)
            ])

            if plans:
                tasks = request.env['day.plan.task'].search([('day_plan_id', 'in', plans.ids)])
                planned = len(tasks)
                completed = len(tasks.filtered(lambda t: t.status == 'done'))
            else:
                planned = 0
                completed = 0

            planned_tasks.append(planned)
            completed_tasks.append(completed)

        return {
            'datasets': [
                {
                    'label': 'Planned Tasks',
                    'data': planned_tasks,
                    'backgroundColor': 'rgba(54, 162, 235, 0.8)',
                    'borderColor': 'rgb(54, 162, 235)',
                    'borderWidth': 1
                },
                {
                    'label': 'Completed Tasks',
                    'data': completed_tasks,
                    'backgroundColor': 'rgba(75, 192, 192, 0.8)',
                    'borderColor': 'rgb(75, 192, 192)',
                    'borderWidth': 1
                }
            ]
        }

    def _get_wellbeing_chart_data(self, dates):
        """Get wellbeing chart data"""
        wellbeing_scores = []

        for date in dates:
            plans = request.env['day.plan'].search([
                ('date', '=', date),
                ('employee_id.user_id', '=', request.env.user.id)
            ])

            if plans:
                analyses = request.env['ai.analysis'].search([
                    ('day_plan_id', 'in', plans.ids),
                    ('state', '=', 'completed')
                ])

                avg_wellbeing = sum(analyses.mapped('wellbeing_assessment')) / len(analyses) if analyses else 0
            else:
                avg_wellbeing = 0

            wellbeing_scores.append(avg_wellbeing)

        return {
            'datasets': [
                {
                    'label': 'Wellbeing Score',
                    'data': wellbeing_scores,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'tension': 0.1,
                    'fill': True
                }
            ]
        }