odoo.define('employee_location_tracker.LiveTracker', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
var rpc = require('web.rpc');
var LocationUtils = require('employee_location_tracker.Utils');

var LiveLocationTracker = Widget.extend({
    template: 'employee_location_tracker.LiveTracker',

    events: {
        'click .o_start_tracking': '_onStartTracking',
        'click .o_stop_tracking': '_onStopTracking',
        'click .o_submit_location': '_onSubmitLocation',
    },

    init: function(parent, options) {
        this._super.apply(this, arguments);
        this.options = options || {};
        this.isTracking = false;
        this.trackingInterval = null;
        this.currentPosition = null;
        this.employee_id = this.options.employee_id;
        this.tracking_frequency = this.options.tracking_frequency || 'normal';

        // Set tracking interval based on frequency
        this.intervalMs = this._getIntervalMs(this.tracking_frequency);
    },

    start: function() {
        var self = this;
        return this._super.apply(this, arguments).then(function() {
            self._updateUI();
            self._loadTrackingSettings();
        });
    },

    destroy: function() {
        this._stopTracking();
        this._super.apply(this, arguments);
    },

    _getIntervalMs: function(frequency) {
        var intervals = {
            'realtime': 60000,    // 1 minute
            'frequent': 300000,   // 5 minutes
            'normal': 900000,     // 15 minutes
            'low': 1800000,       // 30 minutes
            'minimal': 3600000    // 1 hour
        };
        return intervals[frequency] || intervals['normal'];
    },

    _loadTrackingSettings: function() {
        var self = this;
        if (!this.employee_id) return;

        rpc.query({
            model: 'hr.location.tracking.settings',
            method: 'search_read',
            args: [[['employee_id', '=', this.employee_id]], ['tracking_enabled', 'tracking_frequency', 'privacy_mode']]
        }).then(function(settings) {
            if (settings.length > 0) {
                var setting = settings[0];
                self.tracking_frequency = setting.tracking_frequency;
                self.intervalMs = self._getIntervalMs(self.tracking_frequency);
                self.privacy_mode = setting.privacy_mode;

                if (setting.tracking_enabled && !self.privacy_mode) {
                    self._onStartTracking();
                }
            }
        });
    },

    _onStartTracking: function(ev) {
        if (ev) ev.preventDefault();

        if (this.isTracking) return;

        var self = this;
        this.isTracking = true;

        // Get initial location
        this._getCurrentLocation().then(function(position) {
            self.currentPosition = position;
            self._submitCurrentLocation();

            // Start periodic tracking
            self.trackingInterval = setInterval(function() {
                self._trackLocation();
            }, self.intervalMs);

            self._updateUI();
            self._showNotification('Location tracking started', 'success');
        }).catch(function(error) {
            self.isTracking = false;
            self._updateUI();
            self._showNotification('Failed to start tracking: ' + error.message, 'danger');
        });
    },

    _onStopTracking: function(ev) {
        if (ev) ev.preventDefault();
        this._stopTracking();
    },

    _stopTracking: function() {
        if (!this.isTracking) return;

        this.isTracking = false;

        if (this.trackingInterval) {
            clearInterval(this.trackingInterval);
            this.trackingInterval = null;
        }

        this._updateUI();
        this._showNotification('Location tracking stopped', 'info');
    },

    _onSubmitLocation: function(ev) {
        if (ev) ev.preventDefault();

        var self = this;
        this._getCurrentLocation().then(function(position) {
            self.currentPosition = position;
            return self._submitCurrentLocation();
        }).then(function() {
            self._showNotification('Location submitted successfully', 'success');
        }).catch(function(error) {
            self._showNotification('Failed to submit location: ' + error.message, 'danger');
        });
    },

    _trackLocation: function() {
        var self = this;
        this._getCurrentLocation().then(function(position) {
            self.currentPosition = position;
            return self._submitCurrentLocation();
        }).catch(function(error) {
            console.warn('Tracking location failed:', error);
        });
    },

    _getCurrentLocation: function() {
        return LocationUtils.getCurrentPosition({
            enableHighAccuracy: true,
            timeout: 30000,
            maximumAge: 60000 // Accept location up to 1 minute old
        });
    },

    _submitCurrentLocation: function() {
        if (!this.currentPosition || !this.employee_id) {
            return Promise.reject(new Error('No position or employee ID available'));
        }

        var locationData = {
            employee_id: this.employee_id,
            latitude: this.currentPosition.coords.latitude,
            longitude: this.currentPosition.coords.longitude,
            accuracy: this.currentPosition.coords.accuracy,
            altitude: this.currentPosition.coords.altitude,
            speed: this.currentPosition.coords.speed,
            heading: this.currentPosition.coords.heading,
            location_type: this.options.location_type || 'work_location',
            device_info: this._getDeviceInfo(),
            battery_level: this._getBatteryLevel(),
            network_type: this._getNetworkType(),
            timestamp: new Date().toISOString()
        };

        return rpc.query({
            route: '/api/location/submit',
            params: locationData
        }).then(function(result) {
            if (!result.success) {
                throw new Error(result.error || 'Unknown error');
            }
            return result;
        });
    },

    _getDeviceInfo: function() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine
        };
    },

    _getBatteryLevel: function() {
        // Battery API is deprecated, return null
        return null;
    },

    _getNetworkType: function() {
        if (navigator.connection) {
            return navigator.connection.effectiveType || 'unknown';
        }
        return 'unknown';
    },

    _updateUI: function() {
        this.$('.o_start_tracking').toggle(!this.isTracking);
        this.$('.o_stop_tracking').toggle(this.isTracking);
        this.$('.o_tracking_status').text(this.isTracking ? 'Tracking Active' : 'Tracking Stopped');
        this.$('.o_tracking_indicator').toggleClass('o_tracking_active', this.isTracking);

        if (this.currentPosition) {
            var coords = LocationUtils.formatCoordinates(
                this.currentPosition.coords.latitude,
                this.currentPosition.coords.longitude
            );
            this.$('.o_current_location').text(coords);

            var accuracy = this.currentPosition.coords.accuracy;
            var accuracyText = LocationUtils.formatDistance(accuracy) + ' (' + LocationUtils.getAccuracyLevel(accuracy) + ')';
            this.$('.o_location_accuracy').text(accuracyText)
                .removeClass('text-success text-info text-warning text-danger text-muted')
                .addClass(LocationUtils.getAccuracyColorClass(accuracy));
        }
    },

    _showNotification: function(message, type) {
        this.trigger_up('display_notification', {
            message: message,
            type: type
        });
    }
});

return LiveLocationTracker;
});