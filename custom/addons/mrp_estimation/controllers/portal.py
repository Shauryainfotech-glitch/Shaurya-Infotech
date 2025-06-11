from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class EstimationPortal(CustomerPortal):
    @http.route(['/my/estimations'], type='http', auth="user", website=True)
    def portal_my_estimations(self):
        values = self._prepare_portal_layout_values()
        estimations = request.env['mrp.estimation'].search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ])
        values.update({
            'estimations': estimations,
        })
        return request.render("mrp_estimation.portal_estimation_template", values)