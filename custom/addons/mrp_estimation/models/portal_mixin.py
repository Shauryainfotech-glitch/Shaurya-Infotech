from odoo import models, fields, api
from odoo.tools import html2plaintext


class EstimationPortalMixin(models.AbstractModel):
    _name = 'estimation.portal.mixin'
    _description = 'Portal Mixin for Manufacturing Estimation'

    portal_access_url = fields.Char(
        'Portal Access URL',
        compute='_compute_portal_access_url'
    )

    def _compute_portal_access_url(self):
        for record in self:
            record.portal_access_url = f'/my/estimation/{record.id}'

    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        url = self.portal_access_url
        if suffix:
            url = f'{url}/{suffix}'
        if report_type:
            url = f'{url}?report_type={report_type}'
        if download:
            url = f'{url}&download=true'
        if query_string:
            url = f'{url}&{query_string}'
        if anchor:
            url = f'{url}#{anchor}'
        return url 