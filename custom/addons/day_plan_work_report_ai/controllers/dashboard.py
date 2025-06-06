from odoo import http
from odoo.http import request
import json
from datetime import datetime, timedelta
import io
import xlsxwriter
import base64
import logging

_logger = logging.getLogger(__name__)

class DayPlanDashboardController(http.Controller):
    @http.route('/day_plan_work_report_ai/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self, date_range='week', employee_id=False, department_id=False):
        """
        Return dashboard data based on filters
        :param date_range: day, week, month, quarter, all
        :param employee_id: optional employee ID filter
        :param department_id: optional department ID filter
        :return: dict with KPIs and chart data
        """
        # Default response with placeholder data 
        default_response = {
            'kpis': {
                'total_plans': 0,
                'plans_today': 0,
                'completed_plans': 0,
                'pending_tasks': 0,
                'productivity_score': 0,
                'efficiency_rating': 0,
                'wellbeing_assessment': 0,
                'plans_change': 0,
                'tasks_change': 0,
                'completion_rate': 0,
                'avg_productivity': 0,
                'tasks_due_today': 0,
                'overdue_tasks': 0,
                'attention_items': 0,
            },
            'charts': {
                'productivity': {
                    'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'datasets': [{
                        'label': 'Productivity',
                        'data': [65, 70, 75, 80, 75, 68, 72],
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'borderColor': 'rgba(54, 162, 235, 1)',
                        'borderWidth': 1,
                        'fill': False
                    }]
                },
                'tasks': {
                    'labels': ['Done', 'In Progress', 'Draft'],
                    'datasets': [{
                        'label': 'Tasks',
                        'data': [10, 5, 3],
                        'backgroundColor': ['#1cc88a', '#f6c23e', '#858796'],
                        'borderWidth': 1
                    }]
                },
                'completion': {
                    'labels': ['Completed', 'Pending'],
                    'datasets': [{
                        'data': [18, 6],
                        'backgroundColor': ['#4e73df', '#858796'],
                    }]
                },
                'wellbeing': {
                    'labels': ['Focus', 'Energy', 'Stress', 'Satisfaction', 'Work-Life Balance'],
                    'datasets': [{
                        'label': 'Current Week',
                        'data': [80, 70, 60, 75, 65],
                        'fill': True,
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'borderColor': 'rgb(75, 192, 192)',
                        'pointBackgroundColor': 'rgb(75, 192, 192)',
                        'pointBorderColor': '#fff',
                    }]
                }
            }
        }

        try:
            # Calculate date range
            today = datetime.now().date()
            start_date = False
            end_date = today

            if date_range == 'day':
                start_date = today
            elif date_range == 'week':
                start_date = today - timedelta(days=today.weekday())
            elif date_range == 'month':
                start_date = today.replace(day=1)
            elif date_range == 'quarter':
                month = today.month
                quarter_start_month = ((month - 1) // 3) * 3 + 1
                start_date = today.replace(month=quarter_start_month, day=1)
            # For 'all', we don't set a start_date filter

            # Get current user's employee if not specified - safely handle missing employee
            if not employee_id:
                if request.env.user.employee_id:
                    employee_id = request.env.user.employee_id.id
                else:
                    _logger.info(f"User {request.env.user.name} (ID: {request.env.user.id}) has no associated employee record")

            # Build domain for day.plan records based on filters
            domain = []
            if employee_id:
                domain.append(('employee_id', '=', employee_id))
            if department_id:
                domain.append(('department_id', '=', department_id))
            if start_date:
                domain.append(('date', '>=', start_date))
            domain.append(('date', '<=', end_date))

            # Compute previous period for comparisons
            if start_date:
                period_length = (end_date - start_date).days + 1
                prev_end_date = start_date - timedelta(days=1)
                prev_start_date = prev_end_date - timedelta(days=period_length - 1)
                prev_domain = domain.copy()
                prev_domain.remove(('date', '>=', start_date))
                prev_domain.remove(('date', '<=', end_date))
                prev_domain.append(('date', '>=', prev_start_date))
                prev_domain.append(('date', '<=', prev_end_date))
            else:
                # Default previous period if no date range
                prev_domain = False

            # Get plans for current period
            day_plan_obj = request.env['day.plan']
            plans = day_plan_obj.search(domain)
            
            # Get plans from previous period for comparisons
            prev_plans = prev_domain and day_plan_obj.search(prev_domain) or day_plan_obj
            
            # Get all tasks for these plans
            current_tasks = request.env['day.plan.task'].search([
                ('day_plan_id', 'in', plans.ids)
            ])
            
            prev_tasks = prev_domain and request.env['day.plan.task'].search([
                ('day_plan_id', 'in', prev_plans.ids)
            ]) or request.env['day.plan.task']
            
            # Calculate KPIs
            total_plans = len(plans)
            plans_today_count = len(plans.filtered(lambda p: p.date == today))
            completed_plans = len(plans.filtered(lambda p: p.state == 'completed'))
            
            # Calculate tasks metrics
            total_tasks = len(current_tasks)
            completed_tasks = len(current_tasks.filtered(lambda t: t.state == 'done'))
            pending_tasks = len(current_tasks.filtered(lambda t: t.state in ['draft', 'in_progress']))
            overdue_tasks = len(current_tasks.filtered(lambda t: t.state != 'done' and t.deadline and t.deadline < today))
            tasks_due_today = len(current_tasks.filtered(lambda t: t.state != 'done' and t.deadline == today))
            
            # Calculate change percentages
            prev_total_plans = len(prev_plans)
            plans_change = (((total_plans - prev_total_plans) / prev_total_plans * 100)
                           if prev_total_plans else 0)
            
            prev_total_tasks = len(prev_tasks)
            tasks_change = (((total_tasks - prev_total_tasks) / prev_total_tasks * 100)
                           if prev_total_tasks else 0)
            
            # Calculate completion rate
            completion_rate = ((completed_tasks / total_tasks * 100)
                              if total_tasks else 0)
            
            # Calculate productivity scores
            productivity_scores = [plan.productivity_score for plan in plans if plan.productivity_score]
            avg_productivity = sum(productivity_scores) / len(productivity_scores) if productivity_scores else 0
            
            # Get latest efficiency and wellbeing
            latest_plan = plans.sorted(lambda p: p.date, reverse=True)[:1]
            efficiency_rating = latest_plan and latest_plan.efficiency_rating or 0
            wellbeing_assessment = latest_plan and latest_plan.wellbeing_assessment or 0
            
            # Calculate attention items (tasks needing attention)
            attention_items = overdue_tasks + tasks_due_today
            
            # Prepare productivity chart data - last 7 dates
            date_labels = []
            productivity_data = []
            efficiency_data = []
            
            for i in range(6, -1, -1):
                chart_date = today - timedelta(days=i)
                date_labels.append(chart_date.strftime('%a'))
                
                day_plan = plans.filtered(lambda p: p.date == chart_date)
                day_productivity = 0
                day_efficiency = 0
                
                if day_plan:
                    day_productivity = sum(p.productivity_score or 0 for p in day_plan) / len(day_plan)
                    day_efficiency = sum(p.efficiency_rating or 0 for p in day_plan) / len(day_plan)
                
                productivity_data.append(day_productivity)
                efficiency_data.append(day_efficiency)
            
            # Prepare tasks chart data by category
            task_categories = {}
            for task in current_tasks:
                category = task.category or "Uncategorized"
                if category not in task_categories:
                    task_categories[category] = {
                        'total': 0,
                        'completed': 0
                    }
                task_categories[category]['total'] += 1
                if task.state == 'done':
                    task_categories[category]['completed'] += 1
            
            category_labels = list(task_categories.keys())
            total_by_category = [task_categories[cat]['total'] for cat in category_labels]
            completed_by_category = [task_categories[cat]['completed'] for cat in category_labels]
            
            # Prepare completion chart data
            completion_labels = ['Completed', 'Pending', 'Overdue']
            completion_data = [completed_tasks, pending_tasks - overdue_tasks, overdue_tasks]
            
            # Format all chart data for Chart.js
            productivity_chart = {
                'labels': date_labels,
                'datasets': [
                    {
                        'label': 'Productivity',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'borderColor': 'rgba(75, 192, 192, 1)',
                        'data': productivity_data,
                        'fill': 'start',
                        'tension': 0.4
                    },
                    {
                        'label': 'Efficiency',
                        'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                        'borderColor': 'rgba(153, 102, 255, 1)',
                        'data': efficiency_data,
                        'fill': 'start',
                        'tension': 0.4
                    }
                ]
            }
            
            tasks_chart = {
                'labels': category_labels,
                'datasets': [
                    {
                        'label': 'Total Tasks',
                        'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                        'borderColor': 'rgba(54, 162, 235, 1)',
                        'borderWidth': 1,
                        'data': total_by_category
                    },
                    {
                        'label': 'Completed',
                        'backgroundColor': 'rgba(75, 192, 192, 0.5)',
                        'borderColor': 'rgba(75, 192, 192, 1)',
                        'borderWidth': 1,
                        'data': completed_by_category
                    }
                ]
            }
            
            completion_chart = {
                'labels': completion_labels,
                'datasets': [{
                    'data': completion_data,
                    'backgroundColor': [
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 99, 132, 0.5)'
                    ],
                    'borderColor': [
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    'borderWidth': 1
                }]
            }
            
            # Prepare wellbeing chart data (radar)
            # Using the latest available wellbeing data
            wellbeing_chart = {
                'labels': ['Focus', 'Energy', 'Stress', 'Satisfaction', 'Work-Life Balance'],
                'datasets': [{
                    'label': 'Current Week',
                    'data': [
                        latest_plan and latest_plan.focus_score or 70,
                        latest_plan and latest_plan.energy_level or 65,
                        100 - (latest_plan and latest_plan.stress_level or 30),
                        latest_plan and latest_plan.satisfaction or 75,
                        latest_plan and latest_plan.work_life_balance or 70
                    ],
                    'fill': True,
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgb(75, 192, 192)',
                    'pointBackgroundColor': 'rgb(75, 192, 192)',
                    'pointBorderColor': '#fff'
                }]
            }

            return {
                'kpis': {
                    'total_plans': total_plans,
                    'plans_today': plans_today_count,
                    'completed_plans': completed_plans,
                    'pending_tasks': pending_tasks,
                    'productivity_score': round(avg_productivity, 1),
                    'efficiency_rating': round(efficiency_rating, 1),
                    'wellbeing_assessment': round(wellbeing_assessment, 1),
                    'plans_change': round(plans_change, 1),
                    'tasks_change': round(tasks_change, 1),
                    'completion_rate': round(completion_rate, 1),
                    'avg_productivity': round(avg_productivity, 1),
                    'tasks_due_today': tasks_due_today,
                    'overdue_tasks': overdue_tasks,
                    'attention_items': attention_items,
                },
                'charts': {
                    'productivity': productivity_chart,
                    'tasks': tasks_chart,
                    'completion': completion_chart,
                    'wellbeing': wellbeing_chart
                }
            }
        except Exception as e:
            _logger.exception("Error generating dashboard data: %s", str(e))
            # Return our predefined default response with demo chart data
            default_response['error'] = str(e)
            return default_response
    
    @http.route('/day_plan_work_report_ai/export_dashboard_data', type='http', auth='user')
    def export_dashboard_data(self, format='pdf', filters=None):
        """Export dashboard data in the requested format"""
        try:
            if filters:
                filters = json.loads(filters)
            else:
                filters = {'dateRange': 'week', 'employee': False, 'department': False}
            
            # Get the dashboard data
            dashboard_data = self.get_dashboard_data(
                date_range=filters.get('dateRange', 'week'),
                employee_id=filters.get('employee', False),
                department_id=filters.get('department', False)
            )
            
            if format == 'pdf':
                # Generate PDF report
                report = request.env.ref('day_plan_work_report_ai.action_report_day_plan_dashboard')
                return report.with_context(dashboard_data=dashboard_data).report_action(None)
            elif format == 'xlsx':
                # Generate Excel report
                return request.make_response(
                    self._generate_excel(dashboard_data),
                    headers=[
                        ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                        ('Content-Disposition', 'attachment; filename=dashboard_report.xlsx;')
                    ]
                )
            elif format == 'csv':
                # Generate CSV report
                return request.make_response(
                    self._generate_csv(dashboard_data),
                    headers=[
                        ('Content-Type', 'text/csv'),
                        ('Content-Disposition', 'attachment; filename=dashboard_report.csv;')
                    ]
                )
            else:
                return request.not_found()
        except Exception as e:
            _logger.exception("Error exporting dashboard data: %s", str(e))
            return request.not_found()
    
    def _generate_excel(self, dashboard_data):
        """Generate Excel file with dashboard data"""
        # This is a stub - in a real implementation, we'd use xlsxwriter
        # to generate a proper Excel file with charts and formatted data
        return b"Excel export placeholder"
    
    def _generate_csv(self, dashboard_data):
        """Generate CSV file with dashboard data"""
        # This is a stub - in a real implementation, we'd properly format
        # the data into CSV rows and columns
        return b"CSV export placeholder"
