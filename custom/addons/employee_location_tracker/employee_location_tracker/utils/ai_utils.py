import statistics
import numpy as np
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class AIUtils:
    """AI utility functions for location analysis"""

    @staticmethod
    def detect_outliers(data_points, threshold=2):
        """
        Detect outliers using Z-score method
        Returns list of indices that are outliers
        """
        if len(data_points) < 3:
            return []

        try:
            mean = statistics.mean(data_points)
            stdev = statistics.stdev(data_points)

            if stdev == 0:
                return []

            outliers = []
            for i, point in enumerate(data_points):
                z_score = abs((point - mean) / stdev)
                if z_score > threshold:
                    outliers.append(i)

            return outliers

        except Exception as e:
            _logger.error(f"Outlier detection failed: {str(e)}")
            return []

    @staticmethod
    def analyze_movement_patterns(locations):
        """
        Analyze movement patterns from location history
        Returns pattern analysis results
        """
        if len(locations) < 5:
            return {'pattern': 'insufficient_data', 'confidence': 0.0}

        try:
            # Calculate movement metrics
            distances = []
            time_intervals = []
            speeds = []

            for i in range(len(locations) - 1):
                loc1 = locations[i]
                loc2 = locations[i + 1]

                # Calculate distance
                from .location_utils import LocationUtils
                distance = LocationUtils.haversine_distance(
                    loc1.latitude, loc1.longitude,
                    loc2.latitude, loc2.longitude
                )
                distances.append(distance)

                # Calculate time interval
                time_diff = (loc2.timestamp - loc1.timestamp).total_seconds()
                time_intervals.append(time_diff)

                # Calculate speed (m/s)
                if time_diff > 0:
                    speed = distance / time_diff
                    speeds.append(speed)

            # Analyze patterns
            avg_distance = statistics.mean(distances) if distances else 0
            avg_speed = statistics.mean(speeds) if speeds else 0
            distance_variance = statistics.variance(distances) if len(distances) > 1 else 0

            # Classify pattern
            if avg_distance < 100:  # Low movement
                pattern = 'stationary'
                confidence = 0.8
            elif avg_speed > 30:  # High speed (>30 m/s = 108 km/h)
                pattern = 'traveling'
                confidence = 0.9
            elif distance_variance < 10000:  # Low variance
                pattern = 'regular_commute'
                confidence = 0.7
            else:
                pattern = 'irregular'
                confidence = 0.6

            return {
                'pattern': pattern,
                'confidence': confidence,
                'avg_distance': avg_distance,
                'avg_speed': avg_speed * 3.6,  # Convert to km/h
                'distance_variance': distance_variance
            }

        except Exception as e:
            _logger.error(f"Movement pattern analysis failed: {str(e)}")
            return {'pattern': 'error', 'confidence': 0.0}

    @staticmethod
    def predict_next_location(locations, prediction_horizon_minutes=30):
        """
        Simple prediction of next location based on recent movement
        For production, use more sophisticated ML models
        """
        if len(locations) < 3:
            return None

        try:
            # Use last 3-5 locations for prediction
            recent_locations = locations[-5:]

            # Calculate average velocity
            total_lat_change = 0
            total_lon_change = 0
            total_time = 0

            for i in range(len(recent_locations) - 1):
                loc1 = recent_locations[i]
                loc2 = recent_locations[i + 1]

                lat_change = loc2.latitude - loc1.latitude
                lon_change = loc2.longitude - loc1.longitude
                time_change = (loc2.timestamp - loc1.timestamp).total_seconds()

                if time_change > 0:
                    total_lat_change += lat_change
                    total_lon_change += lon_change
                    total_time += time_change

            if total_time == 0:
                return None

            # Calculate velocity (degrees per second)
            avg_lat_velocity = total_lat_change / total_time
            avg_lon_velocity = total_lon_change / total_time

            # Predict location after horizon
            last_location = recent_locations[-1]
            prediction_time_seconds = prediction_horizon_minutes * 60

            predicted_lat = last_location.latitude + (avg_lat_velocity * prediction_time_seconds)
            predicted_lon = last_location.longitude + (avg_lon_velocity * prediction_time_seconds)

            return {
                'latitude': predicted_lat,
                'longitude': predicted_lon,
                'confidence': 0.6,  # Simple model, lower confidence
                'prediction_time': last_location.timestamp + timedelta(minutes=prediction_horizon_minutes)
            }

        except Exception as e:
            _logger.error(f"Location prediction failed: {str(e)}")
            return None

    @staticmethod
    def calculate_location_entropy(locations, grid_size=0.001):
        """
        Calculate entropy of location distribution
        Higher entropy = more diverse locations
        """
        if len(locations) < 2:
            return 0

        try:
            # Create grid and count visits
            grid_counts = {}

            for location in locations:
                # Round to grid
                grid_lat = round(location.latitude / grid_size) * grid_size
                grid_lon = round(location.longitude / grid_size) * grid_size
                grid_key = (grid_lat, grid_lon)

                grid_counts[grid_key] = grid_counts.get(grid_key, 0) + 1

            # Calculate entropy
            total_locations = len(locations)
            entropy = 0

            for count in grid_counts.values():
                probability = count / total_locations
                if probability > 0:
                    entropy -= probability * np.log2(probability)

            return entropy

        except Exception as e:
            _logger.error(f"Entropy calculation failed: {str(e)}")
            return 0

    @staticmethod
    def detect_clusters(locations, max_distance=100):
        """
        Simple clustering algorithm to detect location clusters
        Returns list of cluster centers
        """
        if len(locations) < 2:
            return []

        try:
            from .location_utils import LocationUtils

            clusters = []
            remaining_locations = list(locations)

            while remaining_locations:
                # Start new cluster with first remaining location
                cluster_center = remaining_locations.pop(0)
                cluster_locations = [cluster_center]

                # Find all locations within max_distance
                i = 0
                while i < len(remaining_locations):
                    location = remaining_locations[i]
                    distance = LocationUtils.haversine_distance(
                        cluster_center.latitude, cluster_center.longitude,
                        location.latitude, location.longitude
                    )

                    if distance <= max_distance:
                        cluster_locations.append(remaining_locations.pop(i))
                    else:
                        i += 1

                # Calculate cluster center
                if len(cluster_locations) > 1:
                    avg_lat = sum(loc.latitude for loc in cluster_locations) / len(cluster_locations)
                    avg_lon = sum(loc.longitude for loc in cluster_locations) / len(cluster_locations)

                    clusters.append({
                        'center': (avg_lat, avg_lon),
                        'size': len(cluster_locations),
                        'locations': cluster_locations
                    })

            return clusters

        except Exception as e:
            _logger.error(f"Clustering failed: {str(e)}")
            return []

    @staticmethod
    def calculate_work_life_balance_score(locations):
        """
        Calculate work-life balance score based on location patterns
        Returns score between 0-1 (1 = good balance)
        """
        if len(locations) < 10:
            return 0.5  # Neutral score for insufficient data

        try:
            work_locations = 0
            home_locations = 0
            other_locations = 0

            work_hours_count = 0
            after_hours_count = 0

            for location in locations:
                hour = location.timestamp.hour

                # Categorize by time
                if 9 <= hour <= 17:
                    work_hours_count += 1
                else:
                    after_hours_count += 1

                # Categorize by type
                if location.location_type in ['work_location', 'check_in']:
                    work_locations += 1
                elif location.location_type == 'home':
                    home_locations += 1
                else:
                    other_locations += 1

            # Calculate balance factors
            time_balance = min(after_hours_count / work_hours_count, 1.0) if work_hours_count > 0 else 0.5
            location_diversity = min((home_locations + other_locations) / work_locations,
                                     1.0) if work_locations > 0 else 0.5

            # Combine factors
            balance_score = (time_balance + location_diversity) / 2

            return min(max(balance_score, 0.0), 1.0)

        except Exception as e:
            _logger.error(f"Work-life balance calculation failed: {str(e)}")
            return 0.5
