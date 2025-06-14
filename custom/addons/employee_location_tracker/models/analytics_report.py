from odoo import models, fields, api, tools
from datetime import datetime, timedelta
import json


class LocationAnalyticsDashboard(models.Model):
    _name = 'hr.location.analytics.dashboard'
    _description = 'Location Analytics Dashboard'

    name = fields.Char(string='Dashboard Name', required=True)
    description = fields.Text(string='Description')

    # Date Range
    date_from = fields.Date(
        string='Date From',
        default=lambda self: fields.Date.today() - timedelta(days=30)
    )
    date_to = fields.Date(
        string='Date To',
        default=fields.Date.today
    )

    # Filters
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees',
        help="Leave empty to include all employees"
    )
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments'
    )
    geofence_ids = fields.Many2many(
        'hr.location.geofence',
        string='Geofences'
    )

    # Dashboard Data (JSON fields for flexibility)
    summary_data = fields.Text(
        string='Summary Data',
        help="JSON data for summary widgets"
    )
    chart_data = fields.Text(
        string='Chart Data',
        help="JSON data for charts and graphs"
    )
    map_data = fields.Text(
        string='Map Data',
        help="JSON data for map visualizations"
    )

    # Computed Analytics
    total_employees_tracked = fields.Integer(
        string='Total Employees Tracked',
        compute='_compute_analytics'
    )
    total_locations_recorded = fields.Integer(
        string='Total Locations Recorded',
        compute='_compute_analytics'
    )
    total_distance_traveled = fields.Float(
        string='Total Distance Traveled (km)',
        compute='_compute_analytics'
    )
    avg_locations_per_employee = fields.Float(
        string='Average Locations per Employee',
        compute='_compute_analytics'
    )
    anomalies_detected = fields.Integer(
        string='Anomalies Detected',
        compute='_compute_analytics'
    )
    geofence_violations = fields.Integer(
        string='Geofence Violations',
        compute='_compute_analytics'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('date_from', 'date_to', 'employee_ids', 'department_ids')
    def _compute_analytics(self):
        for record in self:
            # Build domain for location records
            domain = [
                ('timestamp', '>=', record.date_from),
                ('timestamp', '<=', record.date_to),
                ('company_id', '=', record.company_id.id)
            ]

            if record.employee_ids:
                domain.append(('employee_id', 'in', record.employee_ids.ids))
            elif record.department_ids:
                employees = self.env['hr.employee'].search([
                    ('department_id', 'in', record.department_ids.ids)
                ])
                domain.append(('employee_id', 'in', employees.ids))

            locations = self.env['hr.employee.location'].search(domain)

            # Calculate analytics
            record.total_employees_tracked = len(locations.mapped('employee_id'))
            record.total_locations_recorded = len(locations)
            record.total_distance_traveled = sum(locations.mapped('distance_from_last'))
            record.avg_locations_per_employee = (
                record.total_locations_recorded / record.total_employees_tracked
                if record.total_employees_tracked > 0 else 0
            )
            record.anomalies_detected = len(locations.filtered('anomaly_detected'))
            record.geofence_violations = len(locations.filtered(
                lambda l: l.geofence_id and not l.inside_geofence
            ))

    def action_refresh_data(self):
        """Refresh dashboard data"""
        self.ensure_one()

        # Generate summary data
        summary = self._generate_summary_data()
        self.summary_data = json.dumps(summary)

        # Generate chart data
        charts = self._generate_chart_data()
        self.chart_data = json.dumps(charts)

        # Generate map data
        map_data = self._generate_map_data()
        self.map_data = json.dumps(map_data)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Dashboard data refreshed successfully',
                'type': 'success',
            }
        }

    def _generate_summary_data(self):
        """Generate summary statistics"""
        domain = self._get_base_domain()
        locations = self.env['hr.employee.location'].search(domain)

        return {
            'total_locations': len(locations),
            'unique_employees': len(locations.mapped('employee_id')),
            'total_distance': sum(locations.mapped('distance_from_last')),
            'avg_accuracy': sum(locations.mapped('accuracy')) / len(locations) if locations else 0,
            'anomalies': len(locations.filtered('anomaly_detected')),
            'high_confidence': len(locations.filtered(lambda l: l.ai_confidence_score > 0.8)),
            'geofence_entries': len(locations.filtered('geofence_entry')),
            'most_active_employee': self._get_most_active_employee(locations),
            'busiest_geofence': self._get_busiest_geofence(locations)
        }

    def _generate_chart_data(self):
        """Generate data for charts"""
        domain = self._get_base_domain()
        locations = self.env['hr.employee.location'].search(domain)

        # Locations by day
        daily_counts = {}
        for location in locations:
            date_key = location.timestamp.date().isoformat()
            daily_counts[date_key] = daily_counts.get(date_key, 0) + 1

        # Locations by hour
        hourly_counts = {}
        for location in locations:
            hour_key = location.timestamp.hour
            hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1

        # Employee activity
        employee_counts = {}
        for location in locations:
            emp_name = location.employee_id.name
            employee_counts[emp_name] = employee_counts.get(emp_name, 0) + 1

        # Location types
        type_counts = {}
        for location in locations:
            type_key = location.location_type
            type_counts[type_key] = type_counts.get(type_key, 0) + 1

        return {
            'daily_activity': daily_counts,
            'hourly_distribution': hourly_counts,
            'employee_activity': employee_counts,
            'location_types': type_counts,
            'accuracy_distribution': self._get_accuracy_distribution(locations),
            'anomaly_trends': self._get_anomaly_trends(locations)
        }

    def _generate_map_data(self):
        """Generate data for map visualization"""
        domain = self._get_base_domain()
        locations = self.env['hr.employee.location'].search(domain, limit=1000)  # Limit for performance

        map_points = []
        for location in locations:
            map_points.append({
                'lat': location.latitude,
                'lng': location.longitude,
                'employee': location.employee_id.name,
                'timestamp': location.timestamp.isoformat(),
                'type': location.location_type,
                'accuracy': location.accuracy,
                'anomaly': location.anomaly_detected,
                'confidence': location.ai_confidence_score
            })

        # Geofence data
        geofences = self.env['hr.location.geofence'].search([
            ('active', '=', True),
            ('company_id', '=', self.company_id.id)
        ])

        geofence_data = []
        for geofence in geofences:
            if geofence.geofence_type == 'circle':
                geofence_data.append({
                    'name': geofence.name,
                    'type': 'circle',
                    'center': [geofence.center_latitude, geofence.center_longitude],
                    'radius': geofence.radius,
                    'color': geofence.color
                })
            elif geofence.boundary_points:
                try:
                    points = json.loads(geofence.boundary_points)
                    geofence_data.append({
                        'name': geofence.name,
                        'type': 'polygon',
                        'points': points,
                        'color': geofence.color
                    })
                except json.JSONDecodeError:
                    pass

        return {
            'locations': map_points,
            'geofences': geofence_data,
            'center': self._calculate_map_center(locations),
            'zoom': 10
        }

    def _get_base_domain(self):
        """Get base domain for queries"""
        domain = [
            ('timestamp', '>=', self.date_from),
            ('timestamp', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
            ('is_valid', '=', True)
        ]

        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        elif self.department_ids:
            employees = self.env['hr.employee'].search([
                ('department_id', 'in', self.department_ids.ids)
            ])
            domain.append(('employee_id', 'in', employees.ids))

        if self.geofence_ids:
            domain.append(('geofence_id', 'in', self.geofence_ids.ids))

        return domain

    def _get_most_active_employee(self, locations):
        """Get most active employee"""
        if not locations:
            return None

        employee_counts = {}
        for location in locations:
            emp_id = location.employee_id.id
            employee_counts[emp_id] = employee_counts.get(emp_id, 0) + 1

        most_active_id = max(employee_counts, key=employee_counts.get)
        most_active_employee = self.env['hr.employee'].browse(most_active_id)

        return {
            'name': most_active_employee.name,
            'count': employee_counts[most_active_id]
        }

    def _get_busiest_geofence(self, locations):
        """Get busiest geofence"""
        geofence_locations = locations.filtered('geofence_id')
        if not geofence_locations:
            return None

        geofence_counts = {}
        for location in geofence_locations:
            gf_id = location.geofence_id.id
            geofence_counts[gf_id] = geofence_counts.get(gf_id, 0) + 1

        busiest_id = max(geofence_counts, key=geofence_counts.get)
        busiest_geofence = self.env['hr.location.geofence'].browse(busiest_id)

        return {
            'name': busiest_geofence.name,
            'count': geofence_counts[busiest_id]
        }

    def _get_accuracy_distribution(self, locations):
        """Get GPS accuracy distribution"""
        accuracy_ranges = {
            'excellent': 0,  # < 5m
            'good': 0,  # 5-20m
            'fair': 0,  # 20-100m
            'poor': 0  # > 100m
        }

        for location in locations.filtered('accuracy'):
            accuracy = location.accuracy
            if accuracy < 5:
                accuracy_ranges['excellent'] += 1
            elif accuracy < 20:
                accuracy_ranges['good'] += 1
            elif accuracy < 100:
                accuracy_ranges['fair'] += 1
            else:
                accuracy_ranges['poor'] += 1

        return accuracy_ranges

    def _get_anomaly_trends(self, locations):
        """Get anomaly trends over time"""
        anomaly_by_date = {}

        for location in locations:
            date_key = location.timestamp.date().isoformat()
            if date_key not in anomaly_by_date:
                anomaly_by_date[date_key] = {'total': 0, 'anomalies': 0}

            anomaly_by_date[date_key]['total'] += 1
            if location.anomaly_detected:
                anomaly_by_date[date_key]['anomalies'] += 1

        # Calculate anomaly rates
        anomaly_rates = {}
        for date_key, data in anomaly_by_date.items():
            anomaly_rates[date_key] = (
                data['anomalies'] / data['total'] * 100
                if data['total'] > 0 else 0
            )

        return anomaly_rates

    def _calculate_map_center(self, locations):
        """Calculate center point for map"""
        if not locations:
            return [0, 0]

        avg_lat = sum(locations.mapped('latitude')) / len(locations)
        avg_lng = sum(locations.mapped('longitude')) / len(locations)

        return [avg_lat, avg_lng]