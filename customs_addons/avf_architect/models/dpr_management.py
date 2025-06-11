# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
from datetime import datetime, timedelta


class ArchitectDPR(models.Model):
    _name = 'architect.dpr'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Detailed Project Report (DPR)'
    _order = 'create_date desc'

    name = fields.Char(string='DPR Title', required=True, tracking=True)
    code = fields.Char(string='DPR Code', required=True, copy=False)
    project_id = fields.Many2one('architect.project', string='Project', required=True, tracking=True)

    # DPR Type and Classification
    dpr_type = fields.Selection([
        ('preliminary', 'Preliminary DPR'),
        ('detailed', 'Detailed DPR'),
        ('revised', 'Revised DPR'),
        ('final', 'Final DPR')
    ], string='DPR Type', required=True, default='preliminary')

    classification = fields.Selection([
        ('new_construction', 'New Construction'),
        ('renovation', 'Renovation'),
        ('expansion', 'Expansion'),
        ('restoration', 'Restoration'),
        ('infrastructure', 'Infrastructure')
    ], string='Classification', required=True)

    # Basic Information
    department = fields.Char(string='Department/Ministry', required=True)
    scheme_name = fields.Char(string='Scheme Name', required=True)
    location = fields.Text(string='Project Location', required=True)

    # Financial Details
    total_cost = fields.Monetary(string='Total Project Cost', currency_field='currency_id', required=True)
    central_share = fields.Monetary(string='Central Share', currency_field='currency_id')
    state_share = fields.Monetary(string='State Share', currency_field='currency_id')
    beneficiary_share = fields.Monetary(string='Beneficiary Share', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # Timeline
    implementation_period = fields.Integer(string='Implementation Period (Months)')
    start_date = fields.Date(string='Proposed Start Date')
    completion_date = fields.Date(string='Proposed Completion Date')

    # Technical Details
    technical_specification = fields.Html(string='Technical Specification')
    scope_of_work = fields.Html(string='Scope of Work')
    design_parameters = fields.Html(string='Design Parameters')
    quality_standards = fields.Html(string='Quality Standards')

    # Environmental and Social
    environmental_clearance = fields.Boolean(string='Environmental Clearance Required')
    social_impact_assessment = fields.Boolean(string='Social Impact Assessment Required')
    land_acquisition = fields.Boolean(string='Land Acquisition Required')
    rehabilitation_plan = fields.Html(string='Rehabilitation Plan')

    # Compliance and Approvals
    statutory_approvals = fields.Html(string='Statutory Approvals Required')
    regulatory_compliance = fields.Html(string='Regulatory Compliance')

    # Risk Assessment
    risk_assessment = fields.Html(string='Risk Assessment')
    mitigation_measures = fields.Html(string='Mitigation Measures')

    # Implementation Strategy
    implementation_strategy = fields.Html(string='Implementation Strategy')
    monitoring_mechanism = fields.Html(string='Monitoring Mechanism')

    # State and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('revised', 'Revision Required'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    # AI Enhancement
    ai_generated = fields.Boolean(string='AI Generated Sections')
    ai_suggestions = fields.Text(string='AI Suggestions')

    # Attachments and Documents
    document_count = fields.Integer(string='Documents', compute='_compute_document_count')

    # Review and Approval
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    review_date = fields.Date(string='Review Date')
    review_comments = fields.Text(string='Review Comments')
    approver_id = fields.Many2one('res.users', string='Approver')
    approval_date = fields.Date(string='Approval Date')

    @api.model
    # def create(self, vals):
    #     if 'code' not in vals or not vals['code']:
    #         vals['code'] = self.env['ir.sequence'].next_by_code('architect.dpr') or 'New'
    #     return super().create(vals)
    def create(self, vals):
        if 'code' not in vals or not vals['code']:
            vals['code'] = self.env['ir.sequence'].next_by_code('architect.dpr') or 'New'
        return super().create(vals)

    def _compute_document_count(self):
        for dpr in self:
            dpr.document_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'architect.dpr'),
                ('res_id', '=', dpr.id)
            ])

    @api.onchange('total_cost', 'central_share', 'state_share')
    def _onchange_cost_distribution(self):
        if self.total_cost and self.central_share and self.state_share:
            self.beneficiary_share = self.total_cost - self.central_share - self.state_share

    def action_submit_for_review(self):
        self.state = 'under_review'
        self.message_post(body=_("DPR submitted for review."))

    def action_approve(self):
        self.state = 'approved'
        self.approval_date = fields.Date.today()
        self.approver_id = self.env.user
        self.message_post(body=_("DPR approved."))

    def action_reject(self):
        self.state = 'rejected'
        self.message_post(body=_("DPR rejected."))

    def action_request_revision(self):
        self.state = 'revised'
        self.message_post(body=_("DPR revision requested."))

    def action_generate_ai_content(self):
        """Generate AI-powered DPR content"""
        # This would integrate with actual AI service
        ai_content = {
            'technical_specification': self._generate_technical_spec(),
            'scope_of_work': self._generate_scope_of_work(),
            'risk_assessment': self._generate_risk_assessment(),
            'implementation_strategy': self._generate_implementation_strategy()
        }

        for field, content in ai_content.items():
            setattr(self, field, content)

        self.ai_generated = True
        self.ai_suggestions = "AI has generated preliminary content. Please review and customize as needed."
        return True

    def _generate_technical_spec(self):
        return """
        <h3>Technical Specifications</h3>
        <ul>
            <li>Structural Design: As per IS codes and NBC standards</li>
            <li>Materials: Sustainable and locally sourced where possible</li>
            <li>Construction Technology: Modern construction practices</li>
            <li>Safety Standards: Compliance with safety regulations</li>
            <li>Accessibility: Universal design principles</li>
        </ul>
        """

    def _generate_scope_of_work(self):
        return """
        <h3>Scope of Work</h3>
        <ol>
            <li>Site survey and soil investigation</li>
            <li>Detailed architectural and structural design</li>
            <li>Construction and project management</li>
            <li>Quality control and testing</li>
            <li>Commissioning and handover</li>
        </ol>
        """

    def _generate_risk_assessment(self):
        return """
        <h3>Risk Assessment</h3>
        <table border="1" width="100%">
            <tr><th>Risk</th><th>Impact</th><th>Probability</th><th>Mitigation</th></tr>
            <tr><td>Weather delays</td><td>Medium</td><td>High</td><td>Weather monitoring and contingency planning</td></tr>
            <tr><td>Material shortage</td><td>High</td><td>Medium</td><td>Multiple supplier arrangements</td></tr>
            <tr><td>Regulatory changes</td><td>Medium</td><td>Low</td><td>Regular compliance monitoring</td></tr>
        </table>
        """

    def _generate_implementation_strategy(self):
        return """
        <h3>Implementation Strategy</h3>
        <h4>Phase 1: Planning and Design (Months 1-3)</h4>
        <ul>
            <li>Detailed surveys and investigations</li>
            <li>Finalization of designs and approvals</li>
            <li>Tender preparation and contractor selection</li>
        </ul>

        <h4>Phase 2: Construction (Months 4-18)</h4>
        <ul>
            <li>Site mobilization and setup</li>
            <li>Progressive construction with quality checks</li>
            <li>Regular monitoring and reporting</li>
        </ul>

        <h4>Phase 3: Completion and Handover (Months 19-20)</h4>
        <ul>
            <li>Final inspections and testing</li>
            <li>Documentation and training</li>
            <li>Project handover and closure</li>
        </ul>
        """