from odoo import models, fields, api
import json
import logging
from datetime import datetime, timedelta
import statistics

_logger = logging.getLogger(__name__)


class LocationAIAnalysis(models.Model):
    _name = 'hr.location.ai.analysis'
    _description = 'AI Analysis for Location Tracking'

    def analyze_location(self, location_record):
        """Perform comprehensive AI analysis on location data"""
        try:
            results = {}

            # Pattern Recognition Analysis
            pattern_analysis = self._analyze_behavior_pattern(location_record)
            results.update(pattern_analysis)

            # Anomaly Detection
            anomaly_analysis = self._detect_anomalies(location_record)
            results.update(anomaly_analysis)

            # Confidence Scoring
            confidence_score = self._calculate_confidence_score(location_record)
            results['confidence'] = confidence_score

            # Route Optimization Analysis
            route_analysis = self._analyze_route_efficiency(location_record)
            results['route_analysis'] = route_analysis

            # Time Pattern Analysis
            time_analysis = self._analyze_time_patterns(location_record)
            results['time_patterns'] = time_analysis

            # Final validation decision
            results['is_valid'] = (
                    confidence_score > 0.7 and
                    not results.get('anomaly', False) and
                    results.get('pattern', 'unknown') != 'suspicious'
            )

            # Generate summary notes
            results['notes'] = self._generate_analysis_notes(results)

            return results

        except Exception as e:
            _logger.error(f"AI Analysis failed for location {location_record.id}: {str(e)}")
            return {
                'confidence': 0.5,
                'anomaly': False,
                'pattern': 'unknown',
                'is_valid': True,
                'notes': f'AI analysis failed: {str(e)}',
                'anomaly_details': []
            }

    def _analyze_behavior_pattern(self, location_record):
        """Analyze employee behavior patterns using historical data"""
        employee_id = location_record.employee_id.id
        current_time = location_record.timestamp

        # Get historical data for pattern analysis (last 30 days)
        historical_locations = self.env['hr.employee.location'].search([
            ('employee_id', '=', employee_id),
            ('timestamp', '>=', current_time - timedelta(days=30)),
            ('timestamp', '<', current_time),
            ('is_valid', '=', True)
        ], order='timestamp desc', limit=200)

        if len(historical_locations) < 5:
            return {
                'pattern': 'unknown',
                'pattern_confidence': 0.3,
                'pattern_description': 'Insufficient historical data for pattern analysis'
            }

        # Analyze different pattern aspects
        work_pattern = self._analyze_work_pattern(historical_locations, current_time)
        movement_pattern = self._analyze_movement_pattern(historical_locations, location_record)
        location_consistency = self._analyze_location_consistency(historical_locations, location_record)

        # Determine overall pattern
        pattern_type = self._classify_behavior_pattern(work_pattern, movement_pattern, location_consistency)

        return {
            'pattern': pattern_type['type'],
            'pattern_confidence': pattern_type['confidence'],
            'pattern_description': pattern_type['description'],
            'work_pattern': work_pattern,
            'movement_pattern': movement_pattern,
            'location_consistency': location_consistency
        }

    def _analyze_work_pattern(self, historical_locations, current_time):
        """Analyze work time patterns"""
        work_hours_locations = historical_locations.filtered(
            lambda l: 9 <= l.timestamp.hour <= 17
        )

        if not work_hours_locations:
            return {'type': 'irregular', 'score': 0.3}

        # Analyze consistency of work hours
        work_hours = [l.timestamp.hour for l in work_hours_locations]

        if len(set(work_hours)) <= 3:  # Consistent work hours
            return {'type': 'regular', 'score': 0.9}
        elif len(set(work_hours)) <= 6:  # Moderately consistent
            return {'type': 'flexible', 'score': 0.7}
        else:  # Highly variable
            return {'type': 'irregular', 'score': 0.4}

    def _analyze_movement_pattern(self, historical_locations, current_location):
        """Analyze movement and travel patterns"""
        if len(historical_locations) < 2:
            return {'type': 'unknown', 'score': 0.3}

        # Calculate distances between consecutive locations
        distances = []
        for i in range(len(historical_locations) - 1):
            loc1 = historical_locations[i]
            loc2 = historical_locations[i + 1]
            distance = current_location._calculate_distance(
                loc1.latitude, loc1.longitude,
                loc2.latitude, loc2.longitude
            )
            distances.append(distance)

        if not distances:
            return {'type': 'stationary', 'score': 0.5}

        avg_distance = statistics.mean(distances)
        max_distance = max(distances)

        # Classify movement pattern
        if avg_distance < 500:  # Less than 500m average movement
            return {'type': 'stationary', 'score': 0.8}
        elif avg_distance < 5000:  # Less than 5km average movement
            return {'type': 'local', 'score': 0.7}
        elif max_distance > 50000:  # More than 50km max movement
            return {'type': 'traveling', 'score': 0.6}
        else:
            return {'type': 'mobile', 'score': 0.7}

    def _analyze_location_consistency(self, historical_locations, current_location):
        """Analyze consistency of work locations"""
        work_locations = historical_locations.filtered(
            lambda l: l.location_type in ['work_location', 'check_in']
        )

        if len(work_locations) < 3:
            return {'score': 0.3, 'type': 'inconsistent'}

        # Calculate centroid of work locations
        avg_lat = sum(l.latitude for l in work_locations) / len(work_locations)
        avg_lon = sum(l.longitude for l in work_locations) / len(work_locations)

        # Calculate variance from centroid
        variances = []
        for location in work_locations:
            distance = current_location._calculate_distance(
                avg_lat, avg_lon,
                location.latitude, location.longitude
            )
            variances.append(distance)

        avg_variance = statistics.mean(variances)

        # Classify consistency
        if avg_variance < 100:  # Very consistent (within 100m)
            return {'score': 0.95, 'type': 'very_consistent'}
        elif avg_variance < 500:  # Consistent (within 500m)
            return {'score': 0.8, 'type': 'consistent'}
        elif avg_variance < 2000:  # Moderately consistent (within 2km)
            return {'score': 0.6, 'type': 'moderate'}
        else:  # Inconsistent
            return {'score': 0.3, 'type': 'inconsistent'}

    def _classify_behavior_pattern(self, work_pattern, movement_pattern, location_consistency):
        """Classify overall behavior pattern"""
        # Weight different factors
        work_score = work_pattern['score'] * 0.3
        movement_score = movement_pattern['score'] * 0.4
        consistency_score = location_consistency['score'] * 0.3

        overall_score = work_score + movement_score + consistency_score

        # Determine pattern type based on individual analyses
        if movement_pattern['type'] == 'traveling':
            pattern_type = 'traveling'
        elif work_pattern['type'] == 'irregular' and overall_score < 0.5:
            pattern_type = 'unusual'
        elif location_consistency['type'] == 'very_consistent' and work_pattern['type'] == 'regular':
            pattern_type = 'normal'
        elif movement_pattern['type'] == 'stationary' and work_pattern['score'] < 0.4:
            pattern_type = 'working_from_home'
        else:
            pattern_type = 'normal' if overall_score > 0.6 else 'unusual'

        descriptions = {
            'normal': 'Regular work pattern with consistent location behavior',
            'traveling': 'High mobility pattern indicating travel or field work',
            'working_from_home': 'Stationary pattern suggesting remote work',
            'commuting': 'Regular movement pattern between fixed locations',
            'unusual': 'Irregular pattern that deviates from normal behavior',
            'suspicious': 'Pattern that requires immediate attention'
        }

        return {
            'type': pattern_type,
            'confidence': overall_score,
            'description': descriptions.get(pattern_type, 'Unknown pattern type')
        }

    def _detect_anomalies(self, location_record):
        """Detect various types of location anomalies"""
        anomalies = []
        anomaly_scores = []

        # Time-based anomaly detection
        time_anomalies = self._detect_time_anomalies(location_record)
        if time_anomalies['detected']:
            anomalies.extend(time_anomalies['details'])
            anomaly_scores.append(time_anomalies['severity'])

        # Speed-based anomaly detection
        speed_anomalies = self._detect_speed_anomalies(location_record)
        if speed_anomalies['detected']:
            anomalies.extend(speed_anomalies['details'])
            anomaly_scores.append(speed_anomalies['severity'])

        # Location-based anomaly detection
        location_anomalies = self._detect_location_anomalies(location_record)
        if location_anomalies['detected']:
            anomalies.extend(location_anomalies['details'])
            anomaly_scores.append(location_anomalies['severity'])

        # GPS accuracy anomaly detection
        accuracy_anomalies = self._detect_accuracy_anomalies(location_record)
        if accuracy_anomalies['detected']:
            anomalies.extend(accuracy_anomalies['details'])
            anomaly_scores.append(accuracy_anomalies['severity'])

        # Determine overall anomaly status
        anomaly_detected = len(anomalies) > 0
        max_severity = max(anomaly_scores) if anomaly_scores else 0

        return {
            'anomaly': anomaly_detected,
            'anomaly_details': anomalies,
            'anomaly_severity': max_severity,
            'anomaly_count': len(anomalies)
        }

    def _detect_time_anomalies(self, location_record):
        """Detect time-based anomalies"""
        anomalies = []
        severity = 0

        hour = location_record.timestamp.hour
        day_of_week = location_record.timestamp.weekday()  # 0=Monday, 6=Sunday

        # Check for unusual hours
        if hour < 6 or hour > 22:
            anomalies.append(f"Location recorded at unusual hour: {hour}:00")
            severity = max(severity, 0.6)

        # Check for weekend activity (if not expected)
        if day_of_week >= 5:  # Weekend
            if location_record.location_type in ['work_location', 'check_in']:
                anomalies.append("Work location recorded during weekend")
                severity = max(severity, 0.4)

        # Check for public holidays (simplified - would need holiday calendar integration)
        # This is a placeholder for holiday detection

        return {
            'detected': len(anomalies) > 0,
            'details': anomalies,
            'severity': severity
        }

    def _detect_speed_anomalies(self, location_record):
        """Detect unrealistic movement speeds"""
        anomalies = []
        severity = 0

        # Get previous location
        previous_location = self.env['hr.employee.location'].search([
            ('employee_id', '=', location_record.employee_id.id),
            ('timestamp', '<', location_record.timestamp),
            ('is_valid', '=', True)
        ], order='timestamp desc', limit=1)

        if previous_location:
            time_diff = (location_record.timestamp - previous_location.timestamp).total_seconds()

            if time_diff > 0 and time_diff < 3600:  # Only check if less than 1 hour apart
                distance = location_record._calculate_distance(
                    previous_location.latitude, previous_location.longitude,
                    location_record.latitude, location_record.longitude
                )

                # Calculate speed in km/h
                speed_kmh = (distance / 1000) / (time_diff / 3600)

                # Define speed thresholds
                if speed_kmh > 200:  # Unrealistic speed (>200 km/h)
                    anomalies.append(f"Unrealistic travel speed: {speed_kmh:.1f} km/h")
                    severity = max(severity, 0.9)
                elif speed_kmh > 120:  # High speed (>120 km/h)
                    anomalies.append(f"High travel speed detected: {speed_kmh:.1f} km/h")
                    severity = max(severity, 0.6)
                elif time_diff < 60 and distance > 1000:  # >1km in <1 minute
                    anomalies.append(f"Rapid location change: {distance:.0f}m in {time_diff:.0f}s")
                    severity = max(severity, 0.7)

        return {
            'detected': len(anomalies) > 0,
            'details': anomalies,
            'severity': severity
        }

    def _detect_location_anomalies(self, location_record):
        """Detect location-based anomalies"""
        anomalies = []
        severity = 0

        # Check if location is in an unusual area for this employee
        employee_historical = self.env['hr.employee.location'].search([
            ('employee_id', '=', location_record.employee_id.id),
            ('timestamp', '>=', location_record.timestamp - timedelta(days=30)),
            ('is_valid', '=', True)
        ])

        if len(employee_historical) > 10:
            # Calculate distance from employee's usual locations
            distances = []
            for hist_loc in employee_historical:
                distance = location_record._calculate_distance(
                    hist_loc.latitude, hist_loc.longitude,
                    location_record.latitude, location_record.longitude
                )
                distances.append(distance)

            avg_distance = statistics.mean(distances)

            # Check if current location is unusually far from typical locations
            if avg_distance > 50000:  # More than 50km from usual locations
                anomalies.append(f"Location unusually far from typical areas: {avg_distance / 1000:.1f}km")
                severity = max(severity, 0.7)
            elif avg_distance > 20000:  # More than 20km from usual locations
                anomalies.append(f"Location outside normal area: {avg_distance / 1000:.1f}km")
                severity = max(severity, 0.5)

        # Check for locations in restricted areas (if any defined)
        # This would integrate with restricted area definitions

        return {
            'detected': len(anomalies) > 0,
            'details': anomalies,
            'severity': severity
        }

    def _detect_accuracy_anomalies(self, location_record):
        """Detect GPS accuracy issues"""
        anomalies = []
        severity = 0

        if location_record.accuracy:
            if location_record.accuracy > 1000:  # Very poor accuracy (>1km)
                anomalies.append(f"Very poor GPS accuracy: {location_record.accuracy:.0f}m")
                severity = max(severity, 0.8)
            elif location_record.accuracy > 500:  # Poor accuracy (>500m)
                anomalies.append(f"Poor GPS accuracy: {location_record.accuracy:.0f}m")
                severity = max(severity, 0.5)
            elif location_record.accuracy > 100:  # Moderate accuracy issues
                anomalies.append(f"Moderate GPS accuracy: {location_record.accuracy:.0f}m")
                severity = max(severity, 0.3)

        return {
            'detected': len(anomalies) > 0,
            'details': anomalies,
            'severity': severity
        }

    def _calculate_confidence_score(self, location_record):
        """Calculate overall confidence score for the location"""
        score = 1.0

        # GPS accuracy factor
        if location_record.accuracy:
            if location_record.accuracy > 1000:
                score -= 0.4
            elif location_record.accuracy > 500:
                score -= 0.3
            elif location_record.accuracy > 100:
                score -= 0.2
            elif location_record.accuracy > 50:
                score -= 0.1

        # Time-based confidence
        hour = location_record.timestamp.hour
        if 9 <= hour <= 17:  # Work hours
            score += 0.1
        elif hour < 6 or hour > 22:  # Unusual hours
            score -= 0.2

        # Geofence validation
        if location_record.geofence_id:
            if location_record.inside_geofence:
                score += 0.1
            else:
                score -= 0.2

        # Battery level factor (if available)
        if location_record.battery_level:
            if location_record.battery_level < 10:  # Low battery might affect GPS
                score -= 0.1

        # Network type factor
        if location_record.network_type == 'wifi':
            score += 0.05  # WiFi generally more reliable for location

        return max(0.0, min(1.0, score))

    def _analyze_route_efficiency(self, location_record):
        """Analyze route efficiency and suggest optimizations"""
        # Get recent locations for route analysis
        recent_locations = self.env['hr.employee.location'].search([
            ('employee_id', '=', location_record.employee_id.id),
            ('timestamp', '>=', location_record.timestamp - timedelta(hours=8)),
            ('timestamp', '<=', location_record.timestamp)
        ], order='timestamp')

        if len(recent_locations) < 3:
            return {
                'efficiency_score': 0.5,
                'total_distance': 0,
                'suggestions': []
            }

        # Calculate total distance traveled
        total_distance = 0
        for i in range(len(recent_locations) - 1):
            loc1 = recent_locations[i]
            loc2 = recent_locations[i + 1]
            distance = location_record._calculate_distance(
                loc1.latitude, loc1.longitude,
                loc2.latitude, loc2.longitude
            )
            total_distance += distance

        # Analyze efficiency (simplified algorithm)
        straight_line_distance = location_record._calculate_distance(
            recent_locations[0].latitude, recent_locations[0].longitude,
            recent_locations[-1].latitude, recent_locations[-1].longitude
        )

        efficiency_score = straight_line_distance / total_distance if total_distance > 0 else 0

        suggestions = []
        if efficiency_score < 0.5:
            suggestions.append("Route appears inefficient - consider optimizing travel path")
        if total_distance > 100000:  # More than 100km in 8 hours
            suggestions.append("High travel distance detected - review travel necessity")

        return {
            'efficiency_score': efficiency_score,
            'total_distance': total_distance / 1000,  # Convert to km
            'straight_line_distance': straight_line_distance / 1000,
            'suggestions': suggestions
        }

    def _analyze_time_patterns(self, location_record):
        """Analyze time-based patterns"""
        hour = location_record.timestamp.hour
        day_of_week = location_record.timestamp.weekday()

        # Get historical data for the same time periods
        same_hour_locations = self.env['hr.employee.location'].search([
            ('employee_id', '=', location_record.employee_id.id),
            ('timestamp', '>=', location_record.timestamp - timedelta(days=30))
        ]).filtered(lambda l: l.timestamp.hour == hour)

        same_day_locations = self.env['hr.employee.location'].search([
            ('employee_id', '=', location_record.employee_id.id),
            ('timestamp', '>=', location_record.timestamp - timedelta(days=30))
        ]).filtered(lambda l: l.timestamp.weekday() == day_of_week)

        return {
            'hour_frequency': len(same_hour_locations),
            'day_frequency': len(same_day_locations),
            'is_typical_hour': len(same_hour_locations) > 5,
            'is_typical_day': len(same_day_locations) > 10
        }

    def _generate_analysis_notes(self, results):
        """Generate human-readable analysis notes"""
        notes = []

        # Pattern analysis notes
        if 'pattern_description' in results:
            notes.append(f"Pattern: {results['pattern_description']}")

        # Confidence score notes
        confidence = results.get('confidence', 0)
        if confidence > 0.8:
            notes.append("High confidence in location accuracy")
        elif confidence > 0.6:
            notes.append("Moderate confidence in location accuracy")
        else:
            notes.append("Low confidence in location accuracy")

        # Anomaly notes
        if results.get('anomaly', False):
            anomaly_count = results.get('anomaly_count', 0)
            notes.append(f"{anomaly_count} anomal{'y' if anomaly_count == 1 else 'ies'} detected")

        # Route efficiency notes
        route_analysis = results.get('route_analysis', {})
        if route_analysis.get('suggestions'):
            notes.append("Route optimization suggestions available")

        return '; '.join(notes)


