odoo.define('employee_location_tracker.AIDashboard', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');

var AIDashboard = AbstractAction.extend({
    template: 'employee_location_tracker.AIDashboard',

    events: {
        'click .o_dashboard_refresh': '_onRefreshDashboard',
        'change .o_dashboard_filters': '_onFilterChange',
    },

    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.action = action;
        this.dashboard_data = {};
    },

    willStart: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            return self._loadDashboardData();
        });
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self._renderDashboard();
        });
    },

    _loadDashboardData: function () {
        var self = this;

        return rpc.query({
            route: '/api/analytics/summary',
            params: {
                date_from: moment().subtract(30, 'days').format('YYYY-MM-DD'),
                date_to: moment().format('YYYY-MM-DD')
            }
        }).then(function (result) {
            if (result.success) {
                self.dashboard_data = result.summary;
            }
        });
    },

    _renderDashboard: function () {
        var self = this;

        // Render summary cards
        this._renderSummaryCards();

        // Render charts
        this._renderCharts();

        // Render recent activities
        this._renderRecentActivities();
    },

    _renderSummaryCards: function () {
        var data = this.dashboard_data;

        // Total Locations Card
        this.$('.o_summary_total_locations .o_summary_value').text(
            this._formatNumber(data.total_locations || 0)
        );

        // Unique Employees Card
        this.$('.o_summary_employees .o_summary_value').text(
            this._formatNumber(data.unique_employees || 0)
        );

        // Total Distance Card
        this.$('.o_summary_distance .o_summary_value').text(
            this._formatNumber(data.total_distance_km || 0, 1) + ' km'
        );

        // Anomalies Card
        this.$('.o_summary_anomalies .o_summary_value').text(
            this._formatNumber(data.anomalies_detected || 0)
        );

        // High Confidence Card
        this.$('.o_summary_confidence .o_summary_value').text(
            this._formatNumber(data.high_confidence_locations || 0)
        );

        // Average Accuracy Card
        this.$('.o_summary_accuracy .o_summary_value').text(
            this._formatNumber(data.avg_accuracy || 0, 1) + 'm'
        );
    },

    _renderCharts: function () {
        // Location Types Chart
        if (this.dashboard_data.location_types) {
            this._renderPieChart(
                this.$('.o_chart_location_types')[0],
                'Location Types Distribution',
                this.dashboard_data.location_types
            );
        }

        // Daily Activity Chart would go here
        // Weekly patterns, etc.
    },

    _renderPieChart: function (container, title, data) {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded');
            return;
        }

        var labels = Object.keys(data);
        var values = Object.values(data);
        var colors = this._generateColors(labels.length);

        new Chart(container, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: title
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    },

    _renderRecentActivities: function () {
        // Load and display recent location activities
        var self = this;

        rpc.query({
            model: 'hr.employee.location',
            method: 'search_read',
            args: [
                [['timestamp', '>=', moment().subtract(24, 'hours').format('YYYY-MM-DD HH:mm:ss')]],
                ['employee_id', 'timestamp', 'location_type', 'anomaly_detected'],
                0, 10
            ]
        }).then(function (locations) {
            var $container = self.$('.o_recent_activities');
            $container.empty();

            if (locations.length === 0) {
                $container.append('<div class="text-muted">No recent activities</div>');
                return;
            }

            locations.forEach(function (location) {
                var $item = $('<div class="o_activity_item d-flex justify-content-between align-items-center mb-2">');

                var $info = $('<div>');
                $info.append('<strong>' + location.employee_id[1] + '</strong><br>');
                $info.append('<span class="text-muted">' + moment(location.timestamp).fromNow() + '</span>');

                var $badge = $('<span class="badge">');
                if (location.anomaly_detected) {
                    $badge.addClass('badge-warning').text('Anomaly');
                } else {
                    $badge.addClass('badge-success').text(location.location_type);
                }

                $item.append($info).append($badge);
                $container.append($item);
            });
        });
    },

    _onRefreshDashboard: function (ev) {
        ev.preventDefault();

        var $btn = $(ev.currentTarget);
        $btn.prop('disabled', true);

        var self = this;
        this._loadDashboardData().then(function () {
            self._renderDashboard();
            $btn.prop('disabled', false);

            self.displayNotification({
                message: 'Dashboard refreshed successfully',
                type: 'success'
            });
        });
    },

    _onFilterChange: function (ev) {
        // Handle filter changes and refresh dashboard
        this._onRefreshDashboard(ev);
    },

    _formatNumber: function (num, decimals) {
        decimals = decimals || 0;
        return parseFloat(num).toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },

    _generateColors: function (count) {
        var colors = [
            '#007BFF', '#28A745', '#FFC107', '#DC3545', '#6F42C1',
            '#20C997', '#FD7E14', '#E83E8C', '#6C757D', '#17A2B8'
        ];

        var result = [];
        for (var i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }

        return result;
    }
});

core.action_registry.add('employee_location_tracker.ai_dashboard', AIDashboard);

return AIDashboard;
});
