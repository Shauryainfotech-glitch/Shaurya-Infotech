/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class LocationWidget extends Component {
    static template = "employee_location_tracker.LocationWidget";
    static props = standardFieldProps;

    setup() {
        this.state = useState({
            latitude: this.props.record.data.latitude || 0,
            longitude: this.props.record.data.longitude || 0,
            accuracy: this.props.record.data.accuracy || 0,
            isGettingLocation: false
        });
    }

    get isReadonly() {
        return this.props.readonly;
    }

    onGetCurrentLocation() {
        if (!navigator.geolocation) {
            this.env.services.notification.add(
                'Geolocation is not supported by this browser.',
                { type: 'warning' }
            );
            return;
        }

        this.state.isGettingLocation = true;

        navigator.geolocation.getCurrentPosition(
            (position) => {
                this.state.latitude = position.coords.latitude;
                this.state.longitude = position.coords.longitude;
                this.state.accuracy = position.coords.accuracy;
                this.state.isGettingLocation = false;

                // Update the record
                this.props.record.update({
                    latitude: this.state.latitude,
                    longitude: this.state.longitude,
                    accuracy: this.state.accuracy
                });

                this.env.services.notification.add(
                    'Location updated successfully',
                    { type: 'success' }
                );
            },
            (error) => {
                this.state.isGettingLocation = false;
                let message = 'Error getting location: ';
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

                this.env.services.notification.add(message, { type: 'danger' });
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    onShowMap() {
        if (!this.state.latitude || !this.state.longitude) {
            this.env.services.notification.add(
                'No location coordinates available',
                { type: 'warning' }
            );
            return;
        }

        // Open map in new window/tab
        const mapUrl = `https://www.google.com/maps?q=${this.state.latitude},${this.state.longitude}`;
        window.open(mapUrl, '_blank');
    }

    onLocationChange(field, value) {
        this.state[field] = parseFloat(value) || 0;
        
        const updateData = {
            latitude: this.state.latitude,
            longitude: this.state.longitude
        };
        
        this.props.record.update(updateData);
    }
}

registry.category("fields").add("location_widget", LocationWidget);