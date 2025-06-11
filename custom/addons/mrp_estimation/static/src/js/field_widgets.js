odoo.define('mrp_estimation.field_widgets', function(require) {
    var core = require('web.core');
    var fieldRegistry = require('web.field_registry');
    var FieldChar = require('web.basic_fields').FieldChar;

    var FieldProductName = FieldChar.extend({
        _render: function() {
            this._super();
            this.$el.css('font-weight', 'bold');
        },
    });

    fieldRegistry.add('field_product_name', FieldProductName);
});
