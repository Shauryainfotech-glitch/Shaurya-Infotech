from odoo import http

class EstimationController(http.Controller):

    @http.route('/estimation/portal', auth='user', website=True)
    def portal(self, **kw):
        return http.request.render('mrp_estimation.portal_estimation', {})
