# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo import fields, models


def _formio_view_ondelete_cascade(records):
    # When the formio view types are removed on module uninstall,
    # we want to cascade delete the records that use them.
    records.unlink()


FORMIO_VIEW_TYPES = [
    ('formio_builder', 'formio builder'),
    ('formio_form', 'formio form')
]


class IrUIView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(
        selection_add=FORMIO_VIEW_TYPES, ondelete=_formio_view_ondelete_cascade)

    def _get_view_info(self):
        return {
            'formio_builder': {'icon': 'fa fa-rocket'},
            'formio_form': {'icon': 'fa fa-rocket'}
        } | super()._get_view_info()


class IrActionsActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(
        selection_add=FORMIO_VIEW_TYPES, ondelete=_formio_view_ondelete_cascade)
