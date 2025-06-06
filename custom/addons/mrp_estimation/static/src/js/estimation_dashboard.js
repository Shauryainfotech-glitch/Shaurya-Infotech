odoo.define('mrp_estimation.dashboard', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var QWeb = core.qweb;

    var EstimationDashboard = AbstractField.extend({
        template: 'EstimationDashboard',
        events: {
            'click .o_dashboard_action': '_onDashboardAction',
        },

        init: function () {
            this._super.apply(this, arguments);
            this.dashboardData = {};
        },

        _render: function () {
            this._super.apply(this, arguments);
            this._updateDashboard();
        },

        _updateDashboard: function () {
            var self = this;
            this._rpc({
                model: 'mrp.estimation',
                method: 'get_dashboard_data',
                args: [],
            }).then(function (result) {
                self.dashboardData = result;
                self.$el.html(QWeb.render('EstimationDashboard', {
                    widget: self,
                    data: result,
                }));
            });
        },

        _onDashboardAction: function (ev) {
            var action = $(ev.currentTarget).data('action');
            this.do_action(action);
        },
    });

    core.form_widget_registry.add('estimation_dashboard', EstimationDashboard);

    return EstimationDashboard;
}); 