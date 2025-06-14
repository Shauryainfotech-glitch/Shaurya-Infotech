from odoo import api, SUPERUSER_ID
import logging
import requests
import json
import math

_logger = logging.getLogger(__name__)


class LocationUtils:
    """Utility functions for location processing"""

    @staticmethod
    def reverse_geocode(env, latitude, longitude, api_key=None):
        """
        Reverse geocode coordinates to get address
        Supports Google Maps API, OpenStreetMap Nominatim
        """
        try:
            # Try OpenStreetMap Nominatim first (free)
            nominatim_url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1
            }

            response = requests.get(nominatim_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'display_name' in data:
                    return data['display_name']

            # Fallback to Google Maps API if available
            if api_key:
                google_url = f"https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    'latlng': f"{latitude},{longitude}",
                    'key': api_key
                }

                response = requests.get(google_url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'OK' and data['results']:
                        return data['results'][0]['formatted_address']

        except Exception as e:
            _logger.warning(f"Reverse geocoding failed: {str(e)}")

        return f"Location: {latitude:.4f}, {longitude:.4f}"

    @staticmethod
    def get_weather_data(env, latitude, longitude, api_key=None):
        """
        Get weather data for location
        Requires OpenWeatherMap API key
        """
        if not api_key:
            return None

        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': api_key,
                'units': 'metric'
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'condition': data['weather'][0]['description'],
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data.get('wind', {}).get('speed', 0)
                }

        except Exception as e:
            _logger.warning(f"Weather data fetch failed: {str(e)}")

        return None

    @staticmethod
    def calculate_route_distance(env, waypoints):
        """
        Calculate total route distance for multiple waypoints
        """
        if len(waypoints) < 2:
            return 0

        total_distance = 0
        for i in range(len(waypoints) - 1):
            lat1, lon1 = waypoints[i]
            lat2, lon2 = waypoints[i + 1]

            distance = LocationUtils.haversine_distance(lat1, lon1, lat2, lon2)
            total_distance += distance

        return total_distance

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        Returns distance in meters
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in meters
        r = 6371000

        return c * r

    @staticmethod
    def optimize_route(env, waypoints, start_point=None, end_point=None):
        """
        Simple route optimization using nearest neighbor algorithm
        For production, integrate with Google Maps Directions API or similar
        """
        if len(waypoints) < 3:
            return waypoints

        if start_point:
            waypoints = [start_point] + waypoints

        # Simple nearest neighbor optimization
        optimized_route = []
        remaining_points = waypoints.copy()

        # Start with first point
        current_point = remaining_points.pop(0)
        optimized_route.append(current_point)

        while remaining_points:
            # Find nearest point to current
            nearest_distance = float('inf')
            nearest_point = None
            nearest_index = -1

            for i, point in enumerate(remaining_points):
                distance = LocationUtils.haversine_distance(
                    current_point[0], current_point[1],
                    point[0], point[1]
                )
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_point = point
                    nearest_index = i

            # Add nearest point to route
            optimized_route.append(nearest_point)
            current_point = nearest_point
            remaining_points.pop(nearest_index)

        if end_point and end_point not in optimized_route:
            optimized_route.append(end_point)

        return optimized_route

    @staticmethod
    def validate_coordinates(latitude, longitude):
        """Validate GPS coordinates"""
        try:
            lat = float(latitude)
            lon = float(longitude)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (ValueError, TypeError):
            return False

    @staticmethod
    def format_coordinates(latitude, longitude, precision=6):
        """Format coordinates for display"""
        return f"{latitude:.{precision}f}, {longitude:.{precision}f}"

    @staticmethod
    def get_timezone_from_coordinates(latitude, longitude):
        """Get timezone from coordinates using timezonefinder"""
        try:
            from timezonefinder import TimezoneFinder
            tf = TimezoneFinder()
            timezone = tf.timezone_at(lng=longitude, lat=latitude)
            return timezone
        except ImportError:
            _logger.warning("timezonefinder not installed, cannot determine timezone")
            return None
        except Exception as e:
            _logger.warning(f"Failed to get timezone: {str(e)}")
            return None