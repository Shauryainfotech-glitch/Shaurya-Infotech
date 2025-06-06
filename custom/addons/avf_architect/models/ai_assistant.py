
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AVFAIAssistant(models.Model):
    _name = 'avf.ai.assistant'
    _description = 'AI Assistant for Architect'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Request Name', required=True)
    project_id = fields.Many2one('project.project', string='Project')
    
    request_type = fields.Selection([
        ('design_suggestion', 'Design Suggestion'),
        ('compliance_check', 'Compliance Check'),
        ('cost_estimation', 'Cost Estimation'),
        ('project_optimization', 'Project Optimization'),
        ('risk_analysis', 'Risk Analysis'),
        ('material_recommendation', 'Material Recommendation'),
        ('energy_efficiency', 'Energy Efficiency'),
        ('structural_analysis', 'Structural Analysis'),
        ('other', 'Other')
    ], string='Request Type', required=True)

    query = fields.Text(string='Query/Request', required=True)
    response = fields.Html(string='AI Response')
    
    # Context Information
    building_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('institutional', 'Institutional'),
        ('industrial', 'Industrial'),
        ('mixed_use', 'Mixed Use')
    ], string='Building Type')
    
    area_sqft = fields.Float(string='Area (sq ft)')
    budget_range = fields.Selection([
        ('low', 'Low Budget'),
        ('medium', 'Medium Budget'),
        ('high', 'High Budget'),
        ('premium', 'Premium Budget')
    ], string='Budget Range')
    
    location = fields.Char(string='Location')
    climate_zone = fields.Selection([
        ('tropical', 'Tropical'),
        ('subtropical', 'Subtropical'),
        ('temperate', 'Temperate'),
        ('arid', 'Arid'),
        ('polar', 'Polar')
    ], string='Climate Zone')

    # Status and Quality
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string='Status', default='draft')

    confidence_score = fields.Float(string='Confidence Score (%)')
    user_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent')
    ], string='User Rating')

    # Attachments
    input_files = fields.Binary(string='Input Files', attachment=True)
    input_filename = fields.Char(string='Input Filename')
    output_files = fields.Binary(string='Output Files', attachment=True)
    output_filename = fields.Char(string='Output Filename')

    # User Information
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now)
    completion_date = fields.Datetime(string='Completion Date')

    # Additional Information
    tags = fields.Char(string='Tags')
    notes = fields.Text(string='Notes')
    follow_up_required = fields.Boolean(string='Follow-up Required')

    def action_process_request(self):
        """Process AI request"""
        self.ensure_one()
        self.state = 'processing'
        # Here you would integrate with actual AI services
        self.response = self._generate_mock_response()
        self.state = 'completed'
        self.completion_date = fields.Datetime.now()
        self.confidence_score = 85.0  # Mock confidence score

    def _generate_mock_response(self):
        """Generate mock AI response based on request type"""
        responses = {
            'design_suggestion': """
                <h3>Design Recommendations</h3>
                <ul>
                    <li>Consider open floor plan for better space utilization</li>
                    <li>Implement passive cooling strategies for energy efficiency</li>
                    <li>Use local materials to reduce costs and environmental impact</li>
                    <li>Incorporate natural lighting to reduce electricity consumption</li>
                </ul>
            """,
            'compliance_check': """
                <h3>Compliance Analysis</h3>
                <ul>
                    <li>Building Code Compliance: ✓ Compliant</li>
                    <li>Fire Safety Requirements: ⚠ Needs review</li>
                    <li>Accessibility Standards: ✓ Compliant</li>
                    <li>Environmental Clearance: ⚠ Documentation required</li>
                </ul>
            """,
            'cost_estimation': """
                <h3>Cost Estimation</h3>
                <p>Based on the provided parameters:</p>
                <ul>
                    <li>Construction Cost: ₹1,200 per sq ft</li>
                    <li>Material Cost: 60% of total</li>
                    <li>Labor Cost: 25% of total</li>
                    <li>Other Costs: 15% of total</li>
                </ul>
            """,
        }
        return responses.get(self.request_type, "<p>AI analysis completed. Please review the recommendations.</p>")

    def action_regenerate_response(self):
        """Regenerate AI response"""
        self.ensure_one()
        self.action_process_request()

    def action_export_response(self):
        """Export AI response to document"""
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'avf_architect.ai_response_report',
            'report_type': 'qweb-pdf',
            'data': {'id': self.id},
            'context': {'active_id': self.id},
        }
