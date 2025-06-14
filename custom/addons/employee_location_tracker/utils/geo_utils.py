import json
import logging
import math

_logger = logging.getLogger(__name__)


class GeoUtils:
    """Geospatial utility functions"""

    @staticmethod
    def point_in_polygon_advanced(latitude, longitude, boundary_points):
        """
        Advanced point-in-polygon test using Shapely (if available)
        Falls back to ray casting if Shapely not available
        """
        try:
            from shapely.geometry import Point, Polygon

            # Create point
            point = Point(longitude, latitude)  # Note: Shapely uses (x, y) = (lon, lat)

            # Create polygon from boundary points
            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            coords = [(p['lng'], p['lat']) for p in boundary_points]
            polygon = Polygon(coords)

            return polygon.contains(point)

        except ImportError:
            # Fall back to ray casting if Shapely not available
            return GeoUtils.point_in_polygon_ray_casting(latitude, longitude, boundary_points)
        except Exception as e:
            _logger.error(f"Advanced point-in-polygon test failed: {str(e)}")
            return False

    @staticmethod
    def point_in_polygon_ray_casting(latitude, longitude, boundary_points):
        """
        Point-in-polygon test using ray casting algorithm
        """
        try:
            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            if len(boundary_points) < 3:
                return False

            x, y = longitude, latitude
            n = len(boundary_points)
            inside = False

            p1x, p1y = boundary_points[0]['lng'], boundary_points[0]['lat']
            for i in range(1, n + 1):
                p2x, p2y = boundary_points[i % n]['lng'], boundary_points[i % n]['lat']
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y

            return inside

        except Exception as e:
            _logger.error(f"Ray casting polygon test failed: {str(e)}")
            return False

    @staticmethod
    def calculate_polygon_area(boundary_points):
        """
        Calculate area of polygon in square meters
        """
        try:
            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            if len(boundary_points) < 3:
                return 0

            # Use Shoelace formula for polygon area
            # Convert to projected coordinates for better accuracy
            coords = [(p['lng'], p['lat']) for p in boundary_points]

            # Simple area calculation (not perfectly accurate for large polygons)
            area = 0
            n = len(coords)

            for i in range(n):
                j = (i + 1) % n
                area += coords[i][0] * coords[j][1]
                area -= coords[j][0] * coords[i][1]

            area = abs(area) / 2.0

            # Convert from degrees to approximate square meters
            # This is a rough approximation - for precise calculations use proper projection
            lat_avg = sum(p['lat'] for p in boundary_points) / len(boundary_points)
            meters_per_degree_lat = 111000
            meters_per_degree_lng = 111000 * math.cos(math.radians(lat_avg))

            area_sqm = area * meters_per_degree_lat * meters_per_degree_lng

            return area_sqm

        except Exception as e:
            _logger.error(f"Polygon area calculation failed: {str(e)}")
            return 0

    @staticmethod
    def get_polygon_centroid(boundary_points):
        """
        Calculate centroid of polygon
        """
        try:
            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            if len(boundary_points) < 3:
                return None

            # Calculate centroid using the centroid formula
            area = 0
            cx = 0
            cy = 0
            n = len(boundary_points)

            for i in range(n):
                j = (i + 1) % n
                xi, yi = boundary_points[i]['lng'], boundary_points[i]['lat']
                xj, yj = boundary_points[j]['lng'], boundary_points[j]['lat']

                cross = xi * yj - xj * yi
                area += cross
                cx += (xi + xj) * cross
                cy += (yi + yj) * cross

            area /= 2.0
            if area == 0:
                # Fallback to simple average if area is zero
                avg_lat = sum(p['lat'] for p in boundary_points) / len(boundary_points)
                avg_lng = sum(p['lng'] for p in boundary_points) / len(boundary_points)
                return {'latitude': avg_lat, 'longitude': avg_lng}

            cx /= (6.0 * area)
            cy /= (6.0 * area)

            return {'latitude': cy, 'longitude': cx}

        except Exception as e:
            _logger.error(f"Centroid calculation failed: {str(e)}")
            return None

    @staticmethod
    def simplify_polygon(boundary_points, tolerance=0.0001):
        """
        Simplify polygon by reducing number of points
        Uses Douglas-Peucker algorithm if Shapely available
        """
        try:
            from shapely.geometry import Polygon

            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            coords = [(p['lng'], p['lat']) for p in boundary_points]
            polygon = Polygon(coords)

            simplified = polygon.simplify(tolerance, preserve_topology=True)

            # Convert back to boundary points format
            simplified_coords = list(simplified.exterior.coords)
            simplified_points = [
                {'lat': coord[1], 'lng': coord[0]}
                for coord in simplified_coords[:-1]  # Remove duplicate last point
            ]

            return simplified_points

        except ImportError:
            # Simple decimation if Shapely not available
            return GeoUtils._simple_point_reduction(boundary_points, tolerance)
        except Exception as e:
            _logger.error(f"Polygon simplification failed: {str(e)}")
            return boundary_points

    @staticmethod
    def _simple_point_reduction(boundary_points, tolerance):
        """Simple point reduction algorithm"""
        try:
            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            if len(boundary_points) <= 3:
                return boundary_points

            simplified = [boundary_points[0]]  # Always keep first point

            for i in range(1, len(boundary_points) - 1):
                prev_point = simplified[-1]
                curr_point = boundary_points[i]

                # Calculate distance from previous point
                distance = math.sqrt(
                    (curr_point['lat'] - prev_point['lat']) ** 2 +
                    (curr_point['lng'] - prev_point['lng']) ** 2
                )

                # Keep point if distance is greater than tolerance
                if distance > tolerance:
                    simplified.append(curr_point)

            # Always keep last point
            simplified.append(boundary_points[-1])

            return simplified

        except Exception as e:
            _logger.error(f"Simple point reduction failed: {str(e)}")
            return boundary_points

    @staticmethod
    def buffer_polygon(boundary_points, buffer_distance_meters):
        """
        Create buffer around polygon
        """
        try:
            from shapely.geometry import Polygon

            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            coords = [(p['lng'], p['lat']) for p in boundary_points]
            polygon = Polygon(coords)

            # Convert buffer distance from meters to degrees (approximate)
            # 1 degree ≈ 111,000 meters at equator
            buffer_degrees = buffer_distance_meters / 111000

            buffered = polygon.buffer(buffer_degrees)

            # Convert back to boundary points format
            buffered_coords = list(buffered.exterior.coords)
            buffered_points = [
                {'lat': coord[1], 'lng': coord[0]}
                for coord in buffered_coords[:-1]
            ]

            return buffered_points

        except ImportError:
            _logger.warning("Shapely not available, cannot create polygon buffer")
            return boundary_points
        except Exception as e:
            _logger.error(f"Polygon buffering failed: {str(e)}")
            return boundary_points

    @staticmethod
    def validate_polygon(boundary_points):
        """
        Validate polygon for common issues
        """
        try:
            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            issues = []

            # Check minimum points
            if len(boundary_points) < 3:
                issues.append("Polygon must have at least 3 points")
                return False, issues

            # Check for valid coordinates
            for i, point in enumerate(boundary_points):
                if 'lat' not in point or 'lng' not in point:
                    issues.append(f"Point {i + 1} missing lat or lng")
                    continue

                lat, lng = point['lat'], point['lng']
                if not (-90 <= lat <= 90):
                    issues.append(f"Point {i + 1} has invalid latitude: {lat}")
                if not (-180 <= lng <= 180):
                    issues.append(f"Point {i + 1} has invalid longitude: {lng}")

            # Check for self-intersection (basic check)
            if len(boundary_points) > 3:
                for i in range(len(boundary_points)):
                    for j in range(i + 2, len(boundary_points)):
                        if j == len(boundary_points) - 1 and i == 0:
                            continue  # Don't check last segment against first

                        # Simple intersection check would go here
                        # This is a simplified version
                        pass

            # Check for very small polygons
            area = GeoUtils.calculate_polygon_area(boundary_points)
            if area < 1:  # Less than 1 square meter
                issues.append("Polygon area is very small (less than 1 sq meter)")

            return len(issues) == 0, issues

        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

    @staticmethod
    def get_bounding_box(boundary_points):
        """
        Get bounding box of polygon
        """
        try:
            if isinstance(boundary_points, str):
                boundary_points = json.loads(boundary_points)

            if not boundary_points:
                return None

            lats = [p['lat'] for p in boundary_points]
            lngs = [p['lng'] for p in boundary_points]

            return {
                'north': max(lats),
                'south': min(lats),
                'east': max(lngs),
                'west': min(lngs),
                'center_lat': (max(lats) + min(lats)) / 2,
                'center_lng': (max(lngs) + min(lngs)) / 2
            }

        except Exception as e:
            _logger.error(f"Bounding box calculation failed: {str(e)}")
            return None
