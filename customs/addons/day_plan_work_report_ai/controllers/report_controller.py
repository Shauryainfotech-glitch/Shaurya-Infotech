import logging
from datetime import datetime, timedelta

from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class ReportController(http.Controller):

    @http.route('/day_plan/report/dashboard', type='http', auth='user')
    def dashboard_report(self, **kwargs):
        """Generate dashboard report"""
        try:
            # Parse parameters
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            employee_id = kwargs.get('employee_id')
            department_id = kwargs.get('department_id')

            if date_from:
                date_from = fields.Date.from_string(date_from)
            else:
                date_from = fields.Date.today() - timedelta(days=30)

            if date_to:
                date_to = fields.Date.from_string(date_to)
            else:
                date_to = fields.Date.today()

            # Build domain
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to)
            ]

            if employee_id:
                domain.append(('employee_id', '=', int(employee_id)))
            elif department_id:
                employees = request.env['hr.employee'].search([('department_id', '=', int(department_id))])
                domain.append(('employee_id', 'in', employees.ids))
            else:
                # Default to current user's data
                domain.append(('employee_id.user_id', '=', request.env.user.id))

            # Get data
            plans = request.env['day.plan'].search(domain)
            tasks = request.env['day.plan.task'].search([('day_plan_id', 'in', plans.ids)])
            work_reports = request.env['work.report'].search([
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('employee_id', 'in', plans.mapped('employee_id').ids)
            ])
            ai_analyses = request.env['ai.analysis'].search([
                ('day_plan_id', 'in', plans.ids)
            ])

            values = {
                'date_from': date_from,
                'date_to': date_to,
                'plans': plans,
                'tasks': tasks,
                'work_reports': work_reports,
                'ai_analyses': ai_analyses,
                'company': request.env.company
            }

            return request.render('day_plan_work_report_ai.dashboard_report_template', values)

        except Exception as e:
            _logger.error("Error generating dashboard report: %s", str(e))
            return request.render('web.http_error', {
                'status_code': 500,
                'status_message': 'Error generating report'
            })

    @http.route('/day_plan/report/export', type='http', auth='user')
    def export_report(self, **kwargs):
        """Export report as PDF"""
        try:
            report_type = kwargs.get('type', 'dashboard')

            if report_type == 'dashboard':
                return self._export_dashboard_report(**kwargs)
            elif report_type == 'productivity':
                return self._export_productivity_report(**kwargs)
            else:
                return request.not_found()

        except Exception as e:
            _logger.error("Error exporting report: %s", str(e))
            return request.render('web.http_error', {
                'status_code': 500,
                'status_message': 'Error exporting report'
            })

    def _export_dashboard_report(self, **kwargs):
        """Export dashboard report as PDF"""
        # Get report data (similar to dashboard_report method)
        date_from = kwargs.get('date_from', fields.Date.today() - timedelta(days=30))
        date_to = kwargs.get('date_to', fields.Date.today())

        if isinstance(date_from, str):
            date_from = fields.Date.from_string(date_from)
        if isinstance(date_to, str):
            date_to = fields.Date.from_string(date_to)

        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('employee_id.user_id', '=', request.env.user.id)
        ]

        plans = request.env['day.plan'].search(domain)

        # Generate PDF using report engine
        report = request.env.ref('day_plan_work_report_ai.dashboard_report_pdf')
        pdf_content, content_type = report._render_qweb_pdf(plans.ids)

        response = request.make_response(
            pdf_content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="dashboard_report_{date_from}_{date_to}.pdf"')
            ]
        )

        return response

    def _export_productivity_report(self, **kwargs):
        """Export productivity analysis report"""
        # Similar implementation for productivity-specific report
        pass

    @http.route('/day_plan/api/report_data', type='json', auth='user')
    def get_report_data(self, **kwargs):
        """Get report data via JSON API"""
        try:
            date_from = kwargs.get('date_from', (fields.Date.today() - timedelta(days=7)).strftime('%Y-%m-%d'))
            date_to = kwargs.get('date_to', fields.Date.today().strftime('%Y-%m-%d'))
            employee_id = kwargs.get('employee_id')

            # Convert string dates to date objects
            if isinstance(date_from, str):
                date_from = fields.Date.from_string(date_from)
            if isinstance(date_to, str):
                date_to = fields.Date.from_string(date_to)

            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to)
            ]

            if employee_id:
                domain.append(('employee_id', '=', employee_id))
            else:
                domain.append(('employee_id.user_id', '=', request.env.user.id))

            # Get plans and related data
            plans = request.env['day.plan'].search(domain)
            tasks = request.env['day.plan.task'].search([('day_plan_id', 'in', plans.ids)])
            analyses = request.env['ai.analysis'].search([('day_plan_id', 'in', plans.ids)])

            # Calculate summary statistics
            total_plans = len(plans)
            completed_plans = len(plans.filtered(lambda p: p.state == 'completed'))
            total_tasks = len(tasks)
            completed_tasks = len(tasks.filtered(lambda t: t.status == 'done'))

            # AI analysis averages
            avg_productivity = sum(analyses.mapped('productivity_score')) / len(analyses) if analyses else 0
            avg_efficiency = sum(analyses.mapped('efficiency_rating')) / len(analyses) if analyses else 0
            avg_wellbeing = sum(analyses.mapped('wellbeing_assessment')) / len(analyses) if analyses else 0

            return {
                'status': 'success',
                'data': {
                    'summary': {
                        'total_plans': total_plans,
                        'completed_plans': completed_plans,
                        'plan_completion_rate': (completed_plans / total_plans * 100) if total_plans else 0,
                        'total_tasks': total_tasks,
                        'completed_tasks': completed_tasks,
                        'task_completion_rate': (completed_tasks / total_tasks * 100) if total_tasks else 0,
                        'avg_productivity': round(avg_productivity, 1),
                        'avg_efficiency': round(avg_efficiency, 1),
                        'avg_wellbeing': round(avg_wellbeing, 1)
                    },
                    'plans': [{
                        'id': plan.id,
                        'name': plan.name,
                        'date': plan.date.strftime('%Y-%m-%d'),
                        'state': plan.state,
                        'completion_ratio': plan.completion_ratio,
                        'total_tasks': plan.total_tasks,
                        'tasks_completed': plan.tasks_completed
                    } for plan in plans],
                    'period': {
                        'date_from': date_from.strftime('%Y-%m-%d'),
                        'date_to': date_to.strftime('%Y-%m-%d')
                    }
                }
            }

        except Exception as e:
            _logger.error("Error getting report data: %s", str(e))
            return {'status': 'error', 'message': str(e)}