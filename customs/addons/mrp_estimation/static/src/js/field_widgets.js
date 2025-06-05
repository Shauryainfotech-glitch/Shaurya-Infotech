odoo.define('mrp_estimation.field_widgets', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    var field_registry = require('web.field_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var EstimationCostWidget = basic_fields.FloatWidget.extend({
        _formatValue: function (value) {
            var formattedValue = this._super.apply(this, arguments);
            return formattedValue ? '$' + formattedValue : '';
        },
    });

    var EstimationStatusWidget = basic_fields.SelectionWidget.extend({
        _formatValue: function (value) {
            var formattedValue = this._super.apply(this, arguments);
            var statusClass = 'badge badge-' + this._getStatusClass(value);
            return $('<span>', {
                class: statusClass,
                text: formattedValue,
            });
        },

        _getStatusClass: function (value) {
            var classes = {
                'draft': 'secondary',
                'pending': 'warning',
                'approved': 'success',
                'rejected': 'danger',
            };
            return classes[value] || 'secondary';
        },
    });

    field_registry.add('estimation_cost', EstimationCostWidget);
    field_registry.add('estimation_status', EstimationStatusWidget);

    return {
        EstimationCostWidget: EstimationCostWidget,
        EstimationStatusWidget: EstimationStatusWidget,
    };
}); 