from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class LocationTrackingSettings(models.Model):
    _name = 'hr.location.tracking.settings'
    _description = 'Location Tracking Settings'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade'
    )

    # Tracking Configuration
    tracking_enabled = fields.Boolean(
        string='Tracking Enabled',
        default=True,
        help="Enable location tracking for this employee"
    )
    tracking_frequency = fields.Selection([
        ('realtime', 'Real-time (1 min)'),
        ('frequent', 'Frequent (5 min)'),
        ('normal', 'Normal (15 min)'),
        ('low', 'Low (30 min)'),
        ('minimal', 'Minimal (1 hour)')
    ], string='Tracking Frequency', default='normal')

    # Privacy Settings
    privacy_mode = fields.Boolean(
        string='Privacy Mode',
        help="Employee can control when tracking is active"
    )
    tracking_hours_only = fields.Boolean(
        string='Work Hours Only',
        help="Only track during work hours"
    )
    work_start = fields.Float(string='Work Start Hour', default=9.0)
    work_end = fields.Float(string='Work End Hour', default=17.0)

    # Geofence Settings
    auto_attendance = fields.Boolean(
        string='Auto Attendance',
        help="Automatically mark attendance based on geofence"
    )
    alert_outside_geofence = fields.Boolean(
        string='Alert Outside Geofence',
        help="Send alert when employee is outside allowed geofences"
    )

    # Battery Optimization
    battery_optimization = fields.Boolean(
        string='Battery Optimization',
        default=True,
        help="Optimize tracking based on battery level"
    )
    min_battery_level = fields.Integer(
        string='Minimum Battery Level (%)',
        default=15,
        help="Stop intensive tracking below this battery level"
    )

    # Data Retention
    data_retention_days = fields.Integer(
        string='Data Retention (days)',
        default=90,
        help="Number of days to keep location data"
    )

    # Notifications
    notify_anomalies = fields.Boolean(
        string='Notify Anomalies',
        default=True,
        help="Send notifications when anomalies are detected"
    )
    notify_geofence_events = fields.Boolean(
        string='Notify Geofence Events',
        help="Send notifications for geofence entry/exit"
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    # Statistics
    total_locations = fields.Integer(
        string='Total Locations',
        compute='_compute_statistics'
    )
    last_location_time = fields.Datetime(
        string='Last Location',
        compute='_compute_statistics'
    )
    tracking_accuracy_avg = fields.Float(
        string='Average Accuracy (m)',
        compute='_compute_statistics'
    )

    @api.depends('employee_id')
    def _compute_statistics(self):
        for record in self:
            locations = self.env['hr.employee.location'].search([
                ('employee_id', '=', record.employee_id.id)
            ])

            record.total_locations = len(locations)

            if locations:
                record.last_location_time = max(locations.mapped('timestamp'))
                accuracies = locations.filtered('accuracy').mapped('accuracy')
                record.tracking_accuracy_avg = sum(accuracies) / len(accuracies) if accuracies else 0
            else:
                record.last_location_time = False
                record.tracking_accuracy_avg = 0

    def action_clear_location_data(self):
        """Clear all location data for the employee"""
        self.ensure_one()
        locations = self.env['hr.employee.location'].search([
            ('employee_id', '=', self.employee_id.id)
        ])

        count = len(locations)
        locations.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Cleared {count} location records for {self.employee_id.name}',
                'type': 'success',
            }
        }

    def action_cleanup_old_data(self):
        """Manual cleanup of old location data for this employee"""
        self.ensure_one()
        if self.data_retention_days <= 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Data retention is disabled (0 days)',
                    'type': 'warning',
                }
            }

        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        old_locations = self.env['hr.employee.location'].search([
            ('employee_id', '=', self.employee_id.id),
            ('timestamp', '<', cutoff_date)
        ])

        count = len(old_locations)
        old_locations.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Cleaned up {count} old location records for {self.employee_id.name}',
                'type': 'success',
            }
        }

    @api.model
    def cleanup_old_locations(self):
        """Global cleanup of old location data based on retention settings"""
        settings = self.search([('data_retention_days', '>', 0)])
        total_cleaned = 0

        for setting in settings:
            cutoff_date = datetime.now() - timedelta(days=setting.data_retention_days)
            old_locations = self.env['hr.employee.location'].search([
                ('employee_id', '=', setting.employee_id.id),
                ('timestamp', '<', cutoff_date)
            ])

            if old_locations:
                count = len(old_locations)
                total_cleaned += count
                _logger.info(f"Cleaning up {count} old location records for {setting.employee_id.name}")
                old_locations.unlink()

        _logger.info(f"Total location records cleaned up: {total_cleaned}")
        return total_cleaned

    @api.model
    def action_global_cleanup(self):
        """Action to manually trigger global cleanup"""
        total_cleaned = self.cleanup_old_locations()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Global cleanup completed. Removed {total_cleaned} old location records.',
                'type': 'success',
            }
        }


