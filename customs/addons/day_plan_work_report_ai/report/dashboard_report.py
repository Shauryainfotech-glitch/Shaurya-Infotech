import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class DashboardReport(models.AbstractModel):
    _name = 'report.day_plan_work_report_ai.report_dashboard'
    _description = 'Dashboard Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Prepare data for dashboard report"""
        try:
            # Get dashboard records
            dashboards = self.env['day.plan.dashboard'].browse(docids)
            if not dashboards:
                # Create a default dashboard if none exists
                dashboard = self.env['day.plan.dashboard'].create({
                    'name': 'Dashboard Report'
                })
                dashboards = dashboard

            # Get dashboard data for each record
            report_data = []
            for dashboard in dashboards:
                dashboard_data = dashboard._compute_dashboard_data()

                # Get related plans and tasks
                plans = self.env['day.plan'].search([
                    ('date', '>=', dashboard.date_from),
                    ('date', '<=', dashboard.date_to)
                ])

                tasks = self.env['day.plan.task'].search([
                    ('day_plan_id', 'in', plans.ids)
                ])

                # Get AI analyses
                analyses = self.env['ai.analysis'].search([
                    ('day_plan_id', 'in', plans.ids)
                ])

                report_data.append({
                    'dashboard': dashboard,
                    'plans': plans,
                    'tasks': tasks,
                    'analyses': analyses,
                    'kpis': {
                        'total_plans': dashboard.total_plans,
                        'completion_rate': dashboard.completion_rate,
                        'avg_productivity': dashboard.avg_productivity,
                    }
                })

            return {
                'doc_ids': docids,
                'doc_model': 'day.plan.dashboard',
                'docs': dashboards,
                'data': data,
                'report_data': report_data,
                'current_date': self.env.context.get('tz') and \
                                self.env['res.users'].browse(self.env.uid).partner_id.tz or 'UTC'
            }

        except Exception as e:
            _logger.error("Error preparing dashboard report data: %s", str(e))
            return {
                'doc_ids': docids,
                'doc_model': 'day.plan.dashboard',
                'docs': self.env['day.plan.dashboard'],
                'data': data,
                'error': str(e)
            }