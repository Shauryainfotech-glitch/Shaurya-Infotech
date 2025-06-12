import logging
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DayPlanReportGenerator(models.TransientModel):
    _name = 'day.plan.report.generator'
    _description = 'Day Plan Report Generator'

    report_type = fields.Selection([
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report')
    ], string="Report Type", default='weekly', required=True)

    date_from = fields.Date(string="Date From", required=True,
                            default=lambda self: fields.Date.today() - timedelta(days=7))
    date_to = fields.Date(string="Date To", required=True, default=fields.Date.today)
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  default=lambda self: self.env.user.employee_id)
    department_id = fields.Many2one('hr.department', string="Department")

    def action_generate_report(self):
        """Generate the report"""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to)
        ]

        if self.employee_id:
            domain.append(('employee_id', '=', self.employee_id.id))
        elif self.department_id:
            employees = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)])
            domain.append(('employee_id', 'in', employees.ids))

        plans = self.env['day.plan'].search(domain)

        return {
            'name': _('Day Plans Report'),
            'view_mode': 'tree,form',
            'res_model': 'day.plan',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', plans.ids)],
            'target': 'current'
        }