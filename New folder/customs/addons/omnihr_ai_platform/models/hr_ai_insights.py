from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class HRAIInsights(models.Model):
    _name = 'hr.ai.insights'
    _description = 'HR AI-Generated Insights'
    _rec_name = 'insight_title'
    _order = 'priority desc, create_date desc'
    
    insight_title = fields.Char('Insight Title', required=True)
    insight_type = fields.Selection([
        ('performance_trend', 'Performance Trend'),
        ('turnover_risk', 'Turnover Risk'),
        ('engagement_alert', 'Engagement Alert'),
        ('skill_gap', 'Skill Gap Analysis'),
        ('diversity_insight', 'Diversity & Inclusion'),
        ('compensation_analysis', 'Compensation Analysis'),
        ('productivity_pattern', 'Productivity Pattern'),
        ('training_effectiveness', 'Training Effectiveness'),
        ('recruitment_insight', 'Recruitment Insight'),
        ('compliance_alert', 'Compliance Alert'),
    ], 'Insight Type', required=True)
    
    # Content
    insight_summary = fields.Text('Insight Summary', required=True)
    detailed_analysis = fields.Html('Detailed Analysis')
    key_findings = fields.Text('Key Findings')
    recommendations = fields.Text('Recommendations')
    
    # Scope
    scope = fields.Selection([
        ('individual', 'Individual Employee'),
        ('team', 'Team/Department'),
        ('company', 'Company-wide'),
        ('industry', 'Industry Benchmark'),
    ], 'Scope', default='company')
    
    employee_id = fields.Many2one('hr.employee', 'Related Employee')
    department_id = fields.Many2one('hr.department', 'Related Department')
    
    # Priority and Impact
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], 'Priority', default='medium')
    
    impact_level = fields.Selection([
        ('minimal', 'Minimal'),
        ('moderate', 'Moderate'),
        ('significant', 'Significant'),
        ('major', 'Major'),
    ], 'Impact Level', default='moderate')
    
    urgency = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('immediate', 'Immediate'),
    ], 'Urgency', default='medium')
    
    # AI Analysis
    ai_confidence = fields.Float('AI Confidence Score')
    data_quality_score = fields.Float('Data Quality Score')
    statistical_significance = fields.Float('Statistical Significance')
    
    # Data Sources
    data_sources = fields.Text('Data Sources Used')
    analysis_period_start = fields.Date('Analysis Period Start')
    analysis_period_end = fields.Date('Analysis Period End')
    sample_size = fields.Integer('Sample Size')
    
    # Metrics and KPIs
    baseline_metric = fields.Float('Baseline Metric')
    current_metric = fields.Float('Current Metric')
    trend_direction = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ], 'Trend Direction')
    
    percentage_change = fields.Float('Percentage Change')
    
    # Visualization
    chart_data = fields.Text('Chart Data (JSON)')
    visualization_type = fields.Selection([
        ('line_chart', 'Line Chart'),
        ('bar_chart', 'Bar Chart'),
        ('pie_chart', 'Pie Chart'),
        ('scatter_plot', 'Scatter Plot'),
        ('heatmap', 'Heatmap'),
        ('gauge', 'Gauge'),
    ], 'Visualization Type')
    
    # Action Items
    action_required = fields.Boolean('Action Required', default=False)
    suggested_actions = fields.Text('Suggested Actions')
    assigned_to = fields.Many2one('res.users', 'Assigned To')
    due_date = fields.Date('Due Date')
    
    # Status
    insight_status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ], 'Status', default='active')
    
    # Feedback
    user_rating = fields.Selection([
        ('1', 'Not Useful'),
        ('2', 'Somewhat Useful'),
        ('3', 'Useful'),
        ('4', 'Very Useful'),
        ('5', 'Extremely Useful'),
    ], 'User Rating')
    
    feedback_comments = fields.Text('Feedback Comments')
    
    @api.model
    def generate_insights(self, insight_types=None, scope='company'):
        """Generate AI insights for specified types and scope"""
        if not insight_types:
            insight_types = [
                'performance_trend',
                'turnover_risk',
                'engagement_alert',
                'skill_gap',
                'productivity_pattern'
            ]
        
        generated_insights = []
        
        for insight_type in insight_types:
            try:
                insight_data = self._generate_insight_by_type(insight_type, scope)
                if insight_data:
                    insight = self.create(insight_data)
                    generated_insights.append(insight)
            except Exception as e:
                _logger.error(f"Failed to generate insight {insight_type}: {str(e)}")
                continue
        
        return generated_insights
    
    def _generate_insight_by_type(self, insight_type, scope):
        """Generate specific type of insight"""
        ai_orchestrator = self.env['hr.ai.orchestrator']
        
        if insight_type == 'performance_trend':
            return self._generate_performance_trend_insight(ai_orchestrator, scope)
        elif insight_type == 'turnover_risk':
            return self._generate_turnover_risk_insight(ai_orchestrator, scope)
        elif insight_type == 'engagement_alert':
            return self._generate_engagement_alert_insight(ai_orchestrator, scope)
        elif insight_type == 'skill_gap':
            return self._generate_skill_gap_insight(ai_orchestrator, scope)
        elif insight_type == 'diversity_insight':
            return self._generate_diversity_insight(ai_orchestrator, scope)
        elif insight_type == 'compensation_analysis':
            return self._generate_compensation_insight(ai_orchestrator, scope)
        elif insight_type == 'productivity_pattern':
            return self._generate_productivity_insight(ai_orchestrator, scope)
        elif insight_type == 'training_effectiveness':
            return self._generate_training_effectiveness_insight(ai_orchestrator, scope)
        elif insight_type == 'recruitment_insight':
            return self._generate_recruitment_insight(ai_orchestrator, scope)
        elif insight_type == 'compliance_alert':
            return self._generate_compliance_alert_insight(ai_orchestrator, scope)
        
        return None
    
    def _generate_performance_trend_insight(self, ai_orchestrator, scope):
        """Generate performance trend insight"""
        # Gather performance data
        performance_data = self._gather_performance_trend_data(scope)
        
        # Generate AI insight
        insight_result = ai_orchestrator.analyze_performance_trends(performance_data)
        
        return {
            'insight_title': 'Performance Trend Analysis',
            'insight_type': 'performance_trend',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'medium'),
            'impact_level': insight_result.get('impact_level', 'moderate'),
            'ai_confidence': insight_result.get('confidence', 0),
            'trend_direction': insight_result.get('trend_direction', 'stable'),
            'percentage_change': insight_result.get('percentage_change', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'line_chart',
            'action_required': insight_result.get('action_required', False),
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_turnover_risk_insight(self, ai_orchestrator, scope):
        """Generate turnover risk insight"""
        turnover_data = self._gather_turnover_risk_data(scope)
        insight_result = ai_orchestrator.analyze_turnover_risk(turnover_data)
        
        return {
            'insight_title': 'Employee Turnover Risk Analysis',
            'insight_type': 'turnover_risk',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'high'),
            'impact_level': insight_result.get('impact_level', 'significant'),
            'urgency': insight_result.get('urgency', 'high'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'gauge',
            'action_required': True,
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_engagement_alert_insight(self, ai_orchestrator, scope):
        """Generate engagement alert insight"""
        engagement_data = self._gather_engagement_data(scope)
        insight_result = ai_orchestrator.analyze_employee_engagement(engagement_data)
        
        return {
            'insight_title': 'Employee Engagement Alert',
            'insight_type': 'engagement_alert',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'medium'),
            'impact_level': insight_result.get('impact_level', 'moderate'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'bar_chart',
            'action_required': insight_result.get('action_required', False),
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_skill_gap_insight(self, ai_orchestrator, scope):
        """Generate skill gap insight"""
        skill_data = self._gather_skill_gap_data(scope)
        insight_result = ai_orchestrator.analyze_skill_gaps(skill_data)
        
        return {
            'insight_title': 'Skills Gap Analysis',
            'insight_type': 'skill_gap',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'medium'),
            'impact_level': insight_result.get('impact_level', 'significant'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'heatmap',
            'action_required': True,
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_diversity_insight(self, ai_orchestrator, scope):
        """Generate diversity and inclusion insight"""
        diversity_data = self._gather_diversity_data(scope)
        insight_result = ai_orchestrator.analyze_diversity_inclusion(diversity_data)
        
        return {
            'insight_title': 'Diversity & Inclusion Analysis',
            'insight_type': 'diversity_insight',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'medium'),
            'impact_level': insight_result.get('impact_level', 'moderate'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'pie_chart',
            'action_required': insight_result.get('action_required', False),
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_compensation_insight(self, ai_orchestrator, scope):
        """Generate compensation analysis insight"""
        compensation_data = self._gather_compensation_data(scope)
        insight_result = ai_orchestrator.analyze_compensation(compensation_data)
        
        return {
            'insight_title': 'Compensation Analysis',
            'insight_type': 'compensation_analysis',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'medium'),
            'impact_level': insight_result.get('impact_level', 'significant'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'scatter_plot',
            'action_required': insight_result.get('action_required', False),
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_productivity_insight(self, ai_orchestrator, scope):
        """Generate productivity pattern insight"""
        productivity_data = self._gather_productivity_data(scope)
        insight_result = ai_orchestrator.analyze_productivity_patterns(productivity_data)
        
        return {
            'insight_title': 'Productivity Pattern Analysis',
            'insight_type': 'productivity_pattern',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'medium'),
            'impact_level': insight_result.get('impact_level', 'moderate'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'line_chart',
            'action_required': insight_result.get('action_required', False),
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_training_effectiveness_insight(self, ai_orchestrator, scope):
        """Generate training effectiveness insight"""
        training_data = self._gather_training_effectiveness_data(scope)
        insight_result = ai_orchestrator.analyze_training_effectiveness(training_data)
        
        return {
            'insight_title': 'Training Effectiveness Analysis',
            'insight_type': 'training_effectiveness',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'medium'),
            'impact_level': insight_result.get('impact_level', 'moderate'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'bar_chart',
            'action_required': insight_result.get('action_required', False),
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_recruitment_insight(self, ai_orchestrator, scope):
        """Generate recruitment insight"""
        recruitment_data = self._gather_recruitment_data(scope)
        insight_result = ai_orchestrator.analyze_recruitment_effectiveness(recruitment_data)
        
        return {
            'insight_title': 'Recruitment Effectiveness Analysis',
            'insight_type': 'recruitment_insight',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'medium'),
            'impact_level': insight_result.get('impact_level', 'moderate'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'bar_chart',
            'action_required': insight_result.get('action_required', False),
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    def _generate_compliance_alert_insight(self, ai_orchestrator, scope):
        """Generate compliance alert insight"""
        compliance_data = self._gather_compliance_data(scope)
        insight_result = ai_orchestrator.analyze_compliance_status(compliance_data)
        
        return {
            'insight_title': 'Compliance Alert',
            'insight_type': 'compliance_alert',
            'scope': scope,
            'insight_summary': insight_result.get('summary', ''),
            'detailed_analysis': insight_result.get('detailed_analysis', ''),
            'key_findings': insight_result.get('key_findings', ''),
            'recommendations': insight_result.get('recommendations', ''),
            'priority': insight_result.get('priority', 'high'),
            'impact_level': insight_result.get('impact_level', 'major'),
            'urgency': insight_result.get('urgency', 'immediate'),
            'ai_confidence': insight_result.get('confidence', 0),
            'chart_data': json.dumps(insight_result.get('chart_data', {})),
            'visualization_type': 'gauge',
            'action_required': True,
            'suggested_actions': insight_result.get('suggested_actions', ''),
        }
    
    # Data gathering methods
    def _gather_performance_trend_data(self, scope):
        """Gather performance trend data"""
        return {
            'scope': scope,
            'performance_records': [],
            'time_period': '6_months',
            'metrics': ['productivity', 'quality', 'collaboration'],
        }
    
    def _gather_turnover_risk_data(self, scope):
        """Gather turnover risk data"""
        return {
            'scope': scope,
            'employee_data': [],
            'historical_turnover': [],
            'risk_factors': [],
        }
    
    def _gather_engagement_data(self, scope):
        """Gather engagement data"""
        return {
            'scope': scope,
            'sentiment_data': [],
            'survey_responses': [],
            'participation_rates': {},
        }
    
    def _gather_skill_gap_data(self, scope):
        """Gather skill gap data"""
        return {
            'scope': scope,
            'current_skills': {},
            'required_skills': {},
            'training_data': [],
        }
    
    def _gather_diversity_data(self, scope):
        """Gather diversity data"""
        return {
            'scope': scope,
            'demographics': {},
            'representation_data': {},
            'inclusion_metrics': {},
        }
    
    def _gather_compensation_data(self, scope):
        """Gather compensation data"""
        return {
            'scope': scope,
            'salary_data': [],
            'market_benchmarks': {},
            'equity_analysis': {},
        }
    
    def _gather_productivity_data(self, scope):
        """Gather productivity data"""
        return {
            'scope': scope,
            'productivity_metrics': [],
            'time_tracking_data': [],
            'output_measurements': {},
        }
    
    def _gather_training_effectiveness_data(self, scope):
        """Gather training effectiveness data"""
        return {
            'scope': scope,
            'training_programs': [],
            'completion_rates': {},
            'performance_impact': [],
        }
    
    def _gather_recruitment_data(self, scope):
        """Gather recruitment data"""
        return {
            'scope': scope,
            'hiring_metrics': {},
            'candidate_pipeline': [],
            'source_effectiveness': {},
        }
    
    def _gather_compliance_data(self, scope):
        """Gather compliance data"""
        return {
            'scope': scope,
            'compliance_requirements': [],
            'current_status': {},
            'risk_areas': [],
        }
    
    def acknowledge_insight(self):
        """Acknowledge the insight"""
        self.insight_status = 'acknowledged'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Insight acknowledged'),
                'type': 'success'
            }
        }
    
    def dismiss_insight(self, reason=None):
        """Dismiss the insight"""
        self.insight_status = 'dismissed'
        if reason:
            self.feedback_comments = reason
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Insight dismissed'),
                'type': 'info'
            }
        }
    
    def rate_insight(self, rating, comments=None):
        """Rate the insight"""
        self.user_rating = rating
        if comments:
            self.feedback_comments = comments
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Thank you for your feedback!'),
                'type': 'success'
            }
        } 