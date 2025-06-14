odoo.define('employee_location_tracker.MapWidget', function (require) {
'use strict';

var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');
var rpc = require('web.rpc');

var MapWidget = AbstractField.extend({
    className: 'o_field_map_widget',

    init: function (parent, name, record, options) {
        this._super.apply(this, arguments);
        this.map = null;
        this.markers = [];
        this.record_data = record.data;
    },

    _render: function () {
        var self = this;
        this.$el.empty();

        // Create map container
        var $mapContainer = $('<div class="o_map_container" style="height: 400px; width: 100%;"></div>');
        this.$el.append($mapContainer);

        // Initialize map
        this._initializeMap($mapContainer[0]);

        return this._super.apply(this, arguments);
    },

    _initializeMap: function (container) {
        var self = this;

        // Check if we have location data
        var lat = this.record_data.latitude || 0;
        var lng = this.record_data.longitude || 0;

        if (!lat && !lng) {
            container.innerHTML = '<div class="text-center text-muted p-4">No location data available</div>';
            return;
        }

        // Initialize Leaflet map (using CDN)
        if (typeof L === 'undefined') {
            this._loadLeaflet().then(function () {
                self._createMap(container, lat, lng);
            });
        } else {
            this._createMap(container, lat, lng);
        }
    },

    _loadLeaflet: function () {
        return new Promise(function (resolve, reject) {
            // Load Leaflet CSS
            var cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';
            document.head.appendChild(cssLink);

            // Load Leaflet JS
            var script = document.createElement('script');
            script.src = 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    },

    _createMap: function (container, lat, lng) {
        var self = this;

        // Create map
        this.map = L.map(container).setView([lat, lng], 15);

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add marker for current location
        var marker = L.marker([lat, lng]).addTo(this.map);

        // Add popup with location info
        var popupContent = this._createPopupContent();
        marker.bindPopup(popupContent);

        // Load related locations if employee_id is available
        if (this.record_data.employee_id) {
            this._loadEmployeeLocations();
        }

        // Load geofences
        this._loadGeofences();
    },

    _createPopupContent: function () {
        var content = '<div class="o_map_popup">';

        if (this.record_data.employee_id && this.record_data.employee_id[1]) {
            content += '<h6>' + this.record_data.employee_id[1] + '</h6>';
        }

        if (this.record_data.timestamp) {
            content += '<p><strong>Time:</strong> ' + moment(this.record_data.timestamp).format('YYYY-MM-DD HH:mm') + '</p>';
        }

        if (this.record_data.location_type) {
            content += '<p><strong>Type:</strong> ' + this.record_data.location_type + '</p>';
        }

        if (this.record_data.address) {
            content += '<p><strong>Address:</strong> ' + this.record_data.address + '</p>';
        }

        if (this.record_data.accuracy) {
            content += '<p><strong>Accuracy:</strong> ±' + this.record_data.accuracy + 'm</p>';
        }

        if (this.record_data.anomaly_detected) {
            content += '<p class="text-warning"><strong>⚠ Anomaly Detected</strong></p>';
        }

        content += '</div>';
        return content;
    },

    _loadEmployeeLocations: function () {
        var self = this;
        var employee_id = this.record_data.employee_id[0];

        // Load recent locations for the same employee
        rpc.query({
            model: 'hr.employee.location',
            method: 'search_read',
            args: [
                [
                    ['employee_id', '=', employee_id],
                    ['timestamp', '>=', moment().subtract(7, 'days').format('YYYY-MM-DD')],
                    ['id', '!=', this.record_data.id]
                ],
                ['latitude', 'longitude', 'timestamp', 'location_type', 'anomaly_detected'],
                0, 50
            ]
        }).then(function (locations) {
            self._addLocationMarkers(locations);
        });
    },

    _addLocationMarkers: function (locations) {
        var self = this;

        locations.forEach(function (location, index) {
            var color = location.anomaly_detected ? 'red' : 'blue';
            var marker = L.circleMarker([location.latitude, location.longitude], {
                color: color,
                radius: 5,
                opacity: 0.7
            }).addTo(self.map);

            var popupContent = '<div>' +
                '<p><strong>Time:</strong> ' + moment(location.timestamp).format('YYYY-MM-DD HH:mm') + '</p>' +
                '<p><strong>Type:</strong> ' + location.location_type + '</p>' +
                (location.anomaly_detected ? '<p class="text-warning">⚠ Anomaly</p>' : '') +
                '</div>';

            marker.bindPopup(popupContent);
            self.markers.push(marker);
        });
    },

    _loadGeofences: function () {
        var self = this;

        rpc.query({
            model: 'hr.location.geofence',
            method: 'search_read',
            args: [
                [['active', '=', true]],
                ['name', 'geofence_type', 'center_latitude', 'center_longitude', 'radius', 'boundary_points', 'color']
            ]
        }).then(function (geofences) {
            self._addGeofenceOverlays(geofences);
        });
    },

    _addGeofenceOverlays: function (geofences) {
        var self = this;

        geofences.forEach(function (geofence) {
            var color = geofence.color || '#007BFF';

            if (geofence.geofence_type === 'circle' && geofence.center_latitude && geofence.center_longitude) {
                var circle = L.circle([geofence.center_latitude, geofence.center_longitude], {
                    radius: geofence.radius || 100,
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.2
                }).addTo(self.map);

                circle.bindPopup('<strong>' + geofence.name + '</strong><br>Radius: ' + geofence.radius + 'm');

            } else if (geofence.boundary_points) {
                try {
                    var points = JSON.parse(geofence.boundary_points);
                    var latLngs = points.map(function (point) {
                        return [point.lat, point.lng];
                    });

                    var polygon = L.polygon(latLngs, {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.2
                    }).addTo(self.map);

                    polygon.bindPopup('<strong>' + geofence.name + '</strong>');

                } catch (e) {
                    console.warn('Invalid boundary points for geofence:', geofence.name);
                }
            }
        });
    }
});

field_registry.add('map_widget', MapWidget);

return MapWidget;
});