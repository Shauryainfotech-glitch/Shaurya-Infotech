from odoo import models, api, _
from odoo.exceptions import UserError
import json
import logging
import asyncio
from datetime import datetime

_logger = logging.getLogger(__name__)

class HRAIOrchestrator(models.TransientModel):
    _name = 'hr.ai.orchestrator'
    _description = 'HR AI Orchestrator Service'
    
    @api.model
    def analyze_personality(self, employee_data):
        """Analyze employee personality using AI consensus"""
        try:
            # Get AI configuration
            ai_config = self._get_ai_config()
            
            # Prepare prompt for personality analysis
            prompt = self._build_personality_analysis_prompt(employee_data)
            system_prompt = "You are an expert HR psychologist analyzing employee personality traits based on workplace data."
            
            # Get consensus from multiple AI providers
            if ai_config.enable_consensus_mode:
                result = self._get_ai_consensus('personality_analysis', prompt, system_prompt)
            else:
                result = self._get_single_ai_response('personality_analysis', prompt, system_prompt)
            
            return {
                'analysis': result.get('analysis', ''),
                'confidence': result.get('confidence', 0),
                'traits': result.get('traits', []),
                'strengths': result.get('strengths', []),
                'development_areas': result.get('development_areas', []),
            }
            
        except Exception as e:
            _logger.error(f"Personality analysis failed: {str(e)}")
            return {'analysis': 'Analysis failed', 'confidence': 0}
    
    @api.model
    def assess_skills(self, employee_data):
        """Assess employee skills using AI"""
        try:
            prompt = self._build_skills_assessment_prompt(employee_data)
            system_prompt = "You are an expert skills assessor analyzing employee capabilities and identifying skill gaps."
            
            ai_config = self._get_ai_config()
            if ai_config.enable_consensus_mode:
                result = self._get_ai_consensus('skills_assessment', prompt, system_prompt)
            else:
                result = self._get_single_ai_response('skills_assessment', prompt, system_prompt)
            
            return {
                'assessment': result.get('assessment', ''),
                'confidence': result.get('confidence', 0),
                'current_skills': result.get('current_skills', []),
                'gaps': result.get('skill_gaps', ''),
                'recommendations': result.get('recommendations', []),
            }
            
        except Exception as e:
            _logger.error(f"Skills assessment failed: {str(e)}")
            return {'assessment': 'Assessment failed', 'confidence': 0}
    
    @api.model
    def predict_performance(self, employee_data):
        """Predict employee performance using AI"""
        try:
            prompt = self._build_performance_prediction_prompt(employee_data)
            system_prompt = "You are an expert performance analyst predicting future employee performance based on historical data."
            
            ai_config = self._get_ai_config()
            if ai_config.enable_consensus_mode:
                result = self._get_ai_consensus('performance_prediction', prompt, system_prompt)
            else:
                result = self._get_single_ai_response('performance_prediction', prompt, system_prompt)
            
            return {
                'prediction': result.get('prediction', ''),
                'confidence': result.get('confidence', 0),
                'productivity_score': result.get('productivity_score', 0),
                'factors': result.get('key_factors', []),
                'timeline': result.get('timeline', ''),
            }
            
        except Exception as e:
            _logger.error(f"Performance prediction failed: {str(e)}")
            return {'prediction': 'Prediction failed', 'confidence': 0}
    
    @api.model
    def analyze_sentiment(self, employee_data):
        """Analyze employee sentiment using AI"""
        try:
            prompt = self._build_sentiment_analysis_prompt(employee_data)
            system_prompt = "You are an expert sentiment analyst evaluating employee emotional state and engagement."
            
            ai_config = self._get_ai_config()
            if ai_config.enable_consensus_mode:
                result = self._get_ai_consensus('sentiment_analysis', prompt, system_prompt)
            else:
                result = self._get_single_ai_response('sentiment_analysis', prompt, system_prompt)
            
            return {
                'score': result.get('sentiment_score', 0),
                'confidence': result.get('confidence', 0),
                'trend': result.get('trend', 'stable'),
                'indicators': result.get('indicators', []),
                'recommendations': result.get('recommendations', []),
            }
            
        except Exception as e:
            _logger.error(f"Sentiment analysis failed: {str(e)}")
            return {'score': 0, 'confidence': 0, 'trend': 'stable'}
    
    @api.model
    def assess_flight_risk(self, employee_data):
        """Assess employee flight risk using AI"""
        try:
            prompt = self._build_flight_risk_prompt(employee_data)
            system_prompt = "You are an expert HR analyst assessing employee turnover risk based on multiple indicators."
            
            ai_config = self._get_ai_config()
            if ai_config.enable_consensus_mode:
                result = self._get_ai_consensus('flight_risk_assessment', prompt, system_prompt)
            else:
                result = self._get_single_ai_response('flight_risk_assessment', prompt, system_prompt)
            
            return {
                'risk_score': result.get('risk_score', 0),
                'confidence': result.get('confidence', 0),
                'factors': result.get('risk_factors', ''),
                'recommendations': result.get('retention_recommendations', ''),
                'timeline': result.get('timeline', ''),
            }
            
        except Exception as e:
            _logger.error(f"Flight risk assessment failed: {str(e)}")
            return {'risk_score': 0, 'confidence': 0}
    
    @api.model
    def generate_career_recommendations(self, employee_data):
        """Generate career development recommendations using AI"""
        try:
            prompt = self._build_career_recommendations_prompt(employee_data)
            system_prompt = "You are an expert career counselor providing personalized development recommendations."
            
            ai_config = self._get_ai_config()
            if ai_config.enable_consensus_mode:
                result = self._get_ai_consensus('career_recommendations', prompt, system_prompt)
            else:
                result = self._get_single_ai_response('career_recommendations', prompt, system_prompt)
            
            return {
                'recommendations': result.get('recommendations', ''),
                'confidence': result.get('confidence', 0),
                'learning_plan': result.get('learning_plan', ''),
                'career_paths': result.get('career_paths', []),
                'timeline': result.get('timeline', ''),
            }
            
        except Exception as e:
            _logger.error(f"Career recommendations failed: {str(e)}")
            return {'recommendations': 'Recommendations failed', 'confidence': 0}
    
    @api.model
    def analyze_resume(self, candidate_data, job_requirements):
        """Analyze candidate resume using AI"""
        try:
            prompt = self._build_resume_analysis_prompt(candidate_data, job_requirements)
            system_prompt = "You are an expert recruiter analyzing candidate resumes for job fit."
            
            ai_config = self._get_ai_config()
            if ai_config.enable_consensus_mode:
                result = self._get_ai_consensus('resume_analysis', prompt, system_prompt)
            else:
                result = self._get_single_ai_response('resume_analysis', prompt, system_prompt)
            
            return {
                'analysis': result.get('analysis', ''),
                'confidence': result.get('confidence', 0),
                'skills_match': result.get('skills_match', 0),
                'experience_relevance': result.get('experience_relevance', 0),
                'education_fit': result.get('education_fit', 0),
                'strengths': result.get('strengths', []),
                'concerns': result.get('concerns', []),
            }
            
        except Exception as e:
            _logger.error(f"Resume analysis failed: {str(e)}")
            return {'analysis': 'Analysis failed', 'confidence': 0}
    
    @api.model
    def generate_chat_response(self, message, context, session_type):
        """Generate AI chat response"""
        try:
            prompt = self._build_chat_prompt(message, context, session_type)
            system_prompt = self._get_chat_system_prompt(session_type)
            
            ai_config = self._get_ai_config()
            providers = ai_config.get_provider_priority('conversation')
            
            # Use first available provider for chat (real-time requirement)
            result = self._get_single_ai_response('chat_response', prompt, system_prompt, providers[0])
            
            return {
                'response': result.get('response', 'I apologize, but I cannot process your request right now.'),
                'confidence': result.get('confidence', 0),
                'requires_escalation': result.get('requires_escalation', False),
                'escalation_reason': result.get('escalation_reason', ''),
                'suggested_actions': result.get('suggested_actions', []),
            }
            
        except Exception as e:
            _logger.error(f"Chat response generation failed: {str(e)}")
            return {
                'response': 'I apologize, but I encountered an error. Please try again.',
                'confidence': 0,
                'requires_escalation': True,
                'escalation_reason': 'Technical error'
            }
    
    def _get_ai_config(self):
        """Get active AI configuration"""
        config = self.env['hr.advanced.ai.config'].search([('active', '=', True)], limit=1)
        if not config:
            raise UserError(_('No active AI configuration found'))
        return config
    
    def _get_ai_consensus(self, task_type, prompt, system_prompt):
        """Get consensus from multiple AI providers"""
        ai_config = self._get_ai_config()
        providers = ai_config.get_provider_priority(task_type)
        
        # Get responses from multiple providers
        responses = []
        for provider_type in providers[:3]:  # Use top 3 providers
            try:
                provider = self._get_ai_provider(provider_type)
                if provider and provider.health_status == 'healthy':
                    response = provider.execute_request(prompt, system_prompt)
                    responses.append({
                        'provider': provider_type,
                        'response': response,
                        'confidence': self._extract_confidence(response)
                    })
            except Exception as e:
                _logger.warning(f"Provider {provider_type} failed: {str(e)}")
                continue
        
        if not responses:
            raise UserError(_('No AI providers available'))
        
        # Simple consensus: return the response with highest confidence
        if responses:
            best_response = max(responses, key=lambda x: x['confidence'])
            return self._parse_ai_response(best_response['response'])
        else:
            raise UserError(_('No AI providers available'))
    
    def _get_single_ai_response(self, task_type, prompt, system_prompt, preferred_provider=None):
        """Get response from single AI provider"""
        ai_config = self._get_ai_config()
        
        if preferred_provider:
            providers = [preferred_provider]
        else:
            providers = ai_config.get_provider_priority(task_type)
        
        for provider_type in providers:
            try:
                provider = self._get_ai_provider(provider_type)
                if provider and provider.health_status == 'healthy':
                    response = provider.execute_request(prompt, system_prompt)
                    return self._parse_ai_response(response)
            except Exception as e:
                _logger.warning(f"Provider {provider_type} failed: {str(e)}")
                continue
        
        raise UserError(_('No AI providers available'))
    
    def _get_ai_provider(self, provider_type):
        """Get AI provider by type"""
        return self.env['hr.multi.ai.provider'].search([
            ('provider_type', '=', provider_type),
            ('active', '=', True),
            ('health_status', '=', 'healthy')
        ], limit=1)
    
    def _parse_ai_response(self, response):
        """Parse AI response into structured format"""
        content = response.get('content', '')
        
        # Try to parse JSON response
        try:
            if content.startswith('{') and content.endswith('}'):
                parsed = json.loads(content)
                parsed['confidence'] = response.get('usage', {}).get('confidence', 0.8)
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Return text response with default structure
        return {
            'analysis': content,
            'confidence': 0.7,  # Default confidence for text responses
        }
    
    def _extract_confidence(self, response):
        """Extract confidence score from AI response"""
        if isinstance(response, dict):
            return response.get('confidence', 0.7)
        return 0.7
    
    # Prompt building methods
    def _build_personality_analysis_prompt(self, employee_data):
        """Build prompt for personality analysis"""
        return f"""
        Analyze the personality traits of employee {employee_data.get('name', 'Unknown')} based on the following data:
        
        Employee Information:
        - Name: {employee_data.get('name', 'N/A')}
        - Department: {employee_data.get('department', 'N/A')}
        - Job Title: {employee_data.get('job_title', 'N/A')}
        - Tenure: {employee_data.get('hire_date', 'N/A')}
        
        Performance Data:
        {json.dumps(employee_data.get('performance_reviews', []), indent=2)}
        
        Communication Patterns:
        {json.dumps(employee_data.get('collaboration_indicators', {}), indent=2)}
        
        Please provide a comprehensive personality analysis including:
        1. Key personality traits
        2. Strengths and development areas
        3. Work style preferences
        4. Team collaboration style
        5. Leadership potential
        
        Format your response as JSON with the following structure:
        {{
            "analysis": "detailed analysis text",
            "traits": ["trait1", "trait2", ...],
            "strengths": ["strength1", "strength2", ...],
            "development_areas": ["area1", "area2", ...],
            "confidence": 0.85
        }}
        """
    
    def _build_skills_assessment_prompt(self, employee_data):
        """Build prompt for skills assessment"""
        return f"""
        Assess the skills and competencies of employee {employee_data.get('name', 'Unknown')}:
        
        Employee Profile:
        - Role: {employee_data.get('job_title', 'N/A')}
        - Department: {employee_data.get('department', 'N/A')}
        - Experience: {employee_data.get('tenure_months', 0)} months
        
        Performance History:
        {json.dumps(employee_data.get('performance_reviews', []), indent=2)}
        
        Training Records:
        {json.dumps(employee_data.get('completed_trainings', []), indent=2)}
        
        Project Involvement:
        {json.dumps(employee_data.get('project_history', []), indent=2)}
        
        Provide a comprehensive skills assessment including:
        1. Current skill levels
        2. Skill gaps for current role
        3. Skill gaps for career advancement
        4. Recommended training programs
        5. Priority areas for development
        
        Format as JSON:
        {{
            "assessment": "detailed assessment",
            "current_skills": ["skill1", "skill2", ...],
            "skill_gaps": "identified gaps",
            "recommendations": ["rec1", "rec2", ...],
            "confidence": 0.80
        }}
        """
    
    def _build_performance_prediction_prompt(self, employee_data):
        """Build prompt for performance prediction"""
        return f"""
        Predict future performance for employee {employee_data.get('name', 'Unknown')}:
        
        Current Performance Metrics:
        - Overall Score: {employee_data.get('performance_score', 'N/A')}
        - Productivity: {employee_data.get('productivity', 'N/A')}
        - Quality: {employee_data.get('quality', 'N/A')}
        - Collaboration: {employee_data.get('collaboration', 'N/A')}
        
        Historical Trends:
        {json.dumps(employee_data.get('performance_history', []), indent=2)}
        
        Environmental Factors:
        - Team Changes: {employee_data.get('team_changes', 'None')}
        - Role Changes: {employee_data.get('role_changes', 'None')}
        - Training Completed: {employee_data.get('recent_training', 'None')}
        
        Predict performance for the next 6-12 months including:
        1. Expected performance trajectory
        2. Key influencing factors
        3. Potential risks and opportunities
        4. Recommended interventions
        
        Format as JSON:
        {{
            "prediction": "detailed prediction",
            "productivity_score": 85,
            "key_factors": ["factor1", "factor2", ...],
            "timeline": "6-12 months outlook",
            "confidence": 0.75
        }}
        """
    
    def _build_sentiment_analysis_prompt(self, employee_data):
        """Build prompt for sentiment analysis"""
        return f"""
        Analyze the sentiment and emotional state of employee {employee_data.get('name', 'Unknown')}:
        
        Communication Data:
        {json.dumps(employee_data.get('communication', {}), indent=2)}
        
        Attendance Patterns:
        {json.dumps(employee_data.get('attendance', {}), indent=2)}
        
        Performance Indicators:
        {json.dumps(employee_data.get('performance', {}), indent=2)}
        
        Recent Feedback:
        {json.dumps(employee_data.get('feedback', {}), indent=2)}
        
        Analyze sentiment including:
        1. Overall emotional state
        2. Engagement level
        3. Stress indicators
        4. Satisfaction factors
        5. Trend direction
        
        Format as JSON:
        {{
            "sentiment_score": 0.65,
            "trend": "stable|improving|declining",
            "indicators": ["indicator1", "indicator2", ...],
            "recommendations": ["rec1", "rec2", ...],
            "confidence": 0.80
        }}
        """
    
    def _build_flight_risk_prompt(self, employee_data):
        """Build prompt for flight risk assessment"""
        return f"""
        Assess the flight risk for employee {employee_data.get('name', 'Unknown')}:
        
        Employee Profile:
        - Tenure: {employee_data.get('tenure_months', 0)} months
        - Performance: {employee_data.get('performance_score', 'N/A')}
        - Sentiment: {employee_data.get('sentiment_score', 'N/A')}
        
        Risk Indicators:
        - Recent performance changes
        - Engagement levels
        - Career progression
        - Compensation satisfaction
        - Work-life balance
        
        Historical Context:
        {json.dumps(employee_data.get('historical_data', {}), indent=2)}
        
        Assess flight risk including:
        1. Risk probability (0-1 scale)
        2. Key risk factors
        3. Timeline for potential departure
        4. Retention strategies
        
        Format as JSON:
        {{
            "risk_score": 0.35,
            "risk_factors": "identified factors",
            "retention_recommendations": "strategies",
            "timeline": "estimated timeframe",
            "confidence": 0.75
        }}
        """
    
    def _build_career_recommendations_prompt(self, employee_data):
        """Build prompt for career recommendations"""
        return f"""
        Generate career development recommendations for {employee_data.get('name', 'Unknown')}:
        
        Current Position:
        - Role: {employee_data.get('job_title', 'N/A')}
        - Level: {employee_data.get('level', 'N/A')}
        - Performance: {employee_data.get('performance_score', 'N/A')}
        
        Skills and Competencies:
        {json.dumps(employee_data.get('skills', {}), indent=2)}
        
        Career Interests:
        {json.dumps(employee_data.get('career_interests', []), indent=2)}
        
        Company Structure:
        {json.dumps(employee_data.get('company_structure', {}), indent=2)}
        
        Provide recommendations including:
        1. Career path options
        2. Skill development plan
        3. Learning opportunities
        4. Timeline and milestones
        
        Format as JSON:
        {{
            "recommendations": "detailed recommendations",
            "learning_plan": "development plan",
            "career_paths": ["path1", "path2", ...],
            "timeline": "development timeline",
            "confidence": 0.80
        }}
        """
    
    def _build_resume_analysis_prompt(self, candidate_data, job_requirements):
        """Build prompt for resume analysis"""
        return f"""
        Analyze candidate resume for job fit:
        
        Candidate Information:
        - Name: {candidate_data.get('name', 'N/A')}
        - Email: {candidate_data.get('email', 'N/A')}
        
        Resume Content:
        {candidate_data.get('resume_text', 'No resume content available')}
        
        Job Requirements:
        - Position: {job_requirements.get('job_title', 'N/A')}
        - Department: {job_requirements.get('department', 'N/A')}
        - Required Skills: {job_requirements.get('requirements', 'N/A')}
        - Experience Level: {job_requirements.get('experience_level', 'N/A')}
        
        Company Culture:
        {json.dumps(job_requirements.get('company_culture', {}), indent=2)}
        
        Analyze the candidate including:
        1. Skills match percentage
        2. Experience relevance
        3. Education fit
        4. Cultural alignment
        5. Strengths and concerns
        
        Format as JSON:
        {{
            "analysis": "detailed analysis",
            "skills_match": 85,
            "experience_relevance": 75,
            "education_fit": 90,
            "strengths": ["strength1", "strength2", ...],
            "concerns": ["concern1", "concern2", ...],
            "confidence": 0.85
        }}
        """
    
    def _build_chat_prompt(self, message, context, session_type):
        """Build prompt for chat response"""
        return f"""
        User Message: {message}
        
        Session Type: {session_type}
        
        User Context:
        - Name: {context.get('user_profile', {}).get('name', 'User')}
        - Department: {context.get('user_profile', {}).get('department', 'N/A')}
        - Role: {context.get('user_profile', {}).get('job_title', 'N/A')}
        
        Conversation History:
        {json.dumps(context.get('conversation_history', [])[-5:], indent=2)}
        
        Company Policies:
        {json.dumps(context.get('company_policies', {}), indent=2)}
        
        Provide a helpful, accurate, and professional response. If the query requires human intervention or involves sensitive matters, indicate escalation is needed.
        
        Format as JSON:
        {{
            "response": "your response text",
            "requires_escalation": false,
            "escalation_reason": "",
            "suggested_actions": ["action1", "action2", ...],
            "confidence": 0.90
        }}
        """
    
    def _get_chat_system_prompt(self, session_type):
        """Get system prompt for chat based on session type"""
        base_prompt = "You are a helpful HR assistant providing accurate information and support to employees."
        
        session_prompts = {
            'policy_question': base_prompt + " Focus on company policies and procedures.",
            'benefits_info': base_prompt + " Specialize in employee benefits and compensation information.",
            'leave_request': base_prompt + " Help with leave requests and time-off policies.",
            'performance_query': base_prompt + " Assist with performance-related questions and feedback.",
            'career_guidance': base_prompt + " Provide career development and growth guidance.",
            'training_info': base_prompt + " Focus on training opportunities and professional development.",
            'complaint_report': base_prompt + " Handle sensitive matters with care and escalate when appropriate.",
            'technical_support': base_prompt + " Provide technical support for HR systems and tools.",
        }
        
        return session_prompts.get(session_type, base_prompt) 