from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class HRSentimentAnalysis(models.Model):
    _name = 'hr.sentiment.analysis'
    _description = 'Employee Sentiment Analysis'
    _rec_name = 'employee_id'
    _order = 'analysis_date desc'
    
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', 'Department', related='employee_id.department_id', store=True)
    company_id = fields.Many2one('res.company', 'Company', related='employee_id.company_id', store=True)
    
    # Sentiment Scores
    overall_sentiment_score = fields.Float('Overall Sentiment Score', help='Range: -1 (very negative) to 1 (very positive)')
    emotional_state = fields.Selection([
        ('very_positive', 'Very Positive'),
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('very_negative', 'Very Negative'),
    ], 'Emotional State', compute='_compute_emotional_state', store=True)
    
    # Detailed Sentiment Breakdown
    job_satisfaction_score = fields.Float('Job Satisfaction')
    work_life_balance_score = fields.Float('Work-Life Balance')
    team_relationship_score = fields.Float('Team Relationships')
    management_satisfaction_score = fields.Float('Management Satisfaction')
    career_growth_score = fields.Float('Career Growth Satisfaction')
    compensation_satisfaction_score = fields.Float('Compensation Satisfaction')
    
    # Trend Analysis
    sentiment_trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ], 'Sentiment Trend')
    trend_analysis = fields.Text('Trend Analysis')
    
    # Risk Indicators
    burnout_risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], 'Burnout Risk Level')
    stress_indicators = fields.Text('Stress Indicators')
    engagement_level = fields.Float('Engagement Level')
    
    # Data Sources
    communication_sentiment = fields.Float('Communication Sentiment')
    survey_responses = fields.Text('Survey Response Analysis')
    feedback_sentiment = fields.Float('Feedback Sentiment')
    social_interaction_sentiment = fields.Float('Social Interaction Sentiment')
    
    # Alerts and Recommendations
    alert_level = fields.Selection([
        ('none', 'No Alert'),
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
    ], 'Alert Level', default='none')
    recommended_actions = fields.Text('Recommended Actions')
    intervention_suggestions = fields.Text('Intervention Suggestions')
    
    # Analysis Metadata
    analysis_date = fields.Datetime('Analysis Date', default=fields.Datetime.now)
    data_sources_used = fields.Text('Data Sources Used')
    confidence_level = fields.Float('Analysis Confidence Level')
    
    # Status
    analysis_status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], 'Analysis Status', default='pending')
    
    @api.depends('overall_sentiment_score')
    def _compute_emotional_state(self):
        for record in self:
            score = record.overall_sentiment_score
            if score >= 0.6:
                record.emotional_state = 'very_positive'
            elif score >= 0.2:
                record.emotional_state = 'positive'
            elif score >= -0.2:
                record.emotional_state = 'neutral'
            elif score >= -0.6:
                record.emotional_state = 'negative'
            else:
                record.emotional_state = 'very_negative'
    
    def run_sentiment_analysis(self):
        """Run comprehensive sentiment analysis for employee"""
        try:
            # Get AI orchestrator service
            ai_orchestrator = self.env['hr.ai.orchestrator']
            
            # Gather sentiment data
            sentiment_data = self._gather_sentiment_data()
            
            # Run AI sentiment analysis
            analysis_result = ai_orchestrator.analyze_employee_sentiment(sentiment_data)
            
            # Update sentiment scores
            self.overall_sentiment_score = analysis_result.get('overall_score', 0)
            self.job_satisfaction_score = analysis_result.get('job_satisfaction', 0)
            self.work_life_balance_score = analysis_result.get('work_life_balance', 0)
            self.team_relationship_score = analysis_result.get('team_relationships', 0)
            self.management_satisfaction_score = analysis_result.get('management_satisfaction', 0)
            self.career_growth_score = analysis_result.get('career_growth', 0)
            self.compensation_satisfaction_score = analysis_result.get('compensation_satisfaction', 0)
            
            # Update detailed analysis
            self.communication_sentiment = analysis_result.get('communication_sentiment', 0)
            self.feedback_sentiment = analysis_result.get('feedback_sentiment', 0)
            self.social_interaction_sentiment = analysis_result.get('social_sentiment', 0)
            self.engagement_level = analysis_result.get('engagement_level', 0)
            
            # Risk assessment
            risk_analysis = analysis_result.get('risk_analysis', {})
            self.burnout_risk_level = risk_analysis.get('burnout_risk', 'low')
            self.stress_indicators = risk_analysis.get('stress_indicators', '')
            
            # Trend analysis
            self._analyze_sentiment_trends()
            
            # Generate recommendations
            self._generate_recommendations()
            
            # Set alert level
            self._determine_alert_level()
            
            # Update metadata
            self.confidence_level = analysis_result.get('confidence', 0)
            self.data_sources_used = json.dumps(sentiment_data.get('sources', []))
            self.analysis_status = 'completed'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Sentiment analysis completed for %s') % self.employee_id.name,
                    'type': 'success'
                }
            }
            
        except Exception as e:
            self.analysis_status = 'error'
            _logger.error(f"Sentiment analysis failed: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Sentiment analysis failed: %s') % str(e),
                    'type': 'danger'
                }
            }
    
    def _gather_sentiment_data(self):
        """Gather data for sentiment analysis"""
        employee = self.employee_id
        
        # Get recent communication data
        communication_data = self._get_communication_data(employee)
        
        # Get survey responses
        survey_data = self._get_survey_data(employee)
        
        # Get feedback data
        feedback_data = self._get_feedback_data(employee)
        
        # Get attendance patterns
        attendance_data = self._get_attendance_patterns(employee)
        
        # Get performance indicators
        performance_data = self._get_performance_indicators(employee)
        
        return {
            'employee_id': employee.id,
            'name': employee.name,
            'department': employee.department_id.name if employee.department_id else '',
            'communication': communication_data,
            'surveys': survey_data,
            'feedback': feedback_data,
            'attendance': attendance_data,
            'performance': performance_data,
            'sources': ['communication', 'surveys', 'feedback', 'attendance', 'performance']
        }
    
    def _get_communication_data(self, employee):
        """Get employee communication data for sentiment analysis"""
        if not employee.user_id:
            return {}
        
        # Get recent messages (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        messages = self.env['mail.message'].search([
            ('author_id', '=', employee.user_id.partner_id.id),
            ('date', '>=', thirty_days_ago)
        ], limit=100)
        
        message_texts = []
        for message in messages:
            if message.body:
                # Strip HTML tags for sentiment analysis
                import re
                clean_text = re.sub('<[^<]+?>', '', message.body)
                message_texts.append(clean_text)
        
        return {
            'messages': message_texts,
            'message_count': len(messages),
            'communication_frequency': len(messages) / 30,  # messages per day
        }
    
    def _get_survey_data(self, employee):
        """Get employee survey responses"""
        # This would integrate with survey modules
        return {
            'recent_surveys': [],
            'satisfaction_scores': {},
            'open_responses': [],
        }
    
    def _get_feedback_data(self, employee):
        """Get employee feedback data"""
        # This would integrate with performance review modules
        return {
            'peer_feedback': [],
            'manager_feedback': [],
            'self_assessments': [],
            'customer_feedback': [],
        }
    
    def _get_attendance_patterns(self, employee):
        """Get attendance patterns that might indicate sentiment"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', thirty_days_ago)
        ])
        
        if not attendances:
            return {}
        
        # Calculate patterns
        late_arrivals = sum(1 for att in attendances if att.check_in.hour > 9)
        early_departures = sum(1 for att in attendances if att.check_out and att.check_out.hour < 17)
        overtime_days = sum(1 for att in attendances if att.worked_hours > 8)
        
        return {
            'total_days': len(attendances),
            'late_arrival_rate': late_arrivals / len(attendances) if attendances else 0,
            'early_departure_rate': early_departures / len(attendances) if attendances else 0,
            'overtime_frequency': overtime_days / len(attendances) if attendances else 0,
            'avg_hours_per_day': sum(att.worked_hours for att in attendances) / len(attendances) if attendances else 0,
        }
    
    def _get_performance_indicators(self, employee):
        """Get performance indicators that might affect sentiment"""
        # Get recent performance data
        performance_records = self.env['hr.performance.analytics'].search([
            ('employee_id', '=', employee.id),
            ('analysis_status', '=', 'completed')
        ], limit=1, order='last_updated desc')
        
        if performance_records:
            performance = performance_records[0]
            return {
                'overall_score': performance.overall_performance_score,
                'trend': performance.performance_trend,
                'productivity': performance.productivity_score,
                'collaboration': performance.collaboration_score,
            }
        
        return {}
    
    def _analyze_sentiment_trends(self):
        """Analyze sentiment trends over time"""
        # Get previous sentiment analyses
        previous_analyses = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('id', '!=', self.id),
            ('analysis_status', '=', 'completed')
        ], limit=5, order='analysis_date desc')
        
        if len(previous_analyses) >= 2:
            recent_scores = [self.overall_sentiment_score] + [a.overall_sentiment_score for a in previous_analyses[:2]]
            
            # Simple trend calculation
            if recent_scores[0] > recent_scores[1] and recent_scores[1] > recent_scores[2]:
                self.sentiment_trend = 'improving'
                self.trend_analysis = "Sentiment has been consistently improving over recent analyses."
            elif recent_scores[0] < recent_scores[1] and recent_scores[1] < recent_scores[2]:
                self.sentiment_trend = 'declining'
                self.trend_analysis = "Sentiment has been declining over recent analyses. Attention needed."
            else:
                self.sentiment_trend = 'stable'
                self.trend_analysis = "Sentiment has remained relatively stable."
        else:
            self.sentiment_trend = 'stable'
            self.trend_analysis = "Insufficient historical data for trend analysis."
    
    def _generate_recommendations(self):
        """Generate recommendations based on sentiment analysis"""
        recommendations = []
        interventions = []
        
        # Job satisfaction recommendations
        if self.job_satisfaction_score < 0.3:
            recommendations.append("Schedule one-on-one meeting to discuss job satisfaction concerns")
            interventions.append("Consider role adjustment or task variety increase")
        
        # Work-life balance recommendations
        if self.work_life_balance_score < 0.2:
            recommendations.append("Review workload and overtime patterns")
            interventions.append("Implement flexible working arrangements")
        
        # Team relationship recommendations
        if self.team_relationship_score < 0.3:
            recommendations.append("Facilitate team building activities")
            interventions.append("Consider team dynamics assessment")
        
        # Management satisfaction recommendations
        if self.management_satisfaction_score < 0.2:
            recommendations.append("Manager coaching on leadership skills")
            interventions.append("Implement regular feedback sessions")
        
        # Career growth recommendations
        if self.career_growth_score < 0.3:
            recommendations.append("Discuss career development opportunities")
            interventions.append("Create personalized development plan")
        
        # Burnout risk recommendations
        if self.burnout_risk_level in ['high', 'critical']:
            recommendations.append("Immediate intervention required - high burnout risk")
            interventions.append("Consider temporary workload reduction and wellness support")
        
        self.recommended_actions = '\n'.join(recommendations)
        self.intervention_suggestions = '\n'.join(interventions)
    
    def _determine_alert_level(self):
        """Determine alert level based on sentiment analysis"""
        if self.overall_sentiment_score < -0.6 or self.burnout_risk_level == 'critical':
            self.alert_level = 'urgent'
        elif self.overall_sentiment_score < -0.3 or self.burnout_risk_level == 'high':
            self.alert_level = 'high'
        elif self.overall_sentiment_score < 0 or self.sentiment_trend == 'declining':
            self.alert_level = 'medium'
        elif self.overall_sentiment_score < 0.3:
            self.alert_level = 'low'
        else:
            self.alert_level = 'none'
    
    @api.model
    def schedule_batch_sentiment_analysis(self):
        """Schedule sentiment analysis for all employees"""
        employees = self.env['hr.employee'].search([('active', '=', True)])
        
        for employee in employees:
            # Check if recent analysis exists (within last 7 days)
            recent_analysis = self.search([
                ('employee_id', '=', employee.id),
                ('analysis_date', '>=', datetime.now() - timedelta(days=7))
            ], limit=1)
            
            if not recent_analysis:
                # Create new sentiment analysis
                sentiment_analysis = self.create({
                    'employee_id': employee.id,
                })
                try:
                    sentiment_analysis.run_sentiment_analysis()
                except Exception as e:
                    _logger.error(f"Batch sentiment analysis failed for {employee.name}: {str(e)}")
                    continue
    
    def generate_sentiment_report(self):
        """Generate comprehensive sentiment report"""
        return {
            'employee_name': self.employee_id.name,
            'department': self.department_id.name if self.department_id else '',
            'analysis_date': self.analysis_date.strftime('%Y-%m-%d %H:%M'),
            'overall_sentiment': self.overall_sentiment_score,
            'emotional_state': self.emotional_state,
            'sentiment_breakdown': {
                'job_satisfaction': self.job_satisfaction_score,
                'work_life_balance': self.work_life_balance_score,
                'team_relationships': self.team_relationship_score,
                'management_satisfaction': self.management_satisfaction_score,
                'career_growth': self.career_growth_score,
                'compensation_satisfaction': self.compensation_satisfaction_score,
            },
            'risk_assessment': {
                'burnout_risk': self.burnout_risk_level,
                'engagement_level': self.engagement_level,
                'alert_level': self.alert_level,
            },
            'trend': self.sentiment_trend,
            'recommendations': self.recommended_actions,
            'interventions': self.intervention_suggestions,
        } 