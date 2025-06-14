from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class LocationTrackingController(http.Controller):

    @http.route('/location_tracker/dashboard', type='http', auth='user', website=True)
    def location_dashboard(self, **kw):
        """Main dashboard for location tracking"""
        employees = request.env['hr.employee'].search([
            ('company_id', '=', request.env.company.id)
        ])

        geofences = request.env['hr.location.geofence'].search([
            ('active', '=', True),
            ('company_id', '=', request.env.company.id)
        ])

        # Get recent locations
        recent_locations = request.env['hr.employee.location'].search([
            ('timestamp', '>=', fields.Datetime.now() - timedelta(hours=24)),
            ('company_id', '=', request.env.company.id)
        ], order='timestamp desc', limit=100)

        return request.render('employee_location_tracker.dashboard_template', {
            'employees': employees,
            'geofences': geofences,
            'recent_locations': recent_locations,
        })

    @http.route('/location_tracker/employee/<int:employee_id>', type='http', auth='user')
    def employee_locations(self, employee_id, **kw):
        """View locations for specific employee"""
        employee = request.env['hr.employee'].browse(employee_id)

        if not employee.exists():
            return request.not_found()

        # Get date range from parameters
        date_from = kw.get('date_from')
        date_to = kw.get('date_to')

        domain = [('employee_id', '=', employee_id)]
        if date_from:
            domain.append(('timestamp', '>=', date_from))
        if date_to:
            domain.append(('timestamp', '<=', date_to))

        locations = request.env['hr.employee.location'].search(
            domain, order='timestamp desc'
        )

        return request.render('employee_location_tracker.employee_locations_template', {
            'employee': employee,
            'locations': locations,
            'date_from': date_from,
            'date_to': date_to,
        })