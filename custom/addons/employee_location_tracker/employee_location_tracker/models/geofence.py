from odoo import models, fields, api
import math
import json
from odoo.exceptions import ValidationError


class LocationGeofence(models.Model):
    _name = 'hr.location.geofence'
    _description = 'Location Geofence'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Geofence Name', required=True, tracking=True)
    description = fields.Text(string='Description')
    code = fields.Char(string='Code', help="Unique identifier for the geofence")

    # Geofence Type
    geofence_type = fields.Selection([
        ('circle', 'Circular'),
        ('polygon', 'Polygon'),
        ('rectangle', 'Rectangle')
    ], string='Geofence Type', default='circle', required=True, tracking=True)

    # Circle Geofence
    center_latitude = fields.Float(
        string='Center Latitude',
        digits=(10, 6),
        help="Center latitude for circular geofence"
    )
    center_longitude = fields.Float(
        string='Center Longitude',
        digits=(10, 6),
        help="Center longitude for circular geofence"
    )
    radius = fields.Float(
        string='Radius (meters)',
        default=100.0,
        help="Radius in meters for circular geofence"
    )

    # Polygon/Rectangle Geofence
    boundary_points = fields.Text(
        string='Boundary Points',
        help="JSON array of lat/lng coordinates for polygon boundaries"
    )

    # Configuration
    active = fields.Boolean(string='Active', default=True, tracking=True)
    color = fields.Char(string='Color', default='#FF0000', help="Color for map display")

    # Geofence Rules
    auto_attendance = fields.Boolean(
        string='Auto Attendance',
        help="Automatically mark attendance when entering/leaving geofence"
    )
    alert_on_entry = fields.Boolean(
        string='Alert on Entry',
        help="Send notification when employee enters geofence"
    )
    alert_on_exit = fields.Boolean(
        string='Alert on Exit',
        help="Send notification when employee exits geofence"
    )
    allowed_employees = fields.Many2many(
        'hr.employee',
        string='Allowed Employees',
        help="Employees allowed in this geofence"
    )
    restricted_hours = fields.Boolean(
        string='Time Restricted',
        help="Apply time restrictions to this geofence"
    )
    start_time = fields.Float(string='Start Time', default=9.0)
    end_time = fields.Float(string='End Time', default=17.0)

    # Analytics
    entry_count = fields.Integer(
        string='Total Entries',
        compute='_compute_analytics',
        help="Total number of geofence entries"
    )
    current_occupancy = fields.Integer(
        string='Current Occupancy',
        compute='_compute_current_occupancy',
        help="Current number of employees in geofence"
    )
    avg_duration = fields.Float(
        string='Average Duration (hours)',
        compute='_compute_analytics',
        help="Average time spent in geofence"
    )
    last_entry = fields.Datetime(
        string='Last Entry',
        compute='_compute_analytics',
        help="Last time someone entered this geofence"
    )

    # Company and Security
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    @api.constrains('center_latitude', 'center_longitude')
    def _check_coordinates(self):
        for record in self:
            if record.geofence_type == 'circle':
                if not record.center_latitude or not record.center_longitude:
                    raise ValidationError("Center coordinates are required for circular geofence")
                if not (-90 <= record.center_latitude <= 90):
                    raise ValidationError("Latitude must be between -90 and 90 degrees")
                if not (-180 <= record.center_longitude <= 180):
                    raise ValidationError("Longitude must be between -180 and 180 degrees")

    @api.constrains('radius')
    def _check_radius(self):
        for record in self:
            if record.geofence_type == 'circle' and (not record.radius or record.radius <= 0):
                raise ValidationError("Radius must be greater than 0")

    @api.constrains('boundary_points')
    def _check_boundary_points(self):
        for record in self:
            if record.geofence_type in ['polygon', 'rectangle'] and record.boundary_points:
                try:
                    points = json.loads(record.boundary_points)
                    if not isinstance(points, list) or len(points) < 3:
                        raise ValidationError("At least 3 boundary points are required for polygon")

                    for point in points:
                        if not isinstance(point, dict) or 'lat' not in point or 'lng' not in point:
                            raise ValidationError("Each boundary point must have 'lat' and 'lng' keys")

                        if not (-90 <= point['lat'] <= 90):
                            raise ValidationError("Latitude must be between -90 and 90 degrees")
                        if not (-180 <= point['lng'] <= 180):
                            raise ValidationError("Longitude must be between -180 and 180 degrees")

                except (json.JSONDecodeError, KeyError, TypeError):
                    raise ValidationError("Invalid boundary points format")

    def _is_point_inside(self, latitude, longitude):
        """Check if a point is inside the geofence"""
        if self.geofence_type == 'circle':
            return self._is_point_in_circle(latitude, longitude)
        elif self.geofence_type == 'polygon':
            return self._is_point_in_polygon(latitude, longitude)
        elif self.geofence_type == 'rectangle':
            return self._is_point_in_rectangle(latitude, longitude)
        return False

    def _is_point_in_circle(self, latitude, longitude):
        """Check if point is inside circular geofence"""
        if not (self.center_latitude and self.center_longitude and self.radius):
            return False

        distance = self._calculate_distance(
            self.center_latitude, self.center_longitude,
            latitude, longitude
        )
        return distance <= self.radius

    def _is_point_in_polygon(self, latitude, longitude):
        """Check if point is inside polygon using ray casting algorithm"""
        if not self.boundary_points:
            return False

        try:
            points = json.loads(self.boundary_points)
            if len(points) < 3:
                return False

            x, y = longitude, latitude
            n = len(points)
            inside = False

            p1x, p1y = points[0]['lng'], points[0]['lat']
            for i in range(1, n + 1):
                p2x, p2y = points[i % n]['lng'], points[i % n]['lat']
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y

            return inside

        except (json.JSONDecodeError, KeyError, IndexError):
            return False

    def _is_point_in_rectangle(self, latitude, longitude):
        """Check if point is inside rectangle"""
        # For rectangle, use polygon algorithm with 4 points
        return self._is_point_in_polygon(latitude, longitude)

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
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

    @api.depends()
    def _compute_analytics(self):
        for record in self:
            locations = self.env['hr.employee.location'].search([
                ('geofence_id', '=', record.id),
                ('inside_geofence', '=', True)
            ])

            record.entry_count = len(locations)

            if locations:
                record.last_entry = max(locations.mapped('timestamp'))

                # Calculate average duration (simplified)
                total_duration = 0
                employee_sessions = {}

                for location in locations.sorted('timestamp'):
                    emp_id = location.employee_id.id
                    if emp_id not in employee_sessions:
                        employee_sessions[emp_id] = []
                    employee_sessions[emp_id].append(location.timestamp)

                # Simple duration calculation - difference between first and last location per session
                for emp_id, timestamps in employee_sessions.items():
                    if len(timestamps) > 1:
                        duration = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
                        total_duration += duration

                record.avg_duration = total_duration / len(employee_sessions) if employee_sessions else 0
            else:
                record.last_entry = False
                record.avg_duration = 0

    @api.depends()
    def _compute_current_occupancy(self):
        for record in self:
            # Get recent locations within last hour for employees currently in geofence
            recent_time = fields.Datetime.now() - timedelta(hours=1)
            recent_locations = self.env['hr.employee.location'].search([
                ('geofence_id', '=', record.id),
                ('inside_geofence', '=', True),
                ('timestamp', '>=', recent_time)
            ])

            # Count unique employees
            current_employees = recent_locations.mapped('employee_id')
            record.current_occupancy = len(current_employees)

    def action_view_locations(self):
        """View all locations for this geofence"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Locations in {self.name}',
            'res_model': 'hr.employee.location',
            'view_mode': 'tree,form,map',
            'domain': [('geofence_id', '=', self.id)],
            'context': {'default_geofence_id': self.id},
        }

    def action_view_current_occupants(self):
        """View current occupants of the geofence"""
        self.ensure_one()
        recent_time = fields.Datetime.now() - timedelta(hours=1)
        recent_locations = self.env['hr.employee.location'].search([
            ('geofence_id', '=', self.id),
            ('inside_geofence', '=', True),
            ('timestamp', '>=', recent_time)
        ])

        employee_ids = recent_locations.mapped('employee_id').ids

        return {
            'type': 'ir.actions.act_window',
            'name': f'Current Occupants - {self.name}',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', employee_ids)],
        }

    def test_geofence(self, test_latitude, test_longitude):
        """Test if coordinates are inside geofence - useful for debugging"""
        self.ensure_one()
        result = self._is_point_inside(test_latitude, test_longitude)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Point ({test_latitude}, {test_longitude}) is {"inside" if result else "outside"} geofence {self.name}',
                'type': 'info',
            }
        }