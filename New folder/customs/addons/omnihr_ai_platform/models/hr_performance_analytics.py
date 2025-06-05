from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class HRPerformanceAnalytics(models.Model):
    _name = 'hr.performance.analytics'
    _description = 'AI-Powered Performance Analytics'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', 'Department', related='employee_id.department_id', store=True)
    company_id = fields.Many2one('res.company', 'Company', related='employee_id.company_id', store=True)
    
    # Performance Scores
    overall_performance_score = fields.Float('Overall Performance Score', help='AI-calculated performance score (0-100)')
    productivity_score = fields.Float('Productivity Score')
    quality_score = fields.Float('Quality Score')
    collaboration_score = fields.Float('Collaboration Score')
    innovation_score = fields.Float('Innovation Score')
    leadership_score = fields.Float('Leadership Score')
    
    # Trend Analysis
    performance_trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ], 'Performance Trend')
    trend_analysis = fields.Text('Trend Analysis')
    
    # Predictive Analytics
    future_performance_prediction = fields.Float('Predicted Future Performance')
    promotion_readiness = fields.Float('Promotion Readiness Score')
    skill_development_needs = fields.Text('Skill Development Needs')
    
    # Goal Achievement
    goals_completion_rate = fields.Float('Goals Completion Rate (%)')
    kpi_achievement = fields.Text('KPI Achievement Analysis')
    milestone_tracking = fields.Text('Milestone Tracking')
    
    # Comparative Analysis
    peer_comparison = fields.Text('Peer Comparison Analysis')
    department_ranking = fields.Integer('Department Ranking')
    company_percentile = fields.Float('Company Percentile')
    
    # Behavioral Insights
    work_patterns = fields.Text('Work Pattern Analysis')
    communication_effectiveness = fields.Float('Communication Effectiveness')
    time_management_score = fields.Float('Time Management Score')
    stress_indicators = fields.Text('Stress Level Indicators')
    
    # Development Recommendations
    training_recommendations = fields.Text('Training Recommendations')
    mentoring_suggestions = fields.Text('Mentoring Suggestions')
    career_path_guidance = fields.Text('Career Path Guidance')
    
    # Risk Assessment
    performance_risk_factors = fields.Text('Performance Risk Factors')
    burnout_risk_score = fields.Float('Burnout Risk Score')
    retention_risk = fields.Float('Retention Risk Score')
    
    # Analysis Metadata
    analysis_period_start = fields.Date('Analysis Period Start')
    analysis_period_end = fields.Date('Analysis Period End')
    last_updated = fields.Datetime('Last Updated', readonly=True)
    data_quality_score = fields.Float('Data Quality Score', readonly=True)
    
    # Status
    analysis_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], 'Analysis Status', default='pending')
    
    def run_performance_analysis(self):
        """Run comprehensive performance analysis"""
        self.analysis_status = 'in_progress'
        
        try:
            # Set analysis period (last 6 months by default)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=180)
            self.analysis_period_start = start_date
            self.analysis_period_end = end_date
            
            # Get AI orchestrator service
            ai_orchestrator = self.env['hr.ai.orchestrator']
            
            # Gather performance data
            performance_data = self._gather_performance_data(start_date, end_date)
            
            # Run core performance analysis
            core_analysis = ai_orchestrator.analyze_performance(performance_data)
            self.overall_performance_score = core_analysis.get('overall_score', 0)
            self.productivity_score = core_analysis.get('productivity', 0)
            self.quality_score = core_analysis.get('quality', 0)
            self.collaboration_score = core_analysis.get('collaboration', 0)
            self.innovation_score = core_analysis.get('innovation', 0)
            self.leadership_score = core_analysis.get('leadership', 0)
            
            # Trend analysis
            trend_analysis = ai_orchestrator.analyze_performance_trends(performance_data)
            self.performance_trend = trend_analysis.get('trend', 'stable')
            self.trend_analysis = trend_analysis.get('analysis', '')
            
            # Predictive analytics
            prediction_analysis = ai_orchestrator.predict_future_performance(performance_data)
            self.future_performance_prediction = prediction_analysis.get('future_score', 0)
            self.promotion_readiness = prediction_analysis.get('promotion_readiness', 0)
            
            # Goal and KPI analysis
            goal_analysis = ai_orchestrator.analyze_goal_achievement(performance_data)
            self.goals_completion_rate = goal_analysis.get('completion_rate', 0)
            self.kpi_achievement = goal_analysis.get('kpi_analysis', '')
            
            # Behavioral insights
            behavioral_analysis = ai_orchestrator.analyze_work_behavior(performance_data)
            self.work_patterns = behavioral_analysis.get('patterns', '')
            self.communication_effectiveness = behavioral_analysis.get('communication', 0)
            self.time_management_score = behavioral_analysis.get('time_management', 0)
            self.stress_indicators = behavioral_analysis.get('stress_indicators', '')
            
            # Risk assessment
            risk_analysis = ai_orchestrator.assess_performance_risks(performance_data)
            self.performance_risk_factors = risk_analysis.get('risk_factors', '')
            self.burnout_risk_score = risk_analysis.get('burnout_risk', 0)
            self.retention_risk = risk_analysis.get('retention_risk', 0)
            
            # Development recommendations
            development_analysis = ai_orchestrator.generate_development_plan(performance_data)
            self.training_recommendations = development_analysis.get('training', '')
            self.mentoring_suggestions = development_analysis.get('mentoring', '')
            self.career_path_guidance = development_analysis.get('career_guidance', '')
            self.skill_development_needs = development_analysis.get('skill_needs', '')
            
            # Comparative analysis
            self._run_comparative_analysis()
            
            # Update metadata
            self.last_updated = fields.Datetime.now()
            self.data_quality_score = self._calculate_data_quality_score(performance_data)
            self.analysis_status = 'completed'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Performance analysis completed for %s') % self.employee_id.name,
                    'type': 'success'
                }
            }
            
        except Exception as e:
            self.analysis_status = 'error'
            _logger.error(f"Performance analysis failed: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Analysis failed: %s') % str(e),
                    'type': 'danger'
                }
            }
    
    def _gather_performance_data(self, start_date, end_date):
        """Gather comprehensive performance data"""
        employee = self.employee_id
        
        data = {
            'employee_id': employee.id,
            'name': employee.name,
            'department': employee.department_id.name if employee.department_id else '',
            'job_title': employee.job_title or '',
            'manager': employee.parent_id.name if employee.parent_id else '',
            'analysis_period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
            },
        }
        
        # Attendance and time tracking data
        attendance_data = self._get_attendance_metrics(employee, start_date, end_date)
        data.update(attendance_data)
        
        # Task and project completion data
        task_data = self._get_task_completion_data(employee, start_date, end_date)
        data.update(task_data)
        
        # Communication and collaboration data
        communication_data = self._get_communication_metrics(employee, start_date, end_date)
        data.update(communication_data)
        
        # Goal and objective data
        goal_data = self._get_goal_achievement_data(employee, start_date, end_date)
        data.update(goal_data)
        
        # Training and development data
        training_data = self._get_training_participation_data(employee, start_date, end_date)
        data.update(training_data)
        
        # Feedback and review data
        feedback_data = self._get_feedback_data(employee, start_date, end_date)
        data.update(feedback_data)
        
        return data
    
    def _get_attendance_metrics(self, employee, start_date, end_date):
        """Get attendance and punctuality metrics"""
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', start_date),
            ('check_in', '<=', end_date)
        ])
        
        if not attendances:
            return {'attendance_metrics': {}}
        
        total_hours = sum(att.worked_hours for att in attendances)
        avg_daily_hours = total_hours / len(attendances) if attendances else 0
        
        # Calculate punctuality
        on_time_count = sum(1 for att in attendances if att.check_in.hour <= 9)
        punctuality_rate = on_time_count / len(attendances) if attendances else 0
        
        return {
            'attendance_metrics': {
                'total_days': len(attendances),
                'total_hours': total_hours,
                'avg_daily_hours': avg_daily_hours,
                'punctuality_rate': punctuality_rate,
                'consistency_score': self._calculate_consistency_score(attendances),
            }
        }
    
    def _get_task_completion_data(self, employee, start_date, end_date):
        """Get task and project completion data"""
        # This would integrate with project management modules
        return {
            'task_metrics': {
                'completed_tasks': 0,
                'overdue_tasks': 0,
                'completion_rate': 0,
                'quality_ratings': [],
            }
        }
    
    def _get_communication_metrics(self, employee, start_date, end_date):
        """Get communication and collaboration metrics"""
        if not employee.user_id:
            return {'communication_metrics': {}}
        
        # Get mail messages
        messages = self.env['mail.message'].search([
            ('author_id', '=', employee.user_id.partner_id.id),
            ('date', '>=', start_date),
            ('date', '<=', end_date)
        ])
        
        return {
            'communication_metrics': {
                'messages_sent': len(messages),
                'avg_response_time': 2.5,  # Placeholder
                'collaboration_score': 0.8,  # Placeholder
            }
        }
    
    def _get_goal_achievement_data(self, employee, start_date, end_date):
        """Get goal achievement data"""
        # This would integrate with goal management modules
        return {
            'goal_metrics': {
                'total_goals': 0,
                'completed_goals': 0,
                'in_progress_goals': 0,
                'overdue_goals': 0,
                'achievement_rate': 0,
            }
        }
    
    def _get_training_participation_data(self, employee, start_date, end_date):
        """Get training and development participation data"""
        return {
            'training_metrics': {
                'courses_completed': 0,
                'hours_trained': 0,
                'certifications_earned': 0,
                'skill_assessments': [],
            }
        }
    
    def _get_feedback_data(self, employee, start_date, end_date):
        """Get feedback and review data"""
        return {
            'feedback_metrics': {
                'peer_reviews': [],
                'manager_feedback': [],
                'customer_feedback': [],
                'self_assessments': [],
            }
        }
    
    def _calculate_consistency_score(self, attendances):
        """Calculate work pattern consistency score"""
        if len(attendances) < 5:
            return 0
        
        # Simple consistency calculation based on check-in times
        check_in_hours = [att.check_in.hour for att in attendances]
        avg_hour = sum(check_in_hours) / len(check_in_hours)
        variance = sum((hour - avg_hour) ** 2 for hour in check_in_hours) / len(check_in_hours)
        
        # Convert variance to consistency score (0-1)
        consistency_score = max(0, 1 - (variance / 4))  # Normalize by 4 hours variance
        return consistency_score
    
    def _run_comparative_analysis(self):
        """Run comparative analysis against peers"""
        # Get department peers
        department_peers = self.search([
            ('department_id', '=', self.department_id.id),
            ('employee_id', '!=', self.employee_id.id),
            ('analysis_status', '=', 'completed')
        ])
        
        if department_peers:
            peer_scores = [peer.overall_performance_score for peer in department_peers]
            peer_scores.append(self.overall_performance_score)
            peer_scores.sort(reverse=True)
            
            self.department_ranking = peer_scores.index(self.overall_performance_score) + 1
            self.company_percentile = (len(peer_scores) - self.department_ranking + 1) / len(peer_scores) * 100
            
            # Generate peer comparison text
            avg_peer_score = sum(peer_scores[:-1]) / len(peer_scores[:-1]) if peer_scores[:-1] else 0
            if self.overall_performance_score > avg_peer_score:
                comparison = "Above average"
            elif self.overall_performance_score < avg_peer_score:
                comparison = "Below average"
            else:
                comparison = "Average"
            
            self.peer_comparison = f"{comparison} performance compared to department peers. " \
                                 f"Ranking: {self.department_ranking} out of {len(peer_scores)}"
    
    def _calculate_data_quality_score(self, performance_data):
        """Calculate data quality score based on available data"""
        quality_factors = []
        
        # Check attendance data availability
        if performance_data.get('attendance_metrics', {}).get('total_days', 0) > 30:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.5)
        
        # Check communication data
        if performance_data.get('communication_metrics', {}).get('messages_sent', 0) > 10:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.3)
        
        # Add more quality checks as needed
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        return {
            'employee_name': self.employee_id.name,
            'department': self.department_id.name if self.department_id else '',
            'analysis_period': f"{self.analysis_period_start} to {self.analysis_period_end}",
            'overall_score': self.overall_performance_score,
            'trend': self.performance_trend,
            'key_strengths': self._identify_strengths(),
            'improvement_areas': self._identify_improvement_areas(),
            'recommendations': self._generate_recommendations(),
            'next_review_date': self._calculate_next_review_date(),
        }
    
    def _identify_strengths(self):
        """Identify key performance strengths"""
        strengths = []
        if self.productivity_score > 80:
            strengths.append("High productivity")
        if self.collaboration_score > 80:
            strengths.append("Excellent collaboration")
        if self.innovation_score > 75:
            strengths.append("Strong innovation")
        return strengths
    
    def _identify_improvement_areas(self):
        """Identify areas for improvement"""
        areas = []
        if self.time_management_score < 60:
            areas.append("Time management")
        if self.communication_effectiveness < 70:
            areas.append("Communication effectiveness")
        if self.quality_score < 70:
            areas.append("Work quality")
        return areas
    
    def _generate_recommendations(self):
        """Generate actionable recommendations"""
        recommendations = []
        if self.training_recommendations:
            recommendations.append(f"Training: {self.training_recommendations}")
        if self.mentoring_suggestions:
            recommendations.append(f"Mentoring: {self.mentoring_suggestions}")
        if self.career_path_guidance:
            recommendations.append(f"Career: {self.career_path_guidance}")
        return recommendations
    
    def _calculate_next_review_date(self):
        """Calculate next review date based on performance"""
        if self.overall_performance_score < 60:
            # Monthly reviews for underperformers
            return (datetime.now() + timedelta(days=30)).date()
        elif self.overall_performance_score > 85:
            # Quarterly reviews for high performers
            return (datetime.now() + timedelta(days=90)).date()
        else:
            # Bi-monthly reviews for average performers
            return (datetime.now() + timedelta(days=60)).date() 