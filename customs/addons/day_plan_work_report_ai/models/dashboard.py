# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import datetime
import logging
from collections import defaultdict
from datetime import timedelta
import base64

_logger = logging.getLogger(__name__)

class DayPlanDashboard(models.Model):
    _name = 'day.plan.dashboard.clean'
    _description = 'Day Plan Dashboard'
    _table = 'day_plan_dashboard_clean'
    _rec_name = 'name'

    def init(self):
        """Initialize database - simplified to avoid migration issues"""
        super(DayPlanDashboard, self).init()
        try:
            # Drop any conflicting objects if they exist
            self.env.cr.execute("DROP VIEW IF EXISTS day_plan_dashboard CASCADE")
            _logger.info("Cleaned up any existing day_plan_dashboard view if it existed")
        except Exception as e:
            _logger.error("Error handling database objects: %s", str(e), exc_info=True)

    name = fields.Char(string="Name", readonly=True, default="Dashboard")

    # KPI fields
    total_plans = fields.Integer(string="Total Plans", compute="_compute_dashboard_data", store=False)
    plans_today = fields.Integer(string="Plans Today", compute="_compute_dashboard_data", store=False)
    completed_plans = fields.Integer(string="Completed Plans", compute="_compute_dashboard_data", store=False)
    pending_tasks = fields.Integer(string="Pending Tasks", compute="_compute_dashboard_data", store=False)
    productivity_score = fields.Float(string="Productivity Score", compute="_compute_dashboard_data", store=False)
    efficiency_rating = fields.Float(string="Efficiency Rating", compute="_compute_dashboard_data", store=False)
    wellbeing_assessment = fields.Float(string="Wellbeing Score", compute="_compute_dashboard_data", store=False)
    plans_change = fields.Float(string="Plans Change %", compute="_compute_dashboard_data", store=False)
    tasks_change = fields.Float(string="Tasks Change %", compute="_compute_dashboard_data", store=False)
    completion_rate = fields.Float(string="Completion Rate", compute="_compute_dashboard_data", store=False)
    avg_productivity = fields.Float(string="Avg Productivity", compute="_compute_dashboard_data", store=False)
    tasks_due_today = fields.Integer(string="Tasks Due Today", compute="_compute_dashboard_data", store=False)
    overdue_tasks = fields.Integer(string="Overdue Tasks", compute="_compute_dashboard_data", store=False)
    attention_items = fields.Integer(string="Attention Items", compute="_compute_dashboard_data", store=False)

    # Chart data fields
    chart_data = fields.Text(string="Chart Data", compute="_compute_dashboard_data", store=False)
    pie_chart_data = fields.Text(string="Pie Chart Data", compute="_compute_dashboard_data", store=False)
    line_chart_data = fields.Text(string="Line Chart Data", compute="_compute_dashboard_data", store=False)
    radar_chart_data = fields.Text(string="Radar Chart Data", compute="_compute_dashboard_data", store=False)

    @api.model
    def _ensure_dashboard_exists(self):
        """Ensure dashboard exists - called by client action before loading dashboard"""
        try:
            _logger.info("Ensuring dashboard exists")
            dashboard = self.search([], limit=1)
            if not dashboard:
                # Initialize the dashboard if it doesn't exist
                _logger.info("Creating new dashboard record")
                dashboard = self.create({
                    'name': 'Dashboard'
                })
                self.env.cr.commit()  # Commit the transaction to ensure the record is saved
                _logger.info("New dashboard created with ID: %s", dashboard.id)
            return True
        except Exception as e:
            _logger.error("Error in _ensure_dashboard_exists: %s", str(e), exc_info=True)
            # Return True anyway to avoid blocking the UI
            return True

    @api.model
    def _get_default_dashboard(self):
        """Get or create a default dashboard record."""
        try:
            _logger.info("Getting default dashboard")
            dashboard = self.search([], limit=1)
            _logger.info("Dashboard found: %s", dashboard)
            if not dashboard:
                # Initialize the dashboard if it doesn't exist
                _logger.info("Creating new dashboard record")
                dashboard = self.create({
                    'name': 'Dashboard'
                })
                self.env.cr.commit()  # Commit transaction to ensure record is saved
                _logger.info("New dashboard created with ID: %s", dashboard.id)
            return dashboard
        except Exception as e:
            _logger.error("Error in _get_default_dashboard: %s", str(e), exc_info=True)
            # Create an empty dashboard record to return instead of raising an error
            return self.new({'name': 'Dashboard (Temporary)'})
            # This returns a non-persistent record that will prevent client-side errors

    @api.model
    def action_refresh_dashboard(self):
        """Refresh the dashboard by forcing recomputation of fields"""
        dashboard = self._get_default_dashboard()
        dashboard.invalidate_recordset(['total_plans', 'plans_today', 'completed_plans',
                                        'pending_tasks', 'productivity_score', 'chart_data'])
        return {
            'type': 'ir.actions.client',
            'tag': 'day_plan_work_report_ai.dashboard_action',
            'params': {'message': 'Dashboard refreshed successfully!'}
        }

    @api.model
    def action_print_dashboard(self):
        """Print the dashboard as PDF using direct reportlab generation"""
        self.ensure_one()
        try:
            _logger.info("Starting dashboard PDF generation process")
            # Get a report model reference
            report_model = self.env['ir.actions.report']

            # Generate PDF from reportlab
            _logger.info("Generating dashboard PDF report for dashboard ID: %s", self.id)
            pdf_content, pdf_format = report_model.render_reportlab_pdf(self.ids, {})

            # Create an attachment for the report
            filename = f"Dashboard_Report_{fields.Date.today()}.pdf"
            _logger.info("Dashboard PDF generated successfully: %s", filename)

            return {
                'type': 'ir.actions.report.download',
                'data': {
                    'model': 'day.plan.dashboard.clean',  # Updated to use new model name
                    'options': json.dumps({}),
                    'output_format': 'pdf',
                    'filename': filename,
                    'report_name': 'Dashboard Report',
                    'report_content': base64.b64encode(pdf_content).decode('utf-8'),
                },
            }
        except Exception as e:
            _logger.error("Error printing dashboard: %s", str(e), exc_info=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Failed to print dashboard: %s') % str(e),
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def _set_default_values(self, dashboard):
        """Set default values for dashboard when no data is available"""
        # Use sample data for charts
        chart_data_json = {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'datasets': [
                {
                    'label': 'Completed Tasks',
                    'data': [5, 7, 4, 6, 8, 3, 5],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Planned Tasks',
                    'data': [8, 10, 6, 9, 12, 7, 8],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                }
            ]
        }

        dashboard.total_plans = 0
        dashboard.plans_change = 0
        dashboard.completion_rate = 0
        dashboard.avg_productivity = 0
        dashboard.attention_items = 0
        dashboard.chart_data = json.dumps(chart_data_json)
        dashboard.pie_chart_data = json.dumps({"labels": [], "datasets": []})

    def _compute_dashboard_data(self):
        """Compute all dashboard metrics and chart data"""
        for dashboard in self:
            try:
                _logger.info("Computing dashboard data for dashboard ID: %s", dashboard.id)
                
                # Set default values first as fallback
                self._set_default_values(dashboard)
                
                # Check if required models exist
                required_models = ['day.plan', 'day.plan.task', 'ai.analysis']
                missing_models = []
                for model in required_models:
                    try:
                        if not self.env['ir.model'].search([('model', '=', model)], limit=1):
                            missing_models.append(model)
                    except Exception as e:
                        _logger.error("Error checking model %s: %s", model, str(e))
                        missing_models.append(model)
                
                if missing_models:
                    _logger.warning("Missing required models: %s - using default values", missing_models)
                    return

                # Get data from relevant models - with error handling
                day_plans = self.env['day.plan'].search([])
                day_plan_tasks = self.env['day.plan.task'].search([])

                # If no data, set default values
                if not day_plans and not day_plan_tasks:
                    _logger.info("No plan data found, using default values")
                    self._set_default_values(dashboard)
                    continue

                # Calculate KPIs
                dashboard.total_plans = len(day_plans)

                # Calculate plans change percentage (compare to previous week)
                today = fields.Date.today()
                week_ago = today - timedelta(days=7)
                plans_this_week = self.env['day.plan'].search_count([('date', '>=', today - timedelta(days=7)), ('date', '<=', today)])
                plans_prev_week = self.env['day.plan'].search_count([('date', '>=', week_ago - timedelta(days=7)), ('date', '<', week_ago)])

                if plans_prev_week:
                    dashboard.plans_change = ((plans_this_week - plans_prev_week) / plans_prev_week) * 100
                else:
                    dashboard.plans_change = 0

                # Calculate completion rate
                total_tasks = len(day_plan_tasks)
                completed_tasks = self.env['day.plan.task'].search_count([('state', '=', 'done')])
                dashboard.completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks else 0

                # Calculate productivity score
                productivity_scores = []
                for plan in day_plans:
                    ai_analysis = self.env['ai.analysis'].search([('day_plan_id', '=', plan.id)], limit=1)
                    if ai_analysis and hasattr(ai_analysis, 'productivity_score'):
                        productivity_scores.append(ai_analysis.productivity_score)

                dashboard.productivity_score = sum(productivity_scores) / len(productivity_scores) if productivity_scores else 0

                # Calculate attention items
                overdue_tasks = self.env['day.plan.task'].search_count([('deadline', '<', fields.Date.today()), ('state', '!=', 'done')])
                low_productivity_plans = self.env['ai.analysis'].search_count([('productivity_score', '<', 3)])
                dashboard.attention_items = overdue_tasks + low_productivity_plans

                # Generate chart data
                self._generate_chart_data(dashboard)

            except Exception as e:
                _logger.error("Error computing dashboard data: %s", str(e), exc_info=True)
                self._set_default_values(dashboard)

    def _generate_chart_data(self, dashboard):
        """Generate chart data for the dashboard charts"""
        try:
            today = fields.Date.today()
            date_labels = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
            date_values = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

            chart_data = {
                'labels': date_labels,
                'datasets': [
                    {
                        'label': 'Completed Tasks',
                        'data': [0, 0, 0, 0, 0, 0, 0],
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'borderColor': 'rgba(75, 192, 192, 1)',
                        'borderWidth': 1
                    },
                    {
                        'label': 'Planned Tasks',
                        'data': [0, 0, 0, 0, 0, 0, 0],
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'borderColor': 'rgba(54, 162, 235, 1)',
                        'borderWidth': 1
                    }
                ]
            }

            pie_data = {
                'labels': ['No Data'],
                'datasets': [{
                    'data': [100],
                    'backgroundColor': ['rgba(200, 200, 200, 0.8)']
                }]
            }

            line_chart_data = {
                'labels': date_labels,
                'datasets': [{
                    'label': 'Productivity Trend',
                    'data': [0, 0, 0, 0, 0, 0, 0],
                    'fill': False,
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'tension': 0.1
                }]
            }

            # Get task data by day
            planned_tasks_data = []
            completed_tasks_data = []

            for date in date_values:
                planned = self.env['day.plan.task'].search_count([('date', '=', date)])
                planned_tasks_data.append(planned)

                completed = self.env['day.plan.task'].search_count([('date', '=', date), ('state', '=', 'done')])
                completed_tasks_data.append(completed)

            if any(planned_tasks_data) or any(completed_tasks_data):
                chart_data['datasets'][0]['data'] = completed_tasks_data
                chart_data['datasets'][1]['data'] = planned_tasks_data

            task_states = self.env['day.plan.task'].read_group([('state', '!=', False)], ['state'], ['state'])
            if task_states:
                pie_data = {
                    'labels': [state['state'] for state in task_states],
                    'datasets': [{
                        'data': [state['state_count'] for state in task_states],
                        'backgroundColor': [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(153, 102, 255, 0.8)'
                        ]
                    }]
                }

            productivity_data = self.env['ai.analysis'].search_read(
                [('create_date', '>=', date_values[0])],
                ['create_date', 'productivity_score'],
                order='create_date asc'
            )

            if productivity_data:
                productivity_by_day = defaultdict(list)
                for record in productivity_data:
                    day = record['create_date'].date().strftime('%a')
                    if 'productivity_score' in record and record['productivity_score']:
                        productivity_by_day[day].append(record['productivity_score'])

                line_data = []
                for day in date_labels:
                    scores = productivity_by_day.get(day, [])
                    avg_score = sum(scores) / len(scores) if scores else 0
                    line_data.append(avg_score)

                if any(line_data):
                    line_chart_data['datasets'][0]['data'] = line_data

            dashboard.chart_data = json.dumps(chart_data)
            dashboard.pie_chart_data = json.dumps(pie_data)
            dashboard.line_chart_data = json.dumps(line_chart_data)
            dashboard.radar_chart_data = json.dumps({
                'labels': ['Planning', 'Execution', 'Completion', 'Quality', 'Timeliness'],
                'datasets': [{
                    'label': 'Performance',
                    'data': [3, 4, 3.5, 4.2, 3.8],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                }]
            })

        except Exception as e:
            _logger.error("Error generating chart data: %s", str(e), exc_info=True)
            # Set default chart data if there are issues
            dashboard.chart_data = json.dumps({'labels': [], 'datasets': []})
            dashboard.pie_chart_data = json.dumps({'labels': [], 'datasets': []})
            dashboard.line_chart_data = json.dumps({'labels': [], 'datasets': []})
            dashboard.radar_chart_data = json.dumps({'labels': [], 'datasets': []})
