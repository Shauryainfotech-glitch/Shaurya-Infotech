from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class HREmployeeIntelligence(models.Model):
    _name = 'hr.employee.intelligence'
    _description = 'AI-Powered Employee Intelligence'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', 'Company', related='employee_id.company_id', store=True)
    
    # AI Analysis Results
    personality_analysis = fields.Text('Personality Analysis')
    skills_assessment = fields.Text('Skills Assessment')
    performance_prediction = fields.Text('Performance Prediction')
    career_recommendations = fields.Text('Career Development Recommendations')
    
    # Sentiment Analysis
    current_sentiment_score = fields.Float('Current Sentiment Score', help='Range: -1 (negative) to 1 (positive)')
    sentiment_trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ], 'Sentiment Trend')
    
    # Risk Assessment
    flight_risk_score = fields.Float('Flight Risk Score', help='Probability of employee leaving (0-1)')
    risk_factors = fields.Text('Risk Factors')
    retention_recommendations = fields.Text('Retention Recommendations')
    
    # Performance Metrics
    productivity_score = fields.Float('AI Productivity Score')
    collaboration_score = fields.Float('Collaboration Score')
    innovation_score = fields.Float('Innovation Score')
    leadership_potential = fields.Float('Leadership Potential Score')
    
    # Learning & Development
    skill_gaps = fields.Text('Identified Skill Gaps')
    learning_recommendations = fields.Text('Learning Recommendations')
    training_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], 'Training Priority')
    
    # Analysis Metadata
    last_analysis_date = fields.Datetime('Last Analysis Date', readonly=True)
    analysis_confidence = fields.Float('Analysis Confidence', readonly=True)
    data_sources = fields.Text('Data Sources Used')
    
    # Status
    analysis_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], 'Analysis Status', default='pending')
    
    def run_comprehensive_analysis(self):
        """Run comprehensive AI analysis for employee"""
        self.analysis_status = 'in_progress'
        
        try:
            # Get AI orchestrator service
            ai_orchestrator = self.env['hr.ai.orchestrator']
            
            # Gather employee data
            employee_data = self._gather_employee_data()
            
            # Run personality analysis
            personality_result = ai_orchestrator.analyze_personality(employee_data)
            self.personality_analysis = personality_result.get('analysis', '')
            
            # Run skills assessment
            skills_result = ai_orchestrator.assess_skills(employee_data)
            self.skills_assessment = skills_result.get('assessment', '')
            self.skill_gaps = skills_result.get('gaps', '')
            
            # Run performance prediction
            performance_result = ai_orchestrator.predict_performance(employee_data)
            self.performance_prediction = performance_result.get('prediction', '')
            self.productivity_score = performance_result.get('productivity_score', 0)
            
            # Run sentiment analysis
            sentiment_result = ai_orchestrator.analyze_sentiment(employee_data)
            self.current_sentiment_score = sentiment_result.get('score', 0)
            self.sentiment_trend = sentiment_result.get('trend', 'stable')
            
            # Run flight risk assessment
            risk_result = ai_orchestrator.assess_flight_risk(employee_data)
            self.flight_risk_score = risk_result.get('risk_score', 0)
            self.risk_factors = risk_result.get('factors', '')
            self.retention_recommendations = risk_result.get('recommendations', '')
            
            # Generate career recommendations
            career_result = ai_orchestrator.generate_career_recommendations(employee_data)
            self.career_recommendations = career_result.get('recommendations', '')
            self.learning_recommendations = career_result.get('learning_plan', '')
            
            # Update metadata
            self.last_analysis_date = fields.Datetime.now()
            self.analysis_confidence = min([
                personality_result.get('confidence', 0),
                skills_result.get('confidence', 0),
                performance_result.get('confidence', 0),
                sentiment_result.get('confidence', 0),
                risk_result.get('confidence', 0),
            ])
            self.analysis_status = 'completed'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('AI analysis completed successfully for %s') % self.employee_id.name,
                    'type': 'success'
                }
            }
            
        except Exception as e:
            self.analysis_status = 'error'
            _logger.error(f"Employee intelligence analysis failed: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Analysis failed: %s') % str(e),
                    'type': 'danger'
                }
            }
    
    def _gather_employee_data(self):
        """Gather comprehensive employee data for AI analysis"""
        employee = self.employee_id
        
        # Basic employee information
        data = {
            'employee_id': employee.id,
            'name': employee.name,
            'job_title': employee.job_title or '',
            'department': employee.department_id.name if employee.department_id else '',
            'manager': employee.parent_id.name if employee.parent_id else '',
            'work_email': employee.work_email or '',
            'work_phone': employee.work_phone or '',
            'hire_date': employee.create_date.strftime('%Y-%m-%d') if employee.create_date else '',
        }
        
        # Performance data
        performance_data = self._get_performance_data(employee)
        data.update(performance_data)
        
        # Attendance data
        attendance_data = self._get_attendance_data(employee)
        data.update(attendance_data)
        
        # Communication data
        communication_data = self._get_communication_data(employee)
        data.update(communication_data)
        
        # Training data
        training_data = self._get_training_data(employee)
        data.update(training_data)
        
        return data
    
    def _get_performance_data(self, employee):
        """Get employee performance data"""
        # This would integrate with performance management modules
        return {
            'performance_reviews': [],
            'goals_achieved': 0,
            'kpi_scores': {},
        }
    
    def _get_attendance_data(self, employee):
        """Get employee attendance data"""
        # Get attendance records for last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', six_months_ago)
        ])
        
        return {
            'attendance_records': len(attendances),
            'avg_work_hours': sum(att.worked_hours for att in attendances) / len(attendances) if attendances else 0,
            'punctuality_score': self._calculate_punctuality_score(attendances),
        }
    
    def _get_communication_data(self, employee):
        """Get employee communication data"""
        # Get mail messages and activities
        messages = self.env['mail.message'].search([
            ('author_id', '=', employee.user_id.partner_id.id)
        ], limit=100)
        
        return {
            'communication_frequency': len(messages),
            'collaboration_indicators': self._analyze_collaboration(messages),
        }
    
    def _get_training_data(self, employee):
        """Get employee training and development data"""
        return {
            'completed_trainings': [],
            'certifications': [],
            'skill_assessments': [],
        }
    
    def _calculate_punctuality_score(self, attendances):
        """Calculate punctuality score based on attendance data"""
        if not attendances:
            return 0
        
        # Simple punctuality calculation
        on_time_count = 0
        for attendance in attendances:
            # Assuming work starts at 9 AM
            if attendance.check_in.hour <= 9:
                on_time_count += 1
        
        return on_time_count / len(attendances) if attendances else 0
    
    def _analyze_collaboration(self, messages):
        """Analyze collaboration patterns from messages"""
        # Simple collaboration analysis
        return {
            'team_interactions': len(messages),
            'response_rate': 0.8,  # Placeholder
            'initiative_score': 0.7,  # Placeholder
        }
    
    @api.model
    def schedule_batch_analysis(self):
        """Schedule batch analysis for all employees"""
        employees_to_analyze = self.search([
            ('analysis_status', 'in', ['pending', 'error']),
        ])
        
        for employee_intel in employees_to_analyze:
            try:
                employee_intel.run_comprehensive_analysis()
            except Exception as e:
                _logger.error(f"Batch analysis failed for employee {employee_intel.employee_id.name}: {str(e)}")
                continue 