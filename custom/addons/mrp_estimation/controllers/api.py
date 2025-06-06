from odoo import http
from odoo.http import request
import json

class EstimationAPI(http.Controller):
    @http.route('/api/estimation/create', type='json', auth='user', methods=['POST'])
    def create_estimation(self, **post):
        try:
            vals = {
                'name': post.get('name'),
                'product_id': post.get('product_id'),
                'partner_id': post.get('partner_id'),
            }
            estimation = request.env['mrp.estimation'].create(vals)
            return {'status': 'success', 'estimation_id': estimation.id}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/estimation/<int:estimation_id>', type='json', auth='user', methods=['GET'])
    def get_estimation(self, estimation_id, **kw):
        try:
            estimation = request.env['mrp.estimation'].browse(estimation_id)
            if not estimation.exists():
                return {'status': 'error', 'message': 'Estimation not found'}
            return {'status': 'success', 'data': estimation.read()}
        except Exception as e:
            return {'status': 'error', 'message': str(e)} 