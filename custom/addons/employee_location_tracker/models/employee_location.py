from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
import json
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class EmployeeLocation(models.Model):
    _name = 'hr.employee.location'
    _description = 'Employee Location Tracking'
    _order = 'timestamp desc'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True,
        index=True
    )
    timestamp = fields.Datetime(
        string='Timestamp',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        index=True
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )

    # Location Fields
    latitude = fields.Float(
        string='Latitude',
        required=True,
        digits=(10, 6),
        help="GPS Latitude coordinate"
    )
    longitude = fields.Float(
        string='Longitude',
        required=True,
        digits=(10, 6),
        help="GPS Longitude coordinate"
    )
    accuracy = fields.Float(
        string='GPS Accuracy (m)',
        help="Location accuracy in meters"
    )
    altitude = fields.Float(
        string='Altitude (m)',
        help="Altitude in meters"
    )
    speed = fields.Float(
        string='Speed (km/h)',
        help="Speed in kilometers per hour"
    )
    heading = fields.Float(
        string='Heading (degrees)',
        help="Direction of movement in degrees"
    )
    address = fields.Text(
        string='Address',
        help="Reverse geocoded address"
    )

    # Status and Validation
    location_type = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('work_location', 'Work Location'),
        ('break_location', 'Break Location'),
        ('travel', 'Travel'),
        ('client_visit', 'Client Visit'),
        ('meeting', 'Meeting Location'),
        ('home', 'Home Office'),
        ('other', 'Other')
    ], string='Location Type', default='work_location', tracking=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('rejected', 'Rejected'),
        ('anomaly', 'Anomaly Detected')
    ], string='Status', default='draft', tracking=True)

    is_valid = fields.Boolean(
        string='Valid Location',
        default=True,
        help="Whether this location is considered valid"
    )
    validation_notes = fields.Text(
        string='Validation Notes',
        help="Notes about location validation"
    )

    # Geofence Information
    geofence_id = fields.Many2one(
        'hr.location.geofence',
        string='Associated Geofence',
        help="Geofence area this location belongs to"
    )
    inside_geofence = fields.Boolean(
        string='Inside Geofence',
        compute='_compute_inside_geofence',
        store=True
    )
    geofence_entry = fields.Boolean(
        string='Geofence Entry',
        help="Marks entry into a geofence"
    )
    geofence_exit = fields.Boolean(
        string='Geofence Exit',
        help="Marks exit from a geofence"
    )

    # AI Analysis Fields
    ai_confidence_score = fields.Float(
        string='AI Confidence Score',
        help="AI confidence in location accuracy (0-1)",
        digits=(3, 2)
    )
    anomaly_detected = fields.Boolean(
        string='Anomaly Detected',
        help="AI detected unusual location pattern"
    )
    anomaly_details = fields.Text(
        string='Anomaly Details',
        help="Details about detected anomalies"
    )
    behavior_pattern = fields.Selection([
        ('normal', 'Normal Pattern'),
        ('commuting', 'Commuting Pattern'),
        ('traveling', 'Traveling Pattern'),
        ('working_from_home', 'Working from Home'),
        ('unusual', 'Unusual Pattern'),
        ('suspicious', 'Suspicious Pattern'),
        ('unknown', 'Unknown Pattern')
    ], string='Behavior Pattern', default='normal')

    # Weather and Environmental Data
    weather_condition = fields.Char(
        string='Weather Condition',
        help="Weather condition at location"
    )
    temperature = fields.Float(
        string='Temperature (°C)',
        help="Temperature at location"
    )

    # Technical Fields
    device_info = fields.Text(
        string='Device Information',
        help="Device and browser information"
    )
    ip_address = fields.Char(
        string='IP Address',
        help="Device IP address"
    )
    battery_level = fields.Integer(
        string='Battery Level (%)',
        help="Device battery percentage"
    )
    network_type = fields.Selection([
        ('wifi', 'WiFi'),
        ('cellular', 'Cellular'),
        ('unknown', 'Unknown')
    ], string='Network Type')

    # Computed Fields
    distance_from_last = fields.Float(
        string='Distance from Last (km)',
        compute='_compute_distance_from_last',
        store=True,
        help="Distance from previous location"
    )
    time_since_last = fields.Float(
        string='Time Since Last (hours)',
        compute='_compute_time_since_last',
        store=True,
        help="Time elapsed since last location"
    )

    # Company and Security
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('employee_id', 'timestamp', 'location_type')
    def _compute_display_name(self):
        for record in self:
            if record.employee_id and record.timestamp:
                record.display_name = f"{record.employee_id.name} - {record.timestamp.strftime('%Y-%m-%d %H:%M')} - {record.location_type}"
            else:
                record.display_name = "New Location"

    @api.depends('latitude', 'longitude', 'geofence_id')
    def _compute_inside_geofence(self):
        for record in self:
            if record.geofence_id and record.latitude and record.longitude:
                record.inside_geofence = record.geofence_id._is_point_inside(
                    record.latitude, record.longitude
                )
            else:
                record.inside_geofence = False

    @api.depends('employee_id', 'timestamp')
    def _compute_distance_from_last(self):
        for record in self:
            if record.employee_id and record.timestamp:
                previous_location = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('timestamp', '<', record.timestamp),
                    ('id', '!=', record.id)
                ], order='timestamp desc', limit=1)

                if previous_location:
                    record.distance_from_last = record._calculate_distance(
                        previous_location.latitude, previous_location.longitude,
                        record.latitude, record.longitude
                    ) / 1000  # Convert to km
                else:
                    record.distance_from_last = 0.0
            else:
                record.distance_from_last = 0.0

    @api.depends('employee_id', 'timestamp')
    def _compute_time_since_last(self):
        for record in self:
            if record.employee_id and record.timestamp:
                previous_location = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('timestamp', '<', record.timestamp),
                    ('id', '!=', record.id)
                ], order='timestamp desc', limit=1)

                if previous_location:
                    time_diff = record.timestamp - previous_location.timestamp
                    record.time_since_last = time_diff.total_seconds() / 3600  # Convert to hours
                else:
                    record.time_since_last = 0.0
            else:
                record.time_since_last = 0.0

    @api.constrains('latitude', 'longitude')
    def _check_coordinates(self):
        for record in self:
            if not (-90 <= record.latitude <= 90):
                raise ValidationError("Latitude must be between -90 and 90 degrees")
            if not (-180 <= record.longitude <= 180):
                raise ValidationError("Longitude must be between -180 and 180 degrees")

    @api.constrains('accuracy')
    def _check_accuracy(self):
        for record in self:
            if record.accuracy and record.accuracy < 0:
                raise ValidationError("GPS accuracy cannot be negative")

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to add automation logic"""
        records = super().create(vals_list)
        
        for record in records:
            # Auto-validate high confidence locations
            if (record.ai_confidence_score and record.ai_confidence_score > 0.9 and 
                not record.anomaly_detected):
                record.write({
                    'status': 'validated',
                    'is_valid': True,
                    'validation_notes': 'Auto-validated: High AI confidence score'
                })
                _logger.info(f"Auto-validated location {record.id} for {record.employee_id.name}")
            
            # Flag anomalies for review
            if record.anomaly_detected and record.status == 'draft':
                record.write({
                    'status': 'anomaly',
                    'validation_notes': 'Flagged for review: Anomaly detected by AI'
                })
                record._send_anomaly_notification()
                _logger.warning(f"Anomaly flagged for location {record.id} - {record.employee_id.name}")
            
            # Auto-create attendance from geofence
            if (record.geofence_id and 
                record.geofence_id.auto_attendance and 
                record.inside_geofence):
                record._auto_create_attendance()
        
        return records

    def write(self, vals):
        """Override write to handle status changes"""
        result = super().write(vals)
        
        # Check for anomaly detection changes
        if 'anomaly_detected' in vals and vals['anomaly_detected']:
            for record in self:
                if record.status == 'draft':
                    record.write({
                        'status': 'anomaly',
                        'validation_notes': 'Flagged for review: Anomaly detected by AI'
                    })
                    record._send_anomaly_notification()
        
        return result

    def _auto_create_attendance(self):
        """Auto-create attendance record based on geofence entry"""
        self.ensure_one()
        
        try:
            existing_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', self.employee_id.id), 
                ('check_out', '=', False)
            ], limit=1)

            if not existing_attendance and self.location_type == 'check_in':
                self.env['hr.attendance'].create({
                    'employee_id': self.employee_id.id,
                    'check_in': self.timestamp,
                })
                _logger.info(f"Auto check-in created for {self.employee_id.name} at {self.timestamp}")
                
            elif existing_attendance and self.location_type == 'check_out':
                existing_attendance.write({
                    'check_out': self.timestamp
                })
                _logger.info(f"Auto check-out created for {self.employee_id.name} at {self.timestamp}")
                
        except Exception as e:
            _logger.error(f"Error creating auto-attendance for {self.employee_id.name}: {str(e)}")

    def _send_anomaly_notification(self):
        """Send notification when anomaly is detected"""
        try:
            message = f"Location anomaly detected for {self.employee_id.name} at {self.timestamp}"

            # Send message to HR managers
            managers = self.env['res.users'].search([
                ('groups_id', 'in', [self.env.ref('employee_location_tracker.group_location_manager').id])
            ])

            for manager in managers:
                if manager.partner_id:
                    self.message_post(
                        body=message,
                        partner_ids=[manager.partner_id.id],
                        message_type='notification'
                    )
        except Exception as e:
            _logger.error(f"Error sending anomaly notification: {str(e)}")

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        import math
        R = 6371000  # Earth's radius in meters

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def action_validate_location(self):
        """Validate location using AI analysis"""
        self.ensure_one()
        try:
            ai_service = self.env['hr.location.ai.analysis']
            result = ai_service.analyze_location(self)

            self.write({
                'ai_confidence_score': result.get('confidence', 0.0),
                'anomaly_detected': result.get('anomaly', False),
                'anomaly_details': json.dumps(result.get('anomaly_details', [])),
                'behavior_pattern': result.get('pattern', 'unknown'),
                'is_valid': result.get('is_valid', True),
                'validation_notes': result.get('notes', ''),
                'status': 'anomaly' if result.get('anomaly', False) else 'validated'
            })

            # Send notification if anomaly detected
            if result.get('anomaly', False):
                self._send_anomaly_notification()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Location validated successfully. Confidence: {result.get("confidence", 0):.2f}',
                    'type': 'success' if not result.get('anomaly', False) else 'warning',
                }
            }
        except Exception as e:
            _logger.error(f"Location validation failed: {str(e)}")
            raise UserError(f"Validation failed: {str(e)}")

    def action_reject_location(self):
        """Reject location as invalid"""
        self.ensure_one()
        self.write({
            'status': 'rejected',
            'is_valid': False,
            'validation_notes': 'Location manually rejected'
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Location rejected successfully',
                'type': 'info',
            }
        }

    def action_show_on_map(self):
        """Show location on map"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Location on Map',
            'res_model': 'hr.employee.location',
            'view_mode': 'map',
            'res_id': self.id,
            'target': 'new',
        }

    @api.model
    def create_location_from_api(self, vals):
        """Create location from API call with additional validations"""
        # Add reverse geocoding if address not provided
        if not vals.get('address') and vals.get('latitude') and vals.get('longitude'):
            vals['address'] = self._reverse_geocode(vals['latitude'], vals['longitude'])

        # Auto-detect geofence
        if vals.get('latitude') and vals.get('longitude'):
            geofence = self._find_geofence(vals['latitude'], vals['longitude'])
            if geofence:
                vals['geofence_id'] = geofence.id

        location = self.create(vals)

        # Trigger AI analysis asynchronously (if available)
        try:
            location.action_validate_location()
        except Exception as e:
            _logger.warning(f"AI analysis failed for location {location.id}: {str(e)}")

        return location

    def _reverse_geocode(self, latitude, longitude):
        """Get address from coordinates (placeholder - integrate with mapping service)"""
        # This would integrate with Google Maps, OpenStreetMap, etc.
        return f"Location: {latitude:.4f}, {longitude:.4f}"

    def _find_geofence(self, latitude, longitude):
        """Find geofence containing the given coordinates"""
        geofences = self.env['hr.location.geofence'].search([
            ('active', '=', True),
            ('company_id', '=', self.env.company.id)
        ])

        for geofence in geofences:
            if geofence._is_point_inside(latitude, longitude):
                return geofence

        return None