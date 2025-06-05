from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class HRRecruitmentAI(models.Model):
    _name = 'hr.recruitment.ai'
    _description = 'AI-Powered Recruitment Intelligence'
    _rec_name = 'applicant_id'
    
    applicant_id = fields.Many2one('hr.applicant', 'Applicant', required=True, ondelete='cascade')
    job_id = fields.Many2one('hr.job', 'Job Position', related='applicant_id.job_id', store=True)
    company_id = fields.Many2one('res.company', 'Company', related='applicant_id.company_id', store=True)
    
    # AI Assessment Results
    overall_score = fields.Float('Overall AI Score', help='Composite score from 0-100')
    recommendation = fields.Selection([
        ('strong_hire', 'Strong Hire'),
        ('hire', 'Hire'),
        ('maybe', 'Maybe'),
        ('no_hire', 'No Hire'),
        ('strong_no_hire', 'Strong No Hire'),
    ], 'AI Recommendation')
    
    # Detailed Assessments
    resume_analysis = fields.Text('Resume Analysis')
    skills_match_score = fields.Float('Skills Match Score')
    experience_relevance = fields.Float('Experience Relevance Score')
    education_fit = fields.Float('Education Fit Score')
    
    # Personality & Cultural Fit
    personality_assessment = fields.Text('Personality Assessment')
    cultural_fit_score = fields.Float('Cultural Fit Score')
    team_compatibility = fields.Text('Team Compatibility Analysis')
    
    # Interview Analysis
    interview_transcript = fields.Text('Interview Transcript')
    interview_analysis = fields.Text('Interview Analysis')
    communication_score = fields.Float('Communication Score')
    technical_competency = fields.Float('Technical Competency Score')
    
    # Predictive Analytics
    success_probability = fields.Float('Success Probability', help='Predicted success in role (0-1)')
    retention_prediction = fields.Float('Retention Prediction', help='Predicted tenure in years')
    performance_forecast = fields.Text('Performance Forecast')
    
    # Risk Assessment
    red_flags = fields.Text('Identified Red Flags')
    risk_factors = fields.Text('Risk Factors')
    background_check_recommendations = fields.Text('Background Check Recommendations')
    
    # Bias Detection
    bias_analysis = fields.Text('Bias Analysis')
    fairness_score = fields.Float('Fairness Score')
    diversity_impact = fields.Text('Diversity Impact Assessment')
    
    # Analysis Metadata
    analysis_date = fields.Datetime('Analysis Date', readonly=True)
    ai_confidence = fields.Float('AI Confidence Level', readonly=True)
    data_sources = fields.Text('Data Sources Used', readonly=True)
    
    # Status
    analysis_status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], 'Analysis Status', default='pending')
    
    def run_comprehensive_assessment(self):
        """Run comprehensive AI assessment for candidate"""
        self.analysis_status = 'in_progress'
        
        try:
            # Get AI orchestrator service
            ai_orchestrator = self.env['hr.ai.orchestrator']
            
            # Gather candidate data
            candidate_data = self._gather_candidate_data()
            job_requirements = self._gather_job_requirements()
            
            # Run resume analysis
            resume_result = ai_orchestrator.analyze_resume(candidate_data, job_requirements)
            self.resume_analysis = resume_result.get('analysis', '')
            self.skills_match_score = resume_result.get('skills_match', 0)
            self.experience_relevance = resume_result.get('experience_relevance', 0)
            self.education_fit = resume_result.get('education_fit', 0)
            
            # Run personality assessment
            personality_result = ai_orchestrator.assess_candidate_personality(candidate_data)
            self.personality_assessment = personality_result.get('assessment', '')
            self.cultural_fit_score = personality_result.get('cultural_fit', 0)
            
            # Analyze interview if available
            if candidate_data.get('interview_transcript'):
                interview_result = ai_orchestrator.analyze_interview(
                    candidate_data['interview_transcript'], 
                    job_requirements
                )
                self.interview_analysis = interview_result.get('analysis', '')
                self.communication_score = interview_result.get('communication_score', 0)
                self.technical_competency = interview_result.get('technical_score', 0)
            
            # Run predictive analytics
            prediction_result = ai_orchestrator.predict_candidate_success(candidate_data, job_requirements)
            self.success_probability = prediction_result.get('success_probability', 0)
            self.retention_prediction = prediction_result.get('retention_years', 0)
            self.performance_forecast = prediction_result.get('performance_forecast', '')
            
            # Bias detection and fairness analysis
            bias_result = ai_orchestrator.detect_hiring_bias(candidate_data, job_requirements)
            self.bias_analysis = bias_result.get('analysis', '')
            self.fairness_score = bias_result.get('fairness_score', 0)
            self.diversity_impact = bias_result.get('diversity_impact', '')
            
            # Risk assessment
            risk_result = ai_orchestrator.assess_candidate_risks(candidate_data)
            self.red_flags = risk_result.get('red_flags', '')
            self.risk_factors = risk_result.get('risk_factors', '')
            self.background_check_recommendations = risk_result.get('background_recommendations', '')
            
            # Calculate overall score and recommendation
            self._calculate_overall_assessment()
            
            # Update metadata
            self.analysis_date = fields.Datetime.now()
            self.ai_confidence = min([
                resume_result.get('confidence', 0),
                personality_result.get('confidence', 0),
                prediction_result.get('confidence', 0),
                bias_result.get('confidence', 0),
            ])
            self.analysis_status = 'completed'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('AI assessment completed for %s') % self.applicant_id.partner_name,
                    'type': 'success'
                }
            }
            
        except Exception as e:
            self.analysis_status = 'error'
            _logger.error(f"Recruitment AI assessment failed: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Assessment failed: %s') % str(e),
                    'type': 'danger'
                }
            }
    
    def _gather_candidate_data(self):
        """Gather comprehensive candidate data"""
        applicant = self.applicant_id
        
        data = {
            'applicant_id': applicant.id,
            'name': applicant.partner_name,
            'email': applicant.email_from,
            'phone': applicant.partner_phone,
            'resume_text': self._extract_resume_text(),
            'cover_letter': applicant.description or '',
            'linkedin_profile': self._get_linkedin_data(),
            'application_date': applicant.create_date.strftime('%Y-%m-%d'),
            'source': applicant.source_id.name if applicant.source_id else '',
            'stage': applicant.stage_id.name if applicant.stage_id else '',
        }
        
        # Add interview data if available
        interview_data = self._get_interview_data()
        data.update(interview_data)
        
        return data
    
    def _gather_job_requirements(self):
        """Gather job requirements and company culture data"""
        job = self.job_id
        
        requirements = {
            'job_title': job.name,
            'department': job.department_id.name if job.department_id else '',
            'description': job.description or '',
            'requirements': job.requirements or '',
            'expected_employees': job.expected_employees,
            'company_culture': self._get_company_culture_data(),
            'team_composition': self._get_team_composition(),
            'success_criteria': self._get_success_criteria(),
        }
        
        return requirements
    
    def _extract_resume_text(self):
        """Extract text from resume attachments"""
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'hr.applicant'),
            ('res_id', '=', self.applicant_id.id),
        ])
        
        resume_text = ""
        for attachment in attachments:
            if attachment.mimetype in ['application/pdf', 'text/plain', 'application/msword']:
                # In a real implementation, you would use libraries like PyPDF2, python-docx
                # For now, we'll use a placeholder
                resume_text += f"[Resume content from {attachment.name}]\n"
        
        return resume_text
    
    def _get_interview_data(self):
        """Get interview transcripts and notes"""
        # This would integrate with interview scheduling and recording systems
        return {
            'interview_transcript': '',
            'interview_notes': '',
            'interviewer_feedback': '',
        }
    
    def _get_linkedin_data(self):
        """Get LinkedIn profile data if available"""
        # This would integrate with LinkedIn API
        return {
            'profile_url': '',
            'connections': 0,
            'endorsements': [],
            'recommendations': [],
        }
    
    def _get_company_culture_data(self):
        """Get company culture information"""
        return {
            'values': ['Innovation', 'Collaboration', 'Excellence'],
            'work_style': 'Hybrid',
            'team_dynamics': 'Collaborative',
        }
    
    def _get_team_composition(self):
        """Get information about the team the candidate would join"""
        if self.job_id.department_id:
            team_members = self.env['hr.employee'].search([
                ('department_id', '=', self.job_id.department_id.id)
            ])
            
            return {
                'team_size': len(team_members),
                'avg_experience': 5,  # Placeholder
                'skill_distribution': {},
            }
        return {}
    
    def _get_success_criteria(self):
        """Get success criteria for the role"""
        return {
            'key_metrics': ['Performance', 'Collaboration', 'Innovation'],
            'growth_expectations': 'High',
            'learning_curve': '3-6 months',
        }
    
    def _calculate_overall_assessment(self):
        """Calculate overall score and recommendation"""
        # Weighted scoring algorithm
        weights = {
            'skills_match': 0.25,
            'experience_relevance': 0.20,
            'cultural_fit': 0.15,
            'communication': 0.15,
            'technical_competency': 0.15,
            'success_probability': 0.10,
        }
        
        scores = {
            'skills_match': self.skills_match_score,
            'experience_relevance': self.experience_relevance,
            'cultural_fit': self.cultural_fit_score,
            'communication': self.communication_score,
            'technical_competency': self.technical_competency,
            'success_probability': self.success_probability * 100,
        }
        
        # Calculate weighted average
        overall_score = sum(weights[key] * scores[key] for key in weights.keys())
        self.overall_score = overall_score
        
        # Determine recommendation based on score
        if overall_score >= 85:
            self.recommendation = 'strong_hire'
        elif overall_score >= 70:
            self.recommendation = 'hire'
        elif overall_score >= 55:
            self.recommendation = 'maybe'
        elif overall_score >= 40:
            self.recommendation = 'no_hire'
        else:
            self.recommendation = 'strong_no_hire'
    
    def generate_assessment_report(self):
        """Generate comprehensive assessment report"""
        report_data = {
            'candidate_name': self.applicant_id.partner_name,
            'position': self.job_id.name,
            'overall_score': self.overall_score,
            'recommendation': self.recommendation,
            'key_strengths': self._extract_strengths(),
            'areas_of_concern': self._extract_concerns(),
            'interview_highlights': self._extract_interview_highlights(),
            'next_steps': self._generate_next_steps(),
        }
        
        return report_data
    
    def _extract_strengths(self):
        """Extract key strengths from analysis"""
        strengths = []
        if self.skills_match_score > 80:
            strengths.append("Excellent skills match for the role")
        if self.cultural_fit_score > 75:
            strengths.append("Strong cultural fit")
        if self.communication_score > 80:
            strengths.append("Excellent communication skills")
        return strengths
    
    def _extract_concerns(self):
        """Extract areas of concern from analysis"""
        concerns = []
        if self.experience_relevance < 60:
            concerns.append("Limited relevant experience")
        if self.red_flags:
            concerns.append("Background verification recommended")
        return concerns
    
    def _extract_interview_highlights(self):
        """Extract interview highlights"""
        if self.interview_analysis:
            return ["Strong technical responses", "Good cultural alignment"]
        return []
    
    def _generate_next_steps(self):
        """Generate recommended next steps"""
        if self.recommendation in ['strong_hire', 'hire']:
            return ["Proceed with reference checks", "Prepare offer"]
        elif self.recommendation == 'maybe':
            return ["Conduct additional interview", "Skills assessment"]
        else:
            return ["Thank candidate for their time", "Keep in talent pool"] 