# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class AIProcessingQueue(models.Model):
    _name = 'ai.processing.queue'
    _description = 'AI Processing Queue'
    _order = 'priority desc, create_date asc'
    _rec_name = 'name'

    name = fields.Char(string='Queue Item Name', required=True)
    sequence = fields.Char(string='Sequence', default=lambda self: self.env['ir.sequence'].next_by_code('ai.processing.queue'))
    
    # Request Details
    request_type = fields.Selection([
        ('vendor_suggestion', 'Vendor Suggestion'),
        ('risk_assessment', 'Risk Assessment'),
        ('document_analysis', 'Document Analysis'),
        ('vendor_enrichment', 'Vendor Enrichment'),
        ('price_analysis', 'Price Analysis'),
        ('market_analysis', 'Market Analysis'),
        ('compliance_check', 'Compliance Check'),
        ('performance_analysis', 'Performance Analysis'),
    ], string='Request Type', required=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='medium', required=True)
    
    state = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='pending', required=True)
    
    # Input/Output Data
    input_data = fields.Text(string='Input Data (JSON)')
    output_data = fields.Text(string='Output Data (JSON)')
    error_message = fields.Text(string='Error Message')
    
    # Processing Details
    model_name = fields.Char(string='Target Model')
    record_id = fields.Integer(string='Record ID')
    method_name = fields.Char(string='Method Name')
    
    # Timing
    scheduled_date = fields.Datetime(string='Scheduled Date', default=fields.Datetime.now)
    started_date = fields.Datetime(string='Started Date')
    completed_date = fields.Datetime(string='Completed Date')
    processing_time = fields.Float(string='Processing Time (seconds)', compute='_compute_processing_time', store=True)
    
    # AI Service
    ai_service_id = fields.Many2one('purchase.ai.service', string='AI Service')
    ai_provider = fields.Char(string='AI Provider', related='ai_service_id.provider')
    
    # Progress Tracking
    progress = fields.Float(string='Progress (%)', default=0.0)
    progress_message = fields.Char(string='Progress Message')
    
    # Retry Logic
    retry_count = fields.Integer(string='Retry Count', default=0)
    max_retries = fields.Integer(string='Max Retries', default=3)
    
    # User Context
    user_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('started_date', 'completed_date')
    def _compute_processing_time(self):
        for record in self:
            if record.started_date and record.completed_date:
                delta = record.completed_date - record.started_date
                record.processing_time = delta.total_seconds()
            else:
                record.processing_time = 0.0

    def get_input_data_dict(self):
        """Parse input data JSON"""
        if self.input_data:
            try:
                return json.loads(self.input_data)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_input_data_dict(self, data):
        """Set input data as JSON"""
        self.input_data = json.dumps(data, default=str)

    def get_output_data_dict(self):
        """Parse output data JSON"""
        if self.output_data:
            try:
                return json.loads(self.output_data)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_output_data_dict(self, data):
        """Set output data as JSON"""
        self.output_data = json.dumps(data, default=str)

    def action_start_processing(self):
        """Start processing the queue item"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending items can be started'))
        
        self.write({
            'state': 'processing',
            'started_date': fields.Datetime.now(),
            'progress': 0.0,
            'progress_message': 'Starting processing...'
        })

    def action_mark_completed(self, output_data=None):
        """Mark the queue item as completed"""
        self.ensure_one()
        values = {
            'state': 'completed',
            'completed_date': fields.Datetime.now(),
            'progress': 100.0,
            'progress_message': 'Processing completed successfully'
        }
        
        if output_data:
            values['output_data'] = json.dumps(output_data, default=str)
        
        self.write(values)

    def action_mark_failed(self, error_message=None):
        """Mark the queue item as failed"""
        self.ensure_one()
        values = {
            'state': 'failed',
            'completed_date': fields.Datetime.now(),
            'progress_message': 'Processing failed'
        }
        
        if error_message:
            values['error_message'] = error_message
        
        self.write(values)

    def action_retry(self):
        """Retry processing the queue item"""
        self.ensure_one()
        if self.retry_count >= self.max_retries:
            raise UserError(_('Maximum retry attempts reached'))
        
        self.write({
            'state': 'pending',
            'retry_count': self.retry_count + 1,
            'started_date': False,
            'completed_date': False,
            'error_message': False,
            'progress': 0.0,
            'progress_message': f'Retry attempt {self.retry_count + 1}'
        })

    def action_cancel(self):
        """Cancel the queue item"""
        self.ensure_one()
        if self.state == 'processing':
            raise UserError(_('Cannot cancel items that are currently processing'))
        
        self.write({
            'state': 'cancelled',
            'completed_date': fields.Datetime.now(),
            'progress_message': 'Processing cancelled by user'
        })

    def update_progress(self, progress, message=None):
        """Update processing progress"""
        self.ensure_one()
        values = {'progress': min(100.0, max(0.0, progress))}
        if message:
            values['progress_message'] = message
        self.write(values)

    @api.model
    def process_queue(self, limit=10):
        """Process pending queue items"""
        pending_items = self.search([
            ('state', '=', 'pending'),
            ('scheduled_date', '<=', fields.Datetime.now())
        ], limit=limit, order='priority desc, create_date asc')
        
        for item in pending_items:
            try:
                item._process_item()
            except Exception as e:
                _logger.error(f"Error processing queue item {item.id}: {str(e)}")
                item.action_mark_failed(str(e))

    def _process_item(self):
        """Process individual queue item"""
        self.ensure_one()
        self.action_start_processing()
        
        try:
            if self.model_name and self.method_name:
                # Call specific model method
                target_model = self.env[self.model_name]
                if self.record_id:
                    target_record = target_model.browse(self.record_id)
                    method = getattr(target_record, self.method_name)
                else:
                    method = getattr(target_model, self.method_name)
                
                input_data = self.get_input_data_dict()
                result = method(**input_data)
                self.action_mark_completed(result)
            else:
                # Generic processing based on request type
                result = self._process_by_type()
                self.action_mark_completed(result)
                
        except Exception as e:
            _logger.error(f"Error in queue item processing: {str(e)}")
            self.action_mark_failed(str(e))

    def _process_by_type(self):
        """Process based on request type"""
        input_data = self.get_input_data_dict()
        
        if self.request_type == 'vendor_suggestion':
            return self._process_vendor_suggestion(input_data)
        elif self.request_type == 'risk_assessment':
            return self._process_risk_assessment(input_data)
        elif self.request_type == 'document_analysis':
            return self._process_document_analysis(input_data)
        elif self.request_type == 'vendor_enrichment':
            return self._process_vendor_enrichment(input_data)
        else:
            raise UserError(_('Unknown request type: %s') % self.request_type)

    def _process_vendor_suggestion(self, input_data):
        """Process vendor suggestion request"""
        product_id = input_data.get('product_id')
        if not product_id:
            raise UserError(_('Product ID required for vendor suggestion'))
        
        suggestion_model = self.env['purchase.vendor.suggestion']
        return suggestion_model.generate_suggestions_for_product(product_id)

    def _process_risk_assessment(self, input_data):
        """Process risk assessment request"""
        vendor_id = input_data.get('vendor_id')
        if not vendor_id:
            raise UserError(_('Vendor ID required for risk assessment'))
        
        risk_model = self.env['risk.assessment']
        return risk_model.create_assessment(vendor_id)

    def _process_document_analysis(self, input_data):
        """Process document analysis request"""
        document_id = input_data.get('document_id')
        if not document_id:
            raise UserError(_('Document ID required for analysis'))
        
        doc_model = self.env['document.analysis']
        return doc_model.analyze_document(document_id)

    def _process_vendor_enrichment(self, input_data):
        """Process vendor enrichment request"""
        vendor_id = input_data.get('vendor_id')
        if not vendor_id:
            raise UserError(_('Vendor ID required for enrichment'))
        
        enrichment_model = self.env['vendor.enrichment']
        return enrichment_model.enrich_vendor_data(vendor_id)

    @api.model
    def cleanup_old_items(self, days=30):
        """Cleanup old completed/failed items"""
        cutoff_date = fields.Datetime.now() - timedelta(days=days)
        old_items = self.search([
            ('state', 'in', ['completed', 'failed', 'cancelled']),
            ('completed_date', '<', cutoff_date)
        ])
        old_items.unlink()
        return len(old_items)

    @api.model
    def get_queue_statistics(self):
        """Get queue processing statistics"""
        stats = {}
        for state in ['pending', 'processing', 'completed', 'failed']:
            stats[state] = self.search_count([('state', '=', state)])
        
        # Average processing time for completed items
        completed_items = self.search([
            ('state', '=', 'completed'),
            ('processing_time', '>', 0)
        ])
        
        if completed_items:
            stats['avg_processing_time'] = sum(completed_items.mapped('processing_time')) / len(completed_items)
        else:
            stats['avg_processing_time'] = 0.0
        
        return stats 