class LocationTrackingSession(models.Model):
    _name = 'hr.location.tracking.session'
    _description = 'Location Tracking Session'
    _order = 'start_time desc'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    start_time = fields.Datetime(
        string='Session Start',
        required=True,
        default=fields.Datetime.now
    )
    end_time = fields.Datetime(string='Session End')

    # Session Statistics
    total_locations = fields.Integer(
        string='Total Locations',
        compute='_compute_session_stats',
        store=True
    )
    total_distance = fields.Float(
        string='Total Distance (km)',
        compute='_compute_session_stats',
        store=True
    )
    duration = fields.Float(
        string='Duration (hours)',
        compute='_compute_duration',
        store=True
    )
    avg_accuracy = fields.Float(
        string='Average Accuracy (m)',
        compute='_compute_session_stats',
        store=True
    )

    # Session Type
    session_type = fields.Selection([
        ('work', 'Work Session'),
        ('travel', 'Travel Session'),
        ('break', 'Break Session'),
        ('personal', 'Personal Time')
    ], string='Session Type', default='work')

    # Geofences Visited
    geofences_visited = fields.Many2many(
        'hr.location.geofence',
        string='Geofences Visited',
        compute='_compute_geofences_visited',
        store=True
    )

    # Session Status
    status = fields.Selection([
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused')
    ], string='Status', default='active')

    notes = fields.Text(string='Notes')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = delta.total_seconds() / 3600
            elif record.start_time:
                delta = fields.Datetime.now() - record.start_time
                record.duration = delta.total_seconds() / 3600
            else:
                record.duration = 0

    @api.depends('employee_id', 'start_time', 'end_time')
    def _compute_session_stats(self):
        for record in self:
            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('timestamp', '>=', record.start_time)
            ]

            if record.end_time:
                domain.append(('timestamp', '<=', record.end_time))

            locations = self.env['hr.employee.location'].search(domain, order='timestamp')

            record.total_locations = len(locations)

            if locations:
                # Calculate total distance
                total_distance = sum(locations.mapped('distance_from_last'))
                record.total_distance = total_distance

                # Calculate average accuracy
                accuracies = locations.filtered('accuracy').mapped('accuracy')
                record.avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
            else:
                record.total_distance = 0
                record.avg_accuracy = 0

    @api.depends('employee_id', 'start_time', 'end_time')
    def _compute_geofences_visited(self):
        for record in self:
            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('timestamp', '>=', record.start_time),
                ('geofence_id', '!=', False)
            ]

            if record.end_time:
                domain.append(('timestamp', '<=', record.end_time))

            locations = self.env['hr.employee.location'].search(domain)
            geofence_ids = list(set(locations.mapped('geofence_id').ids))
            record.geofences_visited = [(6, 0, geofence_ids)]

    def action_end_session(self):
        """End the tracking session"""
        self.ensure_one()
        self.write({
            'end_time': fields.Datetime.now(),
            'status': 'completed'
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Tracking session ended for {self.employee_id.name}',
                'type': 'success',
            }
        }

    def action_pause_session(self):
        """Pause the tracking session"""
        self.ensure_one()
        self.status = 'paused'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Tracking session paused for {self.employee_id.name}',
                'type': 'info',
            }
        }

    def action_resume_session(self):
        """Resume the tracking session"""
        self.ensure_one()
        self.status = 'active'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Tracking session resumed for {self.employee_id.name}',
                'type': 'success',
            }
        }

    def action_view_locations(self):
        """View all locations for this session"""
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.employee_id.id),
            ('timestamp', '>=', self.start_time)
        ]

        if self.end_time:
            domain.append(('timestamp', '<=', self.end_time))

        return {
            'type': 'ir.actions.act_window',
            'name': f'Session Locations - {self.employee_id.name}',
            'res_model': 'hr.employee.location',
            'view_mode': 'tree,form,map',
            'domain': domain,
        }