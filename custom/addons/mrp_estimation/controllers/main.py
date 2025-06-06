from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class EstimationPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'estimation_count' in counters:
            estimation_count = request.env['mrp.estimation'].search_count([])
            values['estimation_count'] = estimation_count
        return values

    @http.route(['/my/estimations', '/my/estimations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_estimations(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        estimations = request.env['mrp.estimation'].search([])
        values.update({
            'estimations': estimations,
            'page_name': 'estimations',
            'default_url': '/my/estimations',
        })
        return request.render("mrp_estimation.portal_my_estimations", values) 