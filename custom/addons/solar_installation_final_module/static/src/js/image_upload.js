odoo.define('your_module_name.image_upload', function (require) {
    "use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');
    var QWeb = core.qweb;

    FormView.include({
        events: _.extend({}, FormView.prototype.events, {
            'click .o_upload_multiple_images': '_onUploadMultipleImages',
        }),

        _onUploadMultipleImages: function (event) {
            var self = this;
            var files = event.target.files;

            // Ensure files are selected
            if (files.length === 0) {
                alert("Please select at least one file.");
                return;
            }

            var file_data = [];
            var file_count = files.length;

            // Loop through each file and read it
            for (var i = 0; i < file_count; i++) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    file_data.push(e.target.result); // Store base64 data of image

                    // If all files are read, send data to the server
                    if (file_data.length === file_count) {
                        self._rpc({
                            model: 'solar.product.product',
                            method: 'action_upload_multiple_images',
                            args: [],
                            context: {file_data: file_data}, // Pass base64 file data to the backend
                        }).then(function () {
                            // Reload the form view to display the uploaded images
                            self.reload();
                        }).fail(function () {
                            alert("Error while uploading images.");
                        });
                    }
                };
                reader.readAsDataURL(files[i]); // Read file as base64
            }
        },
    });
});
