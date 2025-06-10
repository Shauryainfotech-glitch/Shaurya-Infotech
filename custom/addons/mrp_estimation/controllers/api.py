from odoo import http
from odoo.http import request
import json

class EstimationAPI(http.Controller):

    @http.route('/api/v1/estimations', auth='public', methods=['POST'], type='json', csrf=False)
    def create_estimation(self, **kwargs):
        # Assuming the model is 'mrp.estimation' for estimation creation
        Estimation = request.env['mrp.estimation'].sudo()
        new_estimation = Estimation.create({
            'name': kwargs.get('name'),
            'partner_id': kwargs.get('partner_id'),
            'product_id': kwargs.get('product_id'),
            'quantity': kwargs.get('quantity'),
        })
        return json.dumps({"status": "success", "estimation_id": new_estimation.id})