class LocationAnalyticsReport(models.Model):
    _name = 'hr.location.analytics.report'
    _description = 'Location Analytics Report'
    _auto = False
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    date = fields.Date(string='Date')
    total_locations = fields.Integer(string='Total Locations')
    work_hours_locations = fields.Integer(string='Work Hours Locations')
    travel_distance = fields.Float(string='Travel Distance (km)')
    avg_accuracy = fields.Float(string='Average GPS Accuracy (m)')
    anomaly_count = fields.Integer(string='Anomalies Detected')
    geofence_entries = fields.Integer(string='Geofence Entries')
    avg_confidence_score = fields.Float(string='Average Confidence Score')
    most_common_location_type = fields.Char(string='Most Common Location Type')

    def init(self):
        from odoo import tools
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    row_number() OVER () AS id,
                    employee_id,
                    DATE(timestamp) as date,
                    COUNT(*) as total_locations,
                    COUNT(CASE WHEN EXTRACT(hour FROM timestamp) BETWEEN 9 AND 17 THEN 1 END) as work_hours_locations,
                    COALESCE(SUM(distance_from_last), 0) as travel_distance,
                    COALESCE(AVG(accuracy), 0) as avg_accuracy,
                    COUNT(CASE WHEN anomaly_detected = true THEN 1 END) as anomaly_count,
                    COUNT(CASE WHEN geofence_entry = true OR geofence_exit = true THEN 1 END) as geofence_entries,
                    COALESCE(AVG(ai_confidence_score), 0) as avg_confidence_score,
                    MODE() WITHIN GROUP (ORDER BY location_type) as most_common_location_type
                FROM hr_employee_location
                WHERE is_valid = true
                GROUP BY employee_id, DATE(timestamp)
            )
        """)