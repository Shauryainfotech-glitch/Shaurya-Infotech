import json
import base64
import logging
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)


class PurchaseAIController(http.Controller):

    @http.route('/purchase_ai/test_service', type='json', auth='user', methods=['POST'])
    def test_ai_service(self, service_id):
        """Test AI service connection"""
        try:
            service = request.env['purchase.ai.service'].browse(service_id)
            if not service.exists():
                return {'success': False, 'message': _('Service not found')}
            
            result = service.test_connection()
            return {'success': True, 'result': result}
        except Exception as e:
            _logger.error(f"Error testing AI service: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/generate_suggestions', type='json', auth='user', methods=['POST'])
    def generate_vendor_suggestions(self, product_id, requirements=None):
        """Generate vendor suggestions for a product"""
        try:
            suggestions = request.env['purchase.vendor.suggestion'].generate_suggestions(
                product_id, requirements or {}
            )
            return {'success': True, 'suggestions': suggestions}
        except Exception as e:
            _logger.error(f"Error generating vendor suggestions: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/assess_risk', type='json', auth='user', methods=['POST'])
    def assess_vendor_risk(self, vendor_id, assessment_type='manual'):
        """Trigger vendor risk assessment"""
        try:
            assessment = request.env['risk.assessment'].create_assessment(
                vendor_id, assessment_type
            )
            return {'success': True, 'assessment_id': assessment.id}
        except Exception as e:
            _logger.error(f"Error assessing vendor risk: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/enrich_vendor', type='json', auth='user', methods=['POST'])
    def enrich_vendor(self, vendor_id):
        """Start vendor enrichment process"""
        try:
            enrichment = request.env['vendor.enrichment'].start_enrichment(vendor_id)
            return {'success': True, 'enrichment_id': enrichment.id}
        except Exception as e:
            _logger.error(f"Error enriching vendor: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/submit_feedback', type='json', auth='user', methods=['POST'])
    def submit_feedback(self, suggestion_id, rating, feedback_text):
        """Submit feedback for vendor suggestion"""
        try:
            feedback = request.env['vendor.suggestion.feedback'].create({
                'suggestion_id': suggestion_id,
                'rating': rating,
                'feedback_text': feedback_text,
                'feedback_type': 'user',
                'user_id': request.env.user.id
            })
            return {'success': True, 'feedback_id': feedback.id}
        except Exception as e:
            _logger.error(f"Error submitting feedback: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/upload_document', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_document(self, **kwargs):
        """Upload document for AI analysis"""
        try:
            file = request.httprequest.files.get('file')
            if not file:
                return json.dumps({'success': False, 'message': _('No file provided')})
            
            # Read file content
            file_content = file.read()
            file_name = file.filename
            
            # Create document analysis record
            analysis = request.env['document.analysis'].create({
                'name': f'Analysis: {file_name}',
                'document_name': file_name,
                'document_content': base64.b64encode(file_content),
                'analyzed_by': request.env.user.id,
                'state': 'pending'
            })
            
            # Start analysis
            analysis.start_analysis()
            
            return json.dumps({
                'success': True, 
                'analysis_id': analysis.id,
                'message': _('Document uploaded and analysis started')
            })
        except Exception as e:
            _logger.error(f"Error uploading document: {str(e)}")
            return json.dumps({'success': False, 'message': str(e)})

    @http.route('/purchase_ai/get_queue_status', type='json', auth='user', methods=['POST'])
    def get_queue_status(self, queue_id=None):
        """Get AI processing queue status"""
        try:
            if queue_id:
                queue_item = request.env['ai.processing.queue'].browse(queue_id)
                if queue_item.exists():
                    return {
                        'success': True,
                        'status': queue_item.state,
                        'progress': queue_item.progress,
                        'message': queue_item.status_message
                    }
            else:
                # Get overall queue status
                queue_stats = request.env['ai.processing.queue'].get_queue_statistics()
                return {'success': True, 'stats': queue_stats}
        except Exception as e:
            _logger.error(f"Error getting queue status: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/get_ai_metrics', type='json', auth='user', methods=['POST'])
    def get_ai_metrics(self, period='today'):
        """Get AI performance metrics"""
        try:
            metrics = request.env['ai.performance.metrics'].get_metrics_summary(period)
            return {'success': True, 'metrics': metrics}
        except Exception as e:
            _logger.error(f"Error getting AI metrics: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/get_cost_summary', type='json', auth='user', methods=['POST'])
    def get_cost_summary(self, period='today'):
        """Get AI cost summary"""
        try:
            cost_data = request.env['purchase.ai.service'].get_cost_summary(period)
            return {'success': True, 'cost_data': cost_data}
        except Exception as e:
            _logger.error(f"Error getting cost summary: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/refresh_suggestions', type='json', auth='user', methods=['POST'])
    def refresh_suggestions(self, product_id=None):
        """Refresh vendor suggestions"""
        try:
            if product_id:
                # Refresh for specific product
                suggestions = request.env['purchase.vendor.suggestion'].search([
                    ('product_id', '=', product_id),
                    ('state', '=', 'active')
                ])
                suggestions.refresh_suggestions()
            else:
                # Refresh all active suggestions
                request.env['purchase.vendor.suggestion'].auto_refresh_suggestions()
            
            return {'success': True, 'message': _('Suggestions refreshed successfully')}
        except Exception as e:
            _logger.error(f"Error refreshing suggestions: {str(e)}")
            return {'success': False, 'message': str(e)}

    @http.route('/purchase_ai/export_data', type='http', auth='user', methods=['GET'])
    def export_ai_data(self, data_type, format='csv', **kwargs):
        """Export AI data for analysis"""
        try:
            if data_type == 'suggestions':
                data = request.env['purchase.vendor.suggestion'].export_data_for_analysis()
            elif data_type == 'feedback':
                data = request.env['vendor.suggestion.feedback'].export_data_for_analysis()
            elif data_type == 'metrics':
                data = request.env['ai.performance.metrics'].export_data_for_analysis()
            else:
                raise UserError(_('Invalid data type'))
            
            # Generate file based on format
            if format == 'csv':
                import csv
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
                writer.writeheader()
                writer.writerows(data)
                content = output.getvalue()
                content_type = 'text/csv'
                filename = f'{data_type}_export.csv'
            else:
                content = json.dumps(data, indent=2)
                content_type = 'application/json'
                filename = f'{data_type}_export.json'
            
            return request.make_response(
                content,
                headers=[
                    ('Content-Type', content_type),
                    ('Content-Disposition', f'attachment; filename="{filename}"')
                ]
            )
        except Exception as e:
            _logger.error(f"Error exporting data: {str(e)}")
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            ) 