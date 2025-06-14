/** @odoo-module **/

import { Component, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class MapWidget extends Component {
    static template = "employee_location_tracker.MapWidget";
    static props = standardFieldProps;

    setup() {
        this.orm = useService("orm");
        this.mapRef = useRef("mapContainer");
        this.map = null;
        this.markers = [];

        onMounted(() => {
            this.initializeMap();
        });
    }

    async initializeMap() {
        const recordData = this.props.record.data;
        const lat = recordData.latitude || 0;
        const lng = recordData.longitude || 0;

        if (!lat && !lng) {
            this.mapRef.el.innerHTML = '<div class="text-center text-muted p-4">No location data available</div>';
            return;
        }

        // Load Leaflet if not already loaded
        if (typeof L === 'undefined') {
            await this.loadLeaflet();
        }

        this.createMap(lat, lng);
    }

    loadLeaflet() {
        return new Promise((resolve, reject) => {
            // Load Leaflet CSS
            if (!document.querySelector('link[href*="leaflet"]')) {
                const cssLink = document.createElement('link');
                cssLink.rel = 'stylesheet';
                cssLink.href = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';
                document.head.appendChild(cssLink);
            }

            // Load Leaflet JS
            if (!window.L) {
                const script = document.createElement('script');
                script.src = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js';
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            } else {
                resolve();
            }
        });
    }

    createMap(lat, lng) {
        // Create map
        this.map = L.map(this.mapRef.el).setView([lat, lng], 15);

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add marker for current location
        const marker = L.marker([lat, lng]).addTo(this.map);

        // Add popup with location info
        const popupContent = this.createPopupContent();
        marker.bindPopup(popupContent);

        // Load related locations if employee_id is available
        const recordData = this.props.record.data;
        if (recordData.employee_id) {
            this.loadEmployeeLocations();
        }

        // Load geofences
        this.loadGeofences();
    }

    createPopupContent() {
        const recordData = this.props.record.data;
        let content = '<div class="map-popup">';

        if (recordData.employee_id && recordData.employee_id[1]) {
            content += `<h6>${recordData.employee_id[1]}</h6>`;
        }

        if (recordData.timestamp) {
            const date = new Date(recordData.timestamp);
            content += `<p><strong>Time:</strong> ${date.toLocaleString()}</p>`;
        }

        if (recordData.location_type) {
            content += `<p><strong>Type:</strong> ${recordData.location_type}</p>`;
        }

        if (recordData.address) {
            content += `<p><strong>Address:</strong> ${recordData.address}</p>`;
        }

        if (recordData.accuracy) {
            content += `<p><strong>Accuracy:</strong> ±${recordData.accuracy}m</p>`;
        }

        if (recordData.anomaly_detected) {
            content += '<p class="text-warning"><strong>⚠ Anomaly Detected</strong></p>';
        }

        content += '</div>';
        return content;
    }

    async loadEmployeeLocations() {
        try {
            const recordData = this.props.record.data;
            const employeeId = recordData.employee_id[0];

            // Load recent locations for the same employee (last 7 days)
            const lastWeek = new Date();
            lastWeek.setDate(lastWeek.getDate() - 7);

            const locations = await this.orm.searchRead(
                "hr.employee.location",
                [
                    ["employee_id", "=", employeeId],
                    ["timestamp", ">=", lastWeek.toISOString().split('T')[0]],
                    ["id", "!=", recordData.id]
                ],
                ["latitude", "longitude", "timestamp", "location_type", "anomaly_detected"],
                { limit: 50 }
            );

            this.addLocationMarkers(locations);

        } catch (error) {
            console.error("Failed to load employee locations:", error);
        }
    }

    addLocationMarkers(locations) {
        locations.forEach((location) => {
            const color = location.anomaly_detected ? 'red' : 'blue';
            const marker = L.circleMarker([location.latitude, location.longitude], {
                color: color,
                radius: 5,
                opacity: 0.7
            }).addTo(this.map);

            const date = new Date(location.timestamp);
            const popupContent = `
                <div>
                    <p><strong>Time:</strong> ${date.toLocaleString()}</p>
                    <p><strong>Type:</strong> ${location.location_type}</p>
                    ${location.anomaly_detected ? '<p class="text-warning">⚠ Anomaly</p>' : ''}
                </div>
            `;

            marker.bindPopup(popupContent);
            this.markers.push(marker);
        });
    }

    async loadGeofences() {
        try {
            const geofences = await this.orm.searchRead(
                "hr.location.geofence",
                [["active", "=", true]],
                ["name", "geofence_type", "center_latitude", "center_longitude", "radius", "boundary_points", "color"]
            );

            this.addGeofenceOverlays(geofences);

        } catch (error) {
            console.error("Failed to load geofences:", error);
        }
    }

    addGeofenceOverlays(geofences) {
        geofences.forEach((geofence) => {
            const color = geofence.color || '#007BFF';

            if (geofence.geofence_type === 'circle' && geofence.center_latitude && geofence.center_longitude) {
                const circle = L.circle([geofence.center_latitude, geofence.center_longitude], {
                    radius: geofence.radius || 100,
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.2
                }).addTo(this.map);

                circle.bindPopup(`<strong>${geofence.name}</strong><br>Radius: ${geofence.radius}m`);

            } else if (geofence.boundary_points) {
                try {
                    const points = JSON.parse(geofence.boundary_points);
                    const latLngs = points.map(point => [point.lat, point.lng]);

                    const polygon = L.polygon(latLngs, {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.2
                    }).addTo(this.map);

                    polygon.bindPopup(`<strong>${geofence.name}</strong>`);

                } catch (e) {
                    console.warn('Invalid boundary points for geofence:', geofence.name);
                }
            }
        });
    }
}

// Register the map widget component
registry.category("fields").add("map_widget", MapWidget);