# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class RiskAssessment(models.Model):
    _name = 'risk.assessment'
    _description = 'Vendor Risk Assessment'
    _order = 'assessment_date desc'
    _rec_name = 'name'

    name = fields.Char(string='Assessment Name', required=True)
    sequence = fields.Char(string='Sequence', default=lambda self: self.env['ir.sequence'].next_by_code('risk.assessment'))
    
    # Vendor Information
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, domain=[('is_company', '=', True)])
    vendor_category = fields.Many2one('res.partner.category', string='Vendor Category')
    
    # Assessment Details
    assessment_date = fields.Datetime(string='Assessment Date', default=fields.Datetime.now, required=True)
    assessment_type = fields.Selection([
        ('initial', 'Initial Assessment'),
        ('periodic', 'Periodic Review'),
        ('triggered', 'Triggered Assessment'),
        ('pre_contract', 'Pre-Contract'),
        ('post_incident', 'Post-Incident'),
    ], string='Assessment Type', default='initial', required=True)
    
    # Risk Scores
    overall_risk_score = fields.Float(string='Overall Risk Score', default=0.0, help="0 = Low Risk, 1 = High Risk")
    financial_risk = fields.Float(string='Financial Risk', default=0.0)
    operational_risk = fields.Float(string='Operational Risk', default=0.0)
    compliance_risk = fields.Float(string='Compliance Risk', default=0.0)
    reputation_risk = fields.Float(string='Reputation Risk', default=0.0)
    delivery_risk = fields.Float(string='Delivery Risk', default=0.0)
    quality_risk = fields.Float(string='Quality Risk', default=0.0)
    
    # Risk Categories
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ], string='Risk Level', compute='_compute_risk_level', store=True)
    
    # Assessment Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='State', default='draft', required=True)
    
    # AI Analysis
    ai_analysis_completed = fields.Boolean(string='AI Analysis Completed', default=False)
    ai_confidence_score = fields.Float(string='AI Confidence Score', default=0.0)
    ai_recommendations = fields.Text(string='AI Recommendations')
    ai_risk_factors = fields.Text(string='AI Risk Factors (JSON)')
    
    # Assessment Data
    assessment_data = fields.Text(string='Assessment Data (JSON)')
    risk_mitigation_plan = fields.Text(string='Risk Mitigation Plan')
    
    # Approval Workflow
    requires_approval = fields.Boolean(string='Requires Approval', compute='_compute_requires_approval', store=True)
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Datetime(string='Approval Date')
    rejection_reason = fields.Text(string='Rejection Reason')
    
    # Validity
    is_current = fields.Boolean(string='Is Current Assessment', default=True)
    valid_until = fields.Date(string='Valid Until', compute='_compute_valid_until', store=True)
    next_review_date = fields.Date(string='Next Review Date')
    
    # User Context
    assessed_by = fields.Many2one('res.users', string='Assessed By', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('overall_risk_score')
    def _compute_risk_level(self):
        for record in self:
            if record.overall_risk_score <= 0.3:
                record.risk_level = 'low'
            elif record.overall_risk_score <= 0.6:
                record.risk_level = 'medium'
            elif record.overall_risk_score <= 0.8:
                record.risk_level = 'high'
            else:
                record.risk_level = 'critical'

    @api.depends('risk_level')
    def _compute_requires_approval(self):
        for record in self:
            record.requires_approval = record.risk_level in ['high', 'critical']

    @api.depends('assessment_date', 'assessment_type')
    def _compute_valid_until(self):
        for record in self:
            if record.assessment_date:
                # Different validity periods based on assessment type
                if record.assessment_type == 'initial':
                    days = 365  # 1 year
                elif record.assessment_type == 'periodic':
                    days = 180  # 6 months
                elif record.assessment_type == 'triggered':
                    days = 90   # 3 months
                else:
                    days = 365  # Default 1 year
                
                record.valid_until = record.assessment_date.date() + timedelta(days=days)
            else:
                record.valid_until = False

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            vendor = self.env['res.partner'].browse(vals.get('vendor_id'))
            vals['name'] = f"Risk Assessment: {vendor.name}"
        return super().create(vals)

    def action_start_assessment(self):
        """Start the risk assessment process"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft assessments can be started'))
        
        self.write({
            'state': 'in_progress',
            'assessment_date': fields.Datetime.now(),
        })
        
        # Queue AI analysis
        self.env['ai.processing.queue'].create({
            'name': f'Risk Assessment: {self.vendor_id.name}',
            'request_type': 'risk_assessment',
            'priority': 'high',
            'input_data': json.dumps({'vendor_id': self.vendor_id.id}),
            'model_name': 'risk.assessment',
            'record_id': self.id,
            'method_name': 'run_ai_assessment',
        })

    def run_ai_assessment(self):
        """Run AI-powered risk assessment"""
        self.ensure_one()
        
        try:
            # Gather vendor data for analysis
            vendor_data = self._gather_vendor_data()
            
            # Get AI service for risk assessment
            ai_service = self.env['purchase.ai.service'].get_service_for_usage('risk_assessment')
            if not ai_service:
                raise UserError(_('No AI service configured for risk assessment'))
            
            # Prepare AI prompt
            prompt = self._prepare_risk_assessment_prompt(vendor_data)
            
            # Call AI service
            response = ai_service.call_ai_service(
                prompt=prompt,
                context={'vendor_id': self.vendor_id.id, 'assessment_id': self.id}
            )
            
            if response.get('success'):
                self._process_ai_response(response.get('response', {}))
            else:
                raise UserError(_('AI assessment failed: %s') % response.get('error', 'Unknown error'))
            
            # Calculate overall risk score
            self._calculate_overall_risk()
            
            # Complete assessment
            self.write({
                'state': 'completed',
                'ai_analysis_completed': True,
            })
            
            # Check if approval is required
            if self.requires_approval:
                self._request_approval()
            else:
                self.action_approve()
                
        except Exception as e:
            _logger.error(f"Error in AI risk assessment: {str(e)}")
            self.write({
                'state': 'draft',
                'ai_analysis_completed': False,
            })
            raise

    def _gather_vendor_data(self):
        """Gather comprehensive vendor data for risk assessment"""
        vendor = self.vendor_id
        
        # Basic vendor information
        vendor_data = {
            'basic_info': {
                'name': vendor.name,
                'website': vendor.website,
                'email': vendor.email,
                'phone': vendor.phone,
                'vat': vendor.vat,
                'country': vendor.country_id.name if vendor.country_id else None,
                'industry': vendor.industry_id.name if vendor.industry_id else None,
                'is_company': vendor.is_company,
                'supplier_rank': vendor.supplier_rank,
                'credit_limit': vendor.credit_limit,
            }
        }
        
        # Purchase history
        purchase_orders = self.env['purchase.order'].search([
            ('partner_id', '=', vendor.id)
        ], limit=100)
        
        vendor_data['purchase_history'] = {
            'total_orders': len(purchase_orders),
            'total_amount': sum(purchase_orders.mapped('amount_total')),
            'avg_order_value': sum(purchase_orders.mapped('amount_total')) / len(purchase_orders) if purchase_orders else 0,
            'on_time_delivery_rate': self._calculate_delivery_performance(purchase_orders),
            'quality_issues': self._count_quality_issues(purchase_orders),
            'payment_delays': self._count_payment_delays(purchase_orders),
        }
        
        # Financial data
        vendor_data['financial_data'] = {
            'credit_limit': vendor.credit_limit,
            'payment_term': vendor.property_supplier_payment_term_id.name if vendor.property_supplier_payment_term_id else None,
            'outstanding_invoices': self._get_outstanding_invoices(vendor),
        }
        
        # Compliance data
        vendor_data['compliance_data'] = {
            'certifications': self._get_vendor_certifications(vendor),
            'compliance_documents': self._get_compliance_documents(vendor),
            'audit_results': self._get_audit_results(vendor),
        }
        
        # Market data
        vendor_data['market_data'] = {
            'market_position': 'unknown',  # Would be enriched from external sources
            'competitor_analysis': [],
            'industry_trends': {},
        }
        
        return vendor_data

    def _prepare_risk_assessment_prompt(self, vendor_data):
        """Prepare AI prompt for risk assessment"""
        return f"""
        Conduct a comprehensive risk assessment for the following vendor:
        
        Vendor: {self.vendor_id.name}
        Assessment Type: {self.assessment_type}
        
        Vendor Data:
        {json.dumps(vendor_data, indent=2, default=str)}
        
        Please analyze the following risk categories and provide scores (0-1, where 0 is low risk and 1 is high risk):
        
        1. Financial Risk - Credit worthiness, payment history, financial stability
        2. Operational Risk - Delivery performance, capacity, operational stability
        3. Compliance Risk - Regulatory compliance, certifications, legal issues
        4. Reputation Risk - Market reputation, past incidents, public perception
        5. Delivery Risk - On-time delivery, logistics capabilities, geographic factors
        6. Quality Risk - Product/service quality, defect rates, quality systems
        
        For each risk category, provide:
        - Risk score (0-1)
        - Key risk factors
        - Specific concerns or red flags
        - Mitigation recommendations
        
        Also provide:
        - Overall assessment summary
        - Top 3 risk concerns
        - Recommended actions
        - Confidence score for the assessment (0-1)
        
        Format your response as JSON with the following structure:
        {
            "financial_risk": {"score": 0.0, "factors": [], "concerns": [], "recommendations": []},
            "operational_risk": {"score": 0.0, "factors": [], "concerns": [], "recommendations": []},
            "compliance_risk": {"score": 0.0, "factors": [], "concerns": [], "recommendations": []},
            "reputation_risk": {"score": 0.0, "factors": [], "concerns": [], "recommendations": []},
            "delivery_risk": {"score": 0.0, "factors": [], "concerns": [], "recommendations": []},
            "quality_risk": {"score": 0.0, "factors": [], "concerns": [], "recommendations": []},
            "summary": "Overall assessment summary",
            "top_concerns": ["concern1", "concern2", "concern3"],
            "recommendations": ["recommendation1", "recommendation2"],
            "confidence_score": 0.0
        }
        """

    def _process_ai_response(self, ai_response):
        """Process AI assessment response"""
        try:
            # Extract risk scores
            self.financial_risk = ai_response.get('financial_risk', {}).get('score', 0.0)
            self.operational_risk = ai_response.get('operational_risk', {}).get('score', 0.0)
            self.compliance_risk = ai_response.get('compliance_risk', {}).get('score', 0.0)
            self.reputation_risk = ai_response.get('reputation_risk', {}).get('score', 0.0)
            self.delivery_risk = ai_response.get('delivery_risk', {}).get('score', 0.0)
            self.quality_risk = ai_response.get('quality_risk', {}).get('score', 0.0)
            
            # Store AI analysis data
            self.ai_confidence_score = ai_response.get('confidence_score', 0.0)
            self.ai_recommendations = ai_response.get('summary', '')
            self.ai_risk_factors = json.dumps(ai_response, default=str)
            
            # Store detailed assessment data
            self.assessment_data = json.dumps(ai_response, default=str)
            
        except Exception as e:
            _logger.error(f"Error processing AI response: {str(e)}")
            raise UserError(_('Failed to process AI assessment response'))

    def _calculate_overall_risk(self):
        """Calculate overall risk score from individual risk components"""
        # Get scoring weights
        weights = self.env['vendor.scoring.weights'].get_current_weights()
        
        # Calculate weighted average
        total_score = (
            self.financial_risk * 0.25 +
            self.operational_risk * 0.20 +
            self.compliance_risk * 0.20 +
            self.reputation_risk * 0.15 +
            self.delivery_risk * 0.15 +
            self.quality_risk * 0.05
        )
        
        self.overall_risk_score = min(1.0, max(0.0, total_score))

    def _request_approval(self):
        """Request approval for high-risk assessments"""
        # Create activity for approval
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': f'Risk Assessment Approval Required: {self.vendor_id.name}',
            'note': f'Risk Level: {self.risk_level.title()}\nOverall Score: {self.overall_risk_score:.2f}',
            'res_model_id': self.env.ref('purchase_ai.model_risk_assessment').id,
            'res_id': self.id,
            'user_id': self.env.ref('purchase.group_purchase_manager').users[0].id if self.env.ref('purchase.group_purchase_manager').users else self.env.user.id,
        })

    def action_approve(self):
        """Approve the risk assessment"""
        self.ensure_one()
        if self.state != 'completed':
            raise UserError(_('Only completed assessments can be approved'))
        
        # Mark previous assessments as not current
        previous_assessments = self.search([
            ('vendor_id', '=', self.vendor_id.id),
            ('id', '!=', self.id),
            ('is_current', '=', True)
        ])
        previous_assessments.write({'is_current': False})
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now(),
            'is_current': True,
        })
        
        # Update vendor risk category
        self._update_vendor_risk_category()

    def action_reject(self):
        """Reject the risk assessment"""
        self.ensure_one()
        if self.state != 'completed':
            raise UserError(_('Only completed assessments can be rejected'))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Assessment',
            'res_model': 'risk.assessment.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_assessment_id': self.id}
        }

    def _update_vendor_risk_category(self):
        """Update vendor's risk category based on assessment"""
        vendor = self.vendor_id
        
        # Get or create risk categories
        if self.risk_level == 'low':
            category = self.env.ref('purchase_ai.vendor_category_low_risk', raise_if_not_found=False)
        elif self.risk_level in ['high', 'critical']:
            category = self.env.ref('purchase_ai.vendor_category_high_risk', raise_if_not_found=False)
        else:
            category = None
        
        if category:
            vendor.category_id = [(4, category.id)]

    def _calculate_delivery_performance(self, purchase_orders):
        """Calculate on-time delivery rate"""
        if not purchase_orders:
            return 0.0
        
        on_time_count = 0
        for order in purchase_orders:
            if order.effective_date and order.date_planned:
                if order.effective_date <= order.date_planned:
                    on_time_count += 1
        
        return on_time_count / len(purchase_orders) if purchase_orders else 0.0

    def _count_quality_issues(self, purchase_orders):
        """Count quality-related issues"""
        # This would integrate with quality management module
        return 0

    def _count_payment_delays(self, purchase_orders):
        """Count payment delays"""
        # This would analyze invoice payment history
        return 0

    def _get_outstanding_invoices(self, vendor):
        """Get outstanding invoice information"""
        invoices = self.env['account.move'].search([
            ('partner_id', '=', vendor.id),
            ('move_type', '=', 'in_invoice'),
            ('payment_state', '!=', 'paid')
        ])
        
        return {
            'count': len(invoices),
            'total_amount': sum(invoices.mapped('amount_total')),
        }

    def _get_vendor_certifications(self, vendor):
        """Get vendor certifications"""
        # This would integrate with document management
        return []

    def _get_compliance_documents(self, vendor):
        """Get compliance documents"""
        documents = self.env['ir.attachment'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', vendor.id),
        ])
        
        return [{'name': doc.name, 'type': doc.mimetype} for doc in documents]

    def _get_audit_results(self, vendor):
        """Get audit results"""
        # This would integrate with audit management
        return []

    @api.model
    def create_assessment(self, vendor_id, assessment_type='initial'):
        """Public method to create risk assessment"""
        vendor = self.env['res.partner'].browse(vendor_id)
        if not vendor.exists():
            raise UserError(_('Vendor not found'))
        
        assessment = self.create({
            'vendor_id': vendor_id,
            'assessment_type': assessment_type,
        })
        
        assessment.action_start_assessment()
        return assessment

    @api.model
    def get_current_assessment(self, vendor_id):
        """Get current risk assessment for vendor"""
        return self.search([
            ('vendor_id', '=', vendor_id),
            ('is_current', '=', True),
            ('state', '=', 'approved')
        ], limit=1) 