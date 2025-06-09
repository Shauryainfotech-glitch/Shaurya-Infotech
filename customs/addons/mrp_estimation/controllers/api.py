from odoo import http
from odoo.http import request
import json


class EstimationAPI(http.Controller):

    @http.route('/api/v1/estimations', type='http', auth='user', methods=['GET'], csrf=False)
    def get_estimations(self, **kwargs):
        """Get list of estimations"""
        try:
            domain = []

            # Add partner filter if not manager
            if not request.env.user.has_group('mrp_estimation.group_estimation_manager'):
                domain.append(('user_id', '=', request.env.user.id))

            # Add additional filters from kwargs
            if kwargs.get('partner_id'):
                domain.append(('partner_id', '=', int(kwargs['partner_id'])))
            if kwargs.get('state'):
                domain.append(('state', '=', kwargs['state']))
            if kwargs.get('product_id'):
                domain.append(('product_id', '=', int(kwargs['product_id'])))

            estimations = request.env['mrp.estimation'].search_read(
                domain=domain,
                fields=['name', 'partner_id', 'product_id', 'estimation_date', 'state', 'estimation_total',
                        'currency_id'],
                limit=kwargs.get('limit', 100),
                offset=kwargs.get('offset', 0)
            )

            response_data = {
                'success': True,
                'data': estimations,
                'count': len(estimations)
            }

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

        return json.dumps(response_data, default=str)

    @http.route('/api/v1/estimation/<int:estimation_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_estimation(self, estimation_id, **kwargs):
        """Get single estimation details"""
        try:
            domain = [('id', '=', estimation_id)]

            # Add partner filter if not manager
            if not request.env.user.has_group('mrp_estimation.group_estimation_manager'):
                domain.append(('user_id', '=', request.env.user.id))

            estimation = request.env['mrp.estimation'].search_read(
                domain=domain,
                fields=[
                    'name', 'partner_id', 'product_id', 'product_qty', 'product_uom_id',
                    'estimation_date', 'validity_date', 'state', 'version', 'currency_id',
                    'material_total', 'cost_total', 'markup_total', 'estimation_total',
                    'estimation_line_ids', 'estimation_cost_ids', 'notes', 'customer_notes'
                ]
            )

            if not estimation:
                response_data = {
                    'success': False,
                    'error': 'Estimation not found or access denied'
                }
            else:
                # Get estimation lines
                if estimation[0]['estimation_line_ids']:
                    lines = request.env['mrp.estimation.line'].search_read(
                        domain=[('id', 'in', estimation[0]['estimation_line_ids'])],
                        fields=['product_id', 'product_qty', 'product_uom_id', 'product_cost', 'marked_up_cost',
                                'subtotal']
                    )
                    estimation[0]['estimation_lines'] = lines

                # Get estimation costs
                if estimation[0]['estimation_cost_ids']:
                    costs = request.env['mrp.estimation.cost'].search_read(
                        domain=[('id', 'in', estimation[0]['estimation_cost_ids'])],
                        fields=['name', 'cost_type', 'total_cost']
                    )
                    estimation[0]['estimation_costs'] = costs

                response_data = {
                    'success': True,
                    'data': estimation[0]
                }

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

        return json.dumps(response_data, default=str)

    @http.route('/api/v1/estimation/<int:estimation_id>/approve', type='http', auth='user', methods=['POST'],
                csrf=False)
    def approve_estimation(self, estimation_id, **kwargs):
        """Approve an estimation"""
        try:
            if not request.env.user.has_group('mrp_estimation.group_estimation_manager'):
                return json.dumps({
                    'success': False,
                    'error': 'Access denied. Only estimation managers can approve estimations.'
                })

            estimation = request.env['mrp.estimation'].browse(estimation_id)
            if not estimation.exists():
                return json.dumps({
                    'success': False,
                    'error': 'Estimation not found'
                })

            if estimation.state != 'waiting_approval':
                return json.dumps({
                    'success': False,
                    'error': f'Cannot approve estimation in {estimation.state} state'
                })

            estimation.action_approve()

            response_data = {
                'success': True,
                'message': 'Estimation approved successfully',
                'data': {
                    'id': estimation.id,
                    'state': estimation.state,
                    'name': estimation.name
                }
            }

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

        return json.dumps(response_data, default=str)

    @http.route('/api/v1/estimations/stats', type='http', auth='user', methods=['GET'], csrf=False)
    def get_estimation_stats(self, **kwargs):
        """Get estimation statistics"""
        try:
            domain = []

            # Add partner filter if not manager
            if not request.env.user.has_group('mrp_estimation.group_estimation_manager'):
                domain.append(('user_id', '=', request.env.user.id))

            # Get counts by state
            states = ['draft', 'waiting_approval', 'approved', 'sent', 'confirmed', 'done', 'cancel']
            stats = {}

            for state in states:
                count = request.env['mrp.estimation'].search_count(domain + [('state', '=', state)])
                stats[state] = count

            # Get total amount
            estimations = request.env['mrp.estimation'].search(domain)
            total_amount = sum(estimations.mapped('estimation_total'))

            response_data = {
                'success': True,
                'data': {
                    'counts_by_state': stats,
                    'total_count': sum(stats.values()),
                    'total_amount': total_amount,
                    'currency': request.env.company.currency_id.name
                }
            }

        except Exception as e:
            response_data = {
                'success': False,
                'error': str(e)
            }

        return json.dumps(response_data, default=str)