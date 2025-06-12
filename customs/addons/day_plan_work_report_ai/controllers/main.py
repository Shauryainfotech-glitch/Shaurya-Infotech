import json
import logging
from datetime import datetime, timedelta

from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


class DayPlanController(http.Controller):

    @http.route('/day_plan/dashboard_data', type='json', auth='user', methods=['POST'])
    def get_dashboard_data(self, date_range='week', employee_id=None, department_id=None):
        """Get dashboard data via JSON RPC"""
        try:
            dashboard_model = request.env['day.plan.dashboard']
            data = dashboard_model.get_dashboard_data(
                date_range=date_range,
                employee_id=employee_id,
                department_id=department_id
            )
            return {'status': 'success', 'data': data}
        except Exception as e:
            _logger.error("Error getting dashboard data: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/day_plan/create_plan', type='json', auth='user', methods=['POST'])
    def create_day_plan(self, **kwargs):
        """Create a new day plan via API"""
        try:
            plan_data = {
                'name': kwargs.get('name', 'New Plan'),
                'date': kwargs.get('date', fields.Date.today()),
                'goals': kwargs.get('goals', ''),
                'key_results': kwargs.get('key_results', ''),
                'focus_areas': kwargs.get('focus_areas', ''),
                'potential_blockers': kwargs.get('potential_blockers', '')
            }

            plan = request.env['day.plan'].create(plan_data)
            return {
                'status': 'success',
                'plan_id': plan.id,
                'sequence': plan.sequence
            }
        except Exception as e:
            _logger.error("Error creating day plan: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/day_plan/add_task', type='json', auth='user', methods=['POST'])
    def add_task_to_plan(self, plan_id, task_name, **kwargs):
        """Add a task to a day plan"""
        try:
            task_data = {
                'name': task_name,
                'day_plan_id': plan_id,
                'description': kwargs.get('description', ''),
                'task_type': kwargs.get('task_type', 'other'),
                'priority': kwargs.get('priority', '1'),
                'estimated_hours': kwargs.get('estimated_hours', 0.0)
            }

            task = request.env['day.plan.task'].create(task_data)
            return {
                'status': 'success',
                'task_id': task.id,
                'task_name': task.name
            }
        except Exception as e:
            _logger.error("Error adding task: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/day_plan/update_task_status', type='json', auth='user', methods=['POST'])
    def update_task_status(self, task_id, status):
        """Update task status"""
        try:
            task = request.env['day.plan.task'].browse(task_id)
            if not task.exists():
                return {'status': 'error', 'message': 'Task not found'}

            task.write({'status': status})
            return {'status': 'success', 'message': 'Task status updated'}
        except Exception as e:
            _logger.error("Error updating task status: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    @http.route('/day_plan/submit_work_report', type='json', auth='user', methods=['POST'])
    def submit_work_report(self, **kwargs):
        """Submit a work report"""
        try:
            report_data = {
                'name': kwargs.get('name', 'Work Report'),
                'date': kwargs.get('date', fields.Date.today()),
                'day_plan_id': kwargs.get('day_plan_id'),
                'accomplishments': kwargs.get('accomplishments', ''),
                'challenges': kwargs.get('challenges', ''),
                'solutions': kwargs.get('solutions', ''),
                'learnings': kwargs.get('learnings', ''),
                'next_steps': kwargs.get('next_steps', ''),
                'self_productivity': kwargs.get('self_productivity', '3'),
                'self_quality': kwargs.get('self_quality', '3'),
                'self_satisfaction': kwargs.get('self_satisfaction', '3')
            }

            report = request.env['work.report'].create(report_data)
            return {
                'status': 'success',
                'report_id': report.id,
                'sequence': report.sequence
            }
        except Exception as e:
            _logger.error("Error submitting work report: %s", str(e))
            return {'status': 'error', 'message': str(e)}