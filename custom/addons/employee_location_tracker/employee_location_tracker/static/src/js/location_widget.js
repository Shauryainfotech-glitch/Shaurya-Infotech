odoo.define('employee_location_tracker.LocationWidget', function (require) {
'use strict';

var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');
var core = require('web.core');

var LocationWidget = AbstractField.extend({
    className: 'o_field_location_widget',
    tagName: 'div',

    events: {
        'click .o_location_get_current': '_onGetCurrentLocation',
        'click .o_location_show_map': '_onShowMap',
    },

    init: function (parent, name, record, options) {
        this._super.apply(this, arguments);
        this.latitude = record.data.latitude || 0;
        this.longitude = record.data.longitude || 0;
        this.accuracy = record.data.accuracy || 0;
    },

    _render: function () {
        var self = this;
        this.$el.empty();

        if (this.mode === 'readonly') {
            this._renderReadonly();
        } else {
            this._renderEdit();
        }

        return this._super.apply(this, arguments);
    },

    _renderReadonly: function () {
        var $content = $('<div class="o_location_readonly">');

        if (this.latitude && this.longitude) {
            $content.append(
                $('<div>').text('Lat: ' + this.latitude.toFixed(6) + ', Lng: ' + this.longitude.toFixed(6))
            );

            if (this.accuracy) {
                $content.append(
                    $('<div class="text-muted">').text('Accuracy: ±' + this.accuracy + 'm')
                );
            }

            $content.append(
                $('<button class="btn btn-sm btn-secondary o_location_show_map" type="button">')
                    .text('Show on Map')
            );
        } else {
            $content.append($('<div class="text-muted">').text('No location data'));
        }

        this.$el.append($content);
    },

    _renderEdit: function () {
        var $content = $('<div class="o_location_edit">');

        // Latitude input
        var $latGroup = $('<div class="form-group">');
        $latGroup.append($('<label>').text('Latitude'));
        var $latInput = $('<input class="form-control o_location_latitude" type="number" step="any">');
        $latInput.val(this.latitude);
        $latGroup.append($latInput);
        $content.append($latGroup);

        // Longitude input
        var $lngGroup = $('<div class="form-group">');
        $lngGroup.append($('<label>').text('Longitude'));
        var $lngInput = $('<input class="form-control o_location_longitude" type="number" step="any">');
        $lngInput.val(this.longitude);
        $lngGroup.append($lngInput);
        $content.append($lngGroup);

        // Accuracy display
        if (this.accuracy) {
            var $accGroup = $('<div class="form-group">');
            $accGroup.append($('<label>').text('Accuracy (meters)'));
            var $accInput = $('<input class="form-control" type="number" readonly>');
            $accInput.val(this.accuracy);
            $accGroup.append($accInput);
            $content.append($accGroup);
        }

        // Action buttons
        var $btnGroup = $('<div class="btn-group mt-2">');
        $btnGroup.append(
            $('<button class="btn btn-primary o_location_get_current" type="button">')
                .text('Get Current Location')
        );
        $btnGroup.append(
            $('<button class="btn btn-secondary o_location_show_map" type="button">')
                .text('Show on Map')
        );
        $content.append($btnGroup);

        this.$el.append($content);

        // Bind change events
        this.$('.o_location_latitude, .o_location_longitude').on('change', this._onLocationChange.bind(this));
    },

    _onLocationChange: function () {
        var latitude = parseFloat(this.$('.o_location_latitude').val()) || 0;
        var longitude = parseFloat(this.$('.o_location_longitude').val()) || 0;

        this.latitude = latitude;
        this.longitude = longitude;

        this._setValue({
            latitude: latitude,
            longitude: longitude
        });
    },

    _onGetCurrentLocation: function (ev) {
        ev.preventDefault();
        var self = this;

        if (!navigator.geolocation) {
            this.displayNotification({
                message: 'Geolocation is not supported by this browser.',
                type: 'warning'
            });
            return;
        }

        var $btn = $(ev.currentTarget);
        $btn.prop('disabled', true).text('Getting location...');

        navigator.geolocation.getCurrentPosition(
            function (position) {
                self.latitude = position.coords.latitude;
                self.longitude = position.coords.longitude;
                self.accuracy = position.coords.accuracy;

                self.$('.o_location_latitude').val(self.latitude);
                self.$('.o_location_longitude').val(self.longitude);

                self._setValue({
                    latitude: self.latitude,
                    longitude: self.longitude,
                    accuracy: self.accuracy
                });

                $btn.prop('disabled', false).text('Get Current Location');

                self.displayNotification({
                    message: 'Location updated successfully',
                    type: 'success'
                });
            },
            function (error) {
                var message = 'Error getting location: ';
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        message += 'Permission denied';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message += 'Position unavailable';
                        break;
                    case error.TIMEOUT:
                        message += 'Request timeout';
                        break;
                    default:
                        message += 'Unknown error';
                        break;
                }

                self.displayNotification({
                    message: message,
                    type: 'danger'
                });

                $btn.prop('disabled', false).text('Get Current Location');
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    },

    _onShowMap: function (ev) {
        ev.preventDefault();

        if (!this.latitude || !this.longitude) {
            this.displayNotification({
                message: 'No location coordinates available',
                type: 'warning'
            });
            return;
        }

        // Open map in new window/tab
        var mapUrl = 'https://www.google.com/maps?q=' + this.latitude + ',' + this.longitude;
        window.open(mapUrl, '_blank');
    }
});

field_registry.add('location_widget', LocationWidget);

return LocationWidget;
});