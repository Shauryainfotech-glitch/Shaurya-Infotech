from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime, timedelta  # Added timedelta import

_logger = logging.getLogger(__name__)


class LocationTrackingAPI(http.Controller):

    @http.route('/api/location/submit', type='json', auth='user', methods=['POST'], csrf=False)
    def submit_location(self, **kw):
        """API endpoint to submit location data"""
        try:
            data = request.jsonrequest

            # Validate required fields
            required_fields = ['employee_id', 'latitude', 'longitude']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}

            # Get employee
            employee = request.env['hr.employee'].browse(data['employee_id'])
            if not employee.exists():
                return {'error': 'Invalid employee ID'}

            # Prepare location data
            location_data = {
                'employee_id': data['employee_id'],
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'accuracy': data.get('accuracy'),
                'altitude': data.get('altitude'),
                'speed': data.get('speed'),
                'heading': data.get('heading'),
                'location_type': data.get('location_type', 'work_location'),
                'device_info': data.get('device_info'),
                'battery_level': data.get('battery_level'),
                'network_type': data.get('network_type'),
                'ip_address': request.httprequest.remote_addr,
                'timestamp': datetime.now()
            }

            # Create location record
            location = request.env['hr.employee.location'].create_location_from_api(location_data)

            return {
                'success': True,
                'location_id': location.id,
                'message': 'Location submitted successfully'
            }

        except Exception as e:
            _logger.error(f"Error submitting location: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/location/bulk_submit', type='json', auth='user', methods=['POST'], csrf=False)
    def bulk_submit_locations(self, **kw):
        """API endpoint to submit multiple location records"""
        try:
            data = request.jsonrequest
            locations_data = data.get('locations', [])

            if not locations_data:
                return {'error': 'No location data provided'}

            created_locations = []
            errors = []

            for loc_data in locations_data:
                try:
                    # Validate required fields
                    required_fields = ['employee_id', 'latitude', 'longitude']
                    for field in required_fields:
                        if field not in loc_data:
                            errors.append(f'Missing required field: {field} in location data')
                            continue

                    # Prepare location data
                    location_data = {
                        'employee_id': loc_data['employee_id'],
                        'latitude': loc_data['latitude'],
                        'longitude': loc_data['longitude'],
                        'accuracy': loc_data.get('accuracy'),
                        'altitude': loc_data.get('altitude'),
                        'speed': loc_data.get('speed'),
                        'heading': loc_data.get('heading'),
                        'location_type': loc_data.get('location_type', 'work_location'),
                        'device_info': loc_data.get('device_info'),
                        'battery_level': loc_data.get('battery_level'),
                        'network_type': loc_data.get('network_type'),
                        'ip_address': request.httprequest.remote_addr,
                        'timestamp': datetime.fromisoformat(loc_data.get('timestamp', datetime.now().isoformat()))
                    }

                    # Create location record
                    location = request.env['hr.employee.location'].create_location_from_api(location_data)
                    created_locations.append(location.id)

                except Exception as e:
                    errors.append(f'Error creating location: {str(e)}')

            return {
                'success': True,
                'created_count': len(created_locations),
                'created_locations': created_locations,
                'errors': errors
            }

        except Exception as e:
            _logger.error(f"Error in bulk location submission: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/location/employee/<int:employee_id>', type='json', auth='user', methods=['GET'])
    def get_employee_locations(self, employee_id, **kw):
        """Get locations for a specific employee"""
        try:
            # Get parameters
            limit = kw.get('limit', 100)
            date_from = kw.get('date_from')
            date_to = kw.get('date_to')

            # Build domain
            domain = [('employee_id', '=', employee_id)]
            if date_from:
                domain.append(('timestamp', '>=', date_from))
            if date_to:
                domain.append(('timestamp', '<=', date_to))

            locations = request.env['hr.employee.location'].search(
                domain, order='timestamp desc', limit=limit
            )

            location_data = []
            for location in locations:
                location_data.append({
                    'id': location.id,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'accuracy': location.accuracy,
                    'timestamp': location.timestamp.isoformat(),
                    'location_type': location.location_type,
                    'address': location.address,
                    'geofence_id': location.geofence_id.id if location.geofence_id else None,
                    'geofence_name': location.geofence_id.name if location.geofence_id else None,
                    'inside_geofence': location.inside_geofence,
                    'ai_confidence_score': location.ai_confidence_score,
                    'anomaly_detected': location.anomaly_detected,
                    'status': location.status
                })

            return {
                'success': True,
                'locations': location_data,
                'count': len(location_data)
            }

        except Exception as e:
            _logger.error(f"Error getting employee locations: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/geofence/check', type='json', auth='user', methods=['POST'])
    def check_geofence(self, **kw):
        """Check if coordinates are within any geofence"""
        try:
            data = request.jsonrequest
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            if not latitude or not longitude:
                return {'error': 'Latitude and longitude are required'}

            geofences = request.env['hr.location.geofence'].search([
                ('active', '=', True),
                ('company_id', '=', request.env.company.id)
            ])

            inside_geofences = []
            for geofence in geofences:
                if geofence._is_point_inside(latitude, longitude):
                    inside_geofences.append({
                        'id': geofence.id,
                        'name': geofence.name,
                        'type': geofence.geofence_type,
                        'auto_attendance': geofence.auto_attendance,
                        'alert_on_entry': geofence.alert_on_entry,
                        'alert_on_exit': geofence.alert_on_exit
                    })

            return {
                'success': True,
                'inside_geofences': inside_geofences,
                'count': len(inside_geofences)
            }

        except Exception as e:
            _logger.error(f"Error checking geofence: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/analytics/summary', type='json', auth='user', methods=['GET'])
    def get_analytics_summary(self, **kw):
        """Get analytics summary data"""
        try:
            date_from = kw.get('date_from', (datetime.now() - timedelta(days=30)).isoformat())
            date_to = kw.get('date_to', datetime.now().isoformat())
            employee_ids = kw.get('employee_ids', [])

            domain = [
                ('timestamp', '>=', date_from),
                ('timestamp', '<=', date_to),
                ('company_id', '=', request.env.company.id)
            ]

            if employee_ids:
                domain.append(('employee_id', 'in', employee_ids))

            locations = request.env['hr.employee.location'].search(domain)

            # Calculate summary statistics
            summary = {
                'total_locations': len(locations),
                'unique_employees': len(locations.mapped('employee_id')),
                'total_distance_km': sum(locations.mapped('distance_from_last')),
                'avg_accuracy': sum(locations.mapped('accuracy')) / len(locations) if locations else 0,
                'anomalies_detected': len(locations.filtered('anomaly_detected')),
                'high_confidence_locations': len(locations.filtered(lambda l: l.ai_confidence_score > 0.8)),
                'geofence_entries': len(locations.filtered('geofence_entry')),
                'date_range': {
                    'from': date_from,
                    'to': date_to
                }
            }

            # Location types distribution
            type_distribution = {}
            for location in locations:
                loc_type = location.location_type
                type_distribution[loc_type] = type_distribution.get(loc_type, 0) + 1

            summary['location_types'] = type_distribution

            return {
                'success': True,
                'summary': summary
            }

        except Exception as e:
            _logger.error(f"Error getting analytics summary: {str(e)}")
            return {'error': str(e)}

    @http.route('/api/tracking/settings/<int:employee_id>', type='json', auth='user', methods=['GET', 'POST'])
    def tracking_settings(self, employee_id, **kw):
        """Get or update tracking settings for employee"""
        try:
            employee = request.env['hr.employee'].browse(employee_id)
            if not employee.exists():
                return {'error': 'Invalid employee ID'}

            settings = request.env['hr.location.tracking.settings'].search([
                ('employee_id', '=', employee_id)
            ], limit=1)

            if request.httprequest.method == 'GET':
                # Return current settings
                if settings:
                    return {
                        'success': True,
                        'settings': {
                            'tracking_enabled': settings.tracking_enabled,
                            'tracking_frequency': settings.tracking_frequency,
                            'privacy_mode': settings.privacy_mode,
                            'tracking_hours_only': settings.tracking_hours_only,
                            'work_start': settings.work_start,
                            'work_end': settings.work_end,
                            'auto_attendance': settings.auto_attendance,
                            'battery_optimization': settings.battery_optimization,
                            'min_battery_level': settings.min_battery_level
                        }
                    }
                else:
                    return {
                        'success': True,
                        'settings': {
                            'tracking_enabled': True,
                            'tracking_frequency': 'normal',
                            'privacy_mode': False,
                            'tracking_hours_only': False,
                            'work_start': 9.0,
                            'work_end': 17.0,
                            'auto_attendance': False,
                            'battery_optimization': True,
                            'min_battery_level': 15
                        }
                    }

            elif request.httprequest.method == 'POST':
                # Update settings
                data = request.jsonrequest

                if not settings:
                    settings = request.env['hr.location.tracking.settings'].create({
                        'employee_id': employee_id
                    })

                # Update fields
                update_fields = [
                    'tracking_enabled', 'tracking_frequency', 'privacy_mode',
                    'tracking_hours_only', 'work_start', 'work_end',
                    'auto_attendance', 'battery_optimization', 'min_battery_level'
                ]

                update_data = {}
                for field in update_fields:
                    if field in data:
                        update_data[field] = data[field]

                if update_data:
                    settings.write(update_data)

                return {
                    'success': True,
                    'message': 'Settings updated successfully'
                }

        except Exception as e:
            _logger.error(f"Error handling tracking settings: {str(e)}")
            return {'error': str(e)}