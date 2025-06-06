from odoo import http
from odoo.http import request, Response
import json
import logging
import base64

_logger = logging.getLogger(__name__)

class EstimationAPI(http.Controller):
    @http.route('/api/v1/estimations', type='json', auth='user', methods=['GET'], csrf=False)
    def get_estimations(self, **kwargs):
        try:
            estimations = request.env['mrp.estimation'].search_read(
                domain=[],
                fields=['name', 'partner_id', 'estimation_date', 'state', 'estimation_total']
            )
            # Serialize partner_id as dict
            for est in estimations:
                if est.get('partner_id'):
                    est['partner_id'] = {'id': est['partner_id'][0], 'name': est['partner_id'][1]}
            return estimations
        except Exception as e:
            _logger.error(f"Error fetching estimations: {e}")
            return Response(json.dumps({'error': 'Failed to fetch estimations'}), status=500, content_type='application/json')

    @http.route('/api/v1/estimation/<int:estimation_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_estimation(self, estimation_id, **kwargs):
        try:
            estimation = request.env['mrp.estimation'].search_read(
                domain=[('id', '=', estimation_id)],
                fields=['name', 'partner_id', 'estimation_date', 'state', 'estimation_total', 'estimation_line_ids']
            )
            if estimation:
                est = estimation[0]
                if est.get('partner_id'):
                    est['partner_id'] = {'id': est['partner_id'][0], 'name': est['partner_id'][1]}
                # Fetch detailed lines
                lines = request.env['mrp.estimation.line'].search_read(
                    domain=[('estimation_id', '=', estimation_id)],
                    fields=['product_id', 'product_qty', 'product_cost', 'existing_material', 'supplier_id', 'lead_time']
                )
                for line in lines:
                    if line.get('product_id'):
                        line['product_id'] = {'id': line['product_id'][0], 'name': line['product_id'][1]}
                    if line.get('supplier_id'):
                        line['supplier_id'] = {'id': line['supplier_id'][0], 'name': line['supplier_id'][1]}
                est['estimation_line_ids'] = lines
                return est
            else:
                return Response(json.dumps({'error': 'Estimation not found'}), status=404, content_type='application/json')
        except Exception as e:
            _logger.error(f"Error fetching estimation {estimation_id}: {e}")
            return Response(json.dumps({'error': 'Failed to fetch estimation'}), status=500, content_type='application/json')
