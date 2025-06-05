from odoo import http
from odoo.http import request
import json


class EstimationAPI(http.Controller):
    @http.route('/api/v1/estimations', type='http', auth='user', methods=['GET'], csrf=False)
    def get_estimations(self, **kwargs):
        estimations = request.env['mrp.estimation'].search_read(
            domain=[],
            fields=['name', 'partner_id', 'date', 'state', 'total_amount']
        )
        return json.dumps(estimations)

    @http.route('/api/v1/estimation/<int:estimation_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_estimation(self, estimation_id, **kwargs):
        estimation = request.env['mrp.estimation'].search_read(
            domain=[('id', '=', estimation_id)],
            fields=['name', 'partner_id', 'date', 'state', 'total_amount', 'line_ids']
        )
        return json.dumps(estimation) 