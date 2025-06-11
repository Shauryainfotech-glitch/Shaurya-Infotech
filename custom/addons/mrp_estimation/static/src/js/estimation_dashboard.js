odoo.define('mrp_estimation.estimation_dashboard', function(require) {
    var publicWidget = require('web.public.widget');
    var Widget = require('web.Widget');

    var EstimationDashboard = publicWidget.Widget.extend({
        selector: '.estimation-dashboard',

        events: {
            'click .view-more': '_onViewMoreClick',
        },

        start: function() {
            this._super.apply(this, arguments);
            this._renderDashboard();
        },

        _renderDashboard: function() {
            this.$('.dashboard-content').html('Dashboard content will be displayed here.');
        },

        _onViewMoreClick: function() {
            alert('More details about the estimations.');
        },
    });

    publicWidget.registry.EstimationDashboard = EstimationDashboard;
});
