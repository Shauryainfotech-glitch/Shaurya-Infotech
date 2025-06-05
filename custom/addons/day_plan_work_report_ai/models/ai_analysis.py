from odoo import models, fields, api, _
import logging
import json
import requests
from datetime import datetime, timedelta
from lxml import etree

_logger = logging.getLogger(__name__)

class AIAnalysis(models.Model):
    _name = "ai.analysis"
    _description = "AI Generated Analysis and Insights"
    # Explicitly NOT inheriting mail.thread to avoid document-related fields
    _order = "create_date desc"
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Override to completely replace the form view with our custom one"""
        res = super(AIAnalysis, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
        if view_type == 'form':
            # Get our custom form view
            custom_view = self.env.ref('day_plan_work_report_ai.view_ai_analysis_form')
            custom_res = super(AIAnalysis, self).fields_view_get(
                view_id=custom_view.id, view_type='form', toolbar=toolbar, submenu=submenu)
            return custom_res
            
        return res
    
    def create_new_ai_analysis(self):
        """Create a new AI Analysis record directly without document fields"""
        # First create a new record
        new_analysis = self.create({
            'name': 'New AI Analysis',
            'user_id': self.env.user.id,
            'date': fields.Date.today(),
        })
        
        # Then open it with the clean form view
        return {
            'type': 'ir.actions.act_window',
            'name': _('New AI Analysis'),
            'res_model': 'ai.analysis',
            'res_id': new_analysis.id,
            'view_mode': 'form',
            'view_id': self.env.ref('day_plan_work_report_ai.view_ai_analysis_clean_form').id,
            'target': 'fullscreen',
            'context': {
                'hide_chatter': True,
                'hide_message': True,
                'form_view_initial_mode': 'edit',
                'no_breadcrumbs': True,
            },
            'flags': {
                'form': {
                    'action_buttons': True,
                }
            }
        }

    # Basic Fields
    name = fields.Char(string="Analysis ID", readonly=True, copy=False, default="New")
    work_report_id = fields.Many2one('work.report', string="Work Report")
    day_plan_id = fields.Many2one('day.plan', string="Day Plan")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)
    date = fields.Date(string="Analysis Date", default=fields.Date.today)
    
    # Analysis Type
    analysis_type = fields.Selection([
        ('daily', 'Daily Plan Analysis'),
        ('work_report', 'Work Report Analysis'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Review'),
        ('trend', 'Productivity Trend')
    ], string="Analysis Type", required=True, default='daily')
    
    # AI Provider Configuration
    provider = fields.Selection([
        ('openai', 'OpenAI (GPT-4)'),
        ('anthropic', 'Anthropic (Claude)'),
        ('google', 'Google (Gemini)'),
        ('mock', 'Mock Provider (Testing)')
    ], string="AI Provider", required=True, default='openai')
    
    model_version = fields.Char(string="Model Version", help="Specific model version used for analysis")
    prompt_template_id = fields.Many2one('ai.prompt.template', string="Prompt Template")
    raw_prompt = fields.Text(string="Raw Prompt", help="The actual prompt sent to the AI provider")
    raw_response = fields.Text(string="Raw Response", help="The complete raw response from the AI provider")
    
    # Analysis Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('done', 'Completed'),
        ('failed', 'Failed')
    ], string="Status", default='draft')
    error_message = fields.Text(string="Error Message")
    
    # Metrics and Insights
    productivity_score = fields.Float(string="Productivity Score", 
                                     help="Overall productivity rating from 0-100")
    efficiency_rating = fields.Float(string="Efficiency Rating",
                                    help="Measure of time management effectiveness from 0-100")
    wellbeing_assessment = fields.Float(string="Wellbeing Assessment",
                                       help="Work-life balance indicator from 0-100")
    focus_score = fields.Float(string="Focus Score",
                              help="Ability to maintain concentration on priority tasks")
    
    # Textual Analysis
    summary = fields.Text(string="Summary", help="Brief overview of the analysis")
    strengths = fields.Text(string="Strengths", help="Areas where performance was strong")
    improvement_areas = fields.Text(string="Areas for Improvement")
    recommendations = fields.Text(string="Recommendations", help="Actionable suggestions")
    trend_analysis = fields.Text(string="Trend Analysis", help="Patterns observed over time")
    
    # Time Analysis
    time_allocation = fields.Json(string="Time Allocation", 
                                 help="Breakdown of time spent on different categories")
    task_completion_rate = fields.Float(string="Task Completion Rate", 
                                       help="Percentage of planned tasks completed")
    
    # Related Records
    related_analysis_ids = fields.Many2many('ai.analysis', 'ai_analysis_rel', 
                                          'analysis_id', 'related_id', 
                                          string="Related Analyses")
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('ai.analysis') or 'New'
        return super(AIAnalysis, self).create(vals_list)
    
    def action_process(self):
        """Trigger AI analysis processing"""
        self.ensure_one()
        self.state = 'processing'
        
        try:
            # Generate prompt based on analysis type and context
            prompt = self._prepare_prompt()
            self.raw_prompt = prompt
            
            # Call appropriate AI provider
            if self.provider == 'openai':
                response = self._call_openai(prompt)
            elif self.provider == 'anthropic':
                response = self._call_anthropic(prompt)
            elif self.provider == 'google':
                response = self._call_google(prompt)
            elif self.provider == 'mock':
                response = self._call_mock_provider(prompt)
            else:
                raise ValueError(f"Unsupported AI provider: {self.provider}")
            
            # Process the response
            self.raw_response = response
            self._process_ai_response(response)
            
            self.state = 'done'
            return True
            
        except Exception as e:
            self.state = 'failed'
            self.error_message = str(e)
            _logger.error(f"AI Analysis failed: {str(e)}")
            return False
    
    def _prepare_prompt(self):
        """Prepare the prompt based on analysis type and context"""
        if self.prompt_template_id:
            template = self.prompt_template_id.template
        else:
            # Get default template based on analysis type
            template = self._get_default_prompt_template()
        
        # Gather context data based on analysis type
        context_data = {}
        if self.analysis_type == 'daily':
            context_data = self._gather_daily_plan_data()
        elif self.analysis_type == 'work_report':
            context_data = self._gather_work_report_data()
        elif self.analysis_type == 'weekly':
            context_data = self._gather_weekly_data()
        elif self.analysis_type == 'monthly':
            context_data = self._gather_monthly_data()
        elif self.analysis_type == 'trend':
            context_data = self._gather_trend_data()
        
        # Format the prompt with context data
        prompt = template.format(**context_data)
        return prompt
    
    def _get_default_prompt_template(self):
        """Get default prompt template based on analysis type"""
        if self.analysis_type == 'daily':
            return """
            Analyze the following day plan and completed tasks:
            
            User: {user_name}
            Date: {date}
            
            Plan Title: {plan_title}
            Goals: {goals}
            
            Tasks:
            {tasks}
            
            Task Completion Rate: {completion_rate}%
            
            Please provide:
            1. A productivity score (0-100)
            2. An efficiency rating (0-100)
            3. A wellbeing assessment (0-100)
            4. Key strengths observed
            5. Areas for improvement
            6. Specific actionable recommendations
            7. Time allocation analysis
            
            Format your response as JSON with the following structure:
            {
                "productivity_score": 85,
                "efficiency_rating": 80,
                "wellbeing_assessment": 75,
                "summary": "Brief overview...",
                "strengths": "Areas of strong performance...",
                "improvement_areas": "Areas needing improvement...",
                "recommendations": "Specific actionable suggestions...",
                "time_allocation": {"category1": percentage, "category2": percentage}
            }
            """
        elif self.analysis_type == 'work_report':
            return """
            Analyze the following work report:
            
            User: {user_name}
            Date: {date}
            
            Accomplishments: {accomplishments}
            Challenges: {challenges}
            Solutions: {solutions}
            
            Self-Assessment:
            - Productivity: {self_productivity}
            - Quality: {self_quality}
            - Satisfaction: {self_satisfaction}
            
            Learnings: {learnings}
            Next Steps: {next_steps}
            
            Please provide:
            1. A productivity score (0-100)
            2. An efficiency rating (0-100)
            3. A wellbeing assessment (0-100)
            4. Key strengths observed
            5. Areas for improvement
            6. Specific actionable recommendations
            
            Format your response as JSON with the following structure:
            {
                "productivity_score": 85,
                "efficiency_rating": 80,
                "wellbeing_assessment": 75,
                "summary": "Brief overview...",
                "strengths": "Areas of strong performance...",
                "improvement_areas": "Areas needing improvement...",
                "recommendations": "Specific actionable suggestions..."
            }
            """
        # Add templates for other analysis types
        return "Please analyze the provided data and provide insights."
    
    def _gather_daily_plan_data(self):
        """Gather data for daily plan analysis"""
        plan = self.day_plan_id
        if not plan:
            return {}
            
        tasks = []
        completion_rate = 0
        if plan.task_ids:
            completed_tasks = len(plan.task_ids.filtered(lambda t: t.status == 'done'))
            total_tasks = len(plan.task_ids)
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks else 0
            
            for task in plan.task_ids:
                tasks.append({
                    'name': task.name,
                    'status': task.status,
                    'priority': task.priority,
                    'estimated_hours': task.estimated_hours,
                    'actual_hours': task.actual_hours,
                    'progress': task.progress
                })
        
        return {
            'user_name': plan.employee_id.name or self.env.user.name,
            'date': plan.date,
            'plan_title': plan.name,
            'goals': plan.goals,
            'tasks': json.dumps(tasks),
            'completion_rate': completion_rate
        }
    
    def _gather_work_report_data(self):
        """Gather data for work report analysis"""
        report = self.work_report_id
        if not report:
            return {}
            
        return {
            'user_name': self.env.user.name,
            'date': fields.Date.today(),
            'accomplishments': report.accomplishments or '',
            'challenges': report.challenges or '',
            'solutions': report.solutions or '',
            'self_productivity': report.self_assessment_productivity or '',
            'self_quality': report.self_assessment_quality or '',
            'self_satisfaction': report.self_assessment_satisfaction or '',
            'learnings': report.learnings or '',
            'next_steps': report.next_steps or ''
        }
    
    def _gather_weekly_data(self):
        """Gather data for weekly summary analysis"""
        today = fields.Date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        
        # Get all day plans for the week
        plans = self.env['day.plan'].search([
            ('employee_id', '=', self.env.user.employee_id.id),
            ('date', '>=', start_date),
            ('date', '<=', end_date)
        ])
        
        # Get all work reports for the week
        reports = self.env['work.report'].search([
            ('day_plan_id', 'in', plans.ids)
        ])
        
        # Compile weekly data
        weekly_data = {
            'user_name': self.env.user.name,
            'start_date': start_date,
            'end_date': end_date,
            'total_plans': len(plans),
            'total_reports': len(reports),
            'plans': [],
            'reports': []
        }
        
        for plan in plans:
            weekly_data['plans'].append({
                'date': plan.date,
                'title': plan.name,
                'goals': plan.goals,
                'task_count': len(plan.task_ids),
                'completed_tasks': len(plan.task_ids.filtered(lambda t: t.status == 'done'))
            })
            
        for report in reports:
            weekly_data['reports'].append({
                'date': report.day_plan_id.date,
                'accomplishments': report.accomplishments,
                'challenges': report.challenges
            })
            
        return weekly_data
    
    def _gather_monthly_data(self):
        """Gather data for monthly review analysis"""
        today = fields.Date.today()
        start_date = today.replace(day=1)
        
        # Calculate end of month
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        # Similar to weekly but with monthly date range
        # Implementation similar to _gather_weekly_data
        return {
            'user_name': self.env.user.name,
            'month': today.strftime('%B %Y'),
            'start_date': start_date,
            'end_date': end_date
        }
    
    def _gather_trend_data(self):
        """Gather data for productivity trend analysis"""
        # Get last 30 days of data
        end_date = fields.Date.today()
        start_date = end_date - timedelta(days=30)
        
        # Get all analyses in the period
        analyses = self.search([
            ('user_id', '=', self.env.user.id),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('state', '=', 'done')
        ])
        
        trend_data = {
            'user_name': self.env.user.name,
            'period': f"{start_date} to {end_date}",
            'analyses': []
        }
        
        for analysis in analyses:
            trend_data['analyses'].append({
                'date': analysis.date,
                'type': analysis.analysis_type,
                'productivity_score': analysis.productivity_score,
                'efficiency_rating': analysis.efficiency_rating,
                'wellbeing_assessment': analysis.wellbeing_assessment
            })
            
        return trend_data
    
    def _call_openai(self, prompt):
        """Call OpenAI API"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('ai_analysis.openai_api_key')
        if not api_key:
            raise ValueError("OpenAI API key not configured")
            
        try:
            import openai
            openai.api_key = api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that analyzes work productivity data and provides insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            self.model_version = "gpt-4"
            return response.choices[0].message.content
            
        except ImportError:
            _logger.error("OpenAI Python package not installed")
            raise ValueError("OpenAI Python package not installed. Install with: pip install openai")
        except Exception as e:
            _logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _call_anthropic(self, prompt):
        """Call Anthropic Claude API"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('ai_analysis.anthropic_api_key')
        if not api_key:
            raise ValueError("Anthropic API key not configured")
            
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                temperature=0.2,
                system="You are an AI assistant that analyzes work productivity data and provides insights.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            self.model_version = "claude-3-opus"
            return response.content[0].text
            
        except ImportError:
            _logger.error("Anthropic Python package not installed")
            raise ValueError("Anthropic Python package not installed. Install with: pip install anthropic")
        except Exception as e:
            _logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def _call_google(self, prompt):
        """Call Google Gemini API"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('ai_analysis.google_api_key')
        if not api_key:
            raise ValueError("Google API key not configured")
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            self.model_version = "gemini-pro"
            return response.text
            
        except ImportError:
            _logger.error("Google Generative AI package not installed")
            raise ValueError("Google Generative AI package not installed. Install with: pip install google-generativeai")
        except Exception as e:
            _logger.error(f"Google API error: {str(e)}")
            raise
    
    def _call_mock_provider(self, prompt):
        """Mock AI provider for testing"""
        _logger.info(f"Mock AI provider called with prompt: {prompt}")
        
        # Generate a mock response
        mock_response = {
            "productivity_score": 75,
            "efficiency_rating": 70,
            "wellbeing_assessment": 80,
            "summary": "This is a mock analysis for testing purposes.",
            "strengths": "Good task organization and prioritization.",
            "improvement_areas": "Could improve time estimation accuracy.",
            "recommendations": "Consider breaking down large tasks into smaller subtasks.",
            "time_allocation": {"planning": 20, "execution": 60, "review": 20}
        }
        
        self.model_version = "mock-v1"
        return json.dumps(mock_response)
    
    def _process_ai_response(self, response):
        """Process the AI response and extract metrics"""
        try:
            # Try to parse as JSON
            data = json.loads(response)
            
            # Update fields from the parsed response
            if isinstance(data, dict):
                for field in ['productivity_score', 'efficiency_rating', 'wellbeing_assessment', 
                             'summary', 'strengths', 'improvement_areas', 'recommendations']:
                    if field in data:
                        setattr(self, field, data[field])
                
                # Handle time allocation if present
                if 'time_allocation' in data and isinstance(data['time_allocation'], dict):
                    self.time_allocation = json.dumps(data['time_allocation'])
                    
                # Handle focus score if present
                if 'focus_score' in data:
                    self.focus_score = data['focus_score']
                    
                # Handle task completion rate if present
                if 'task_completion_rate' in data:
                    self.task_completion_rate = data['task_completion_rate']
                    
                # Handle trend analysis if present
                if 'trend_analysis' in data:
                    self.trend_analysis = data['trend_analysis']
                    
        except json.JSONDecodeError:
            # If not JSON, try to extract information using regex or other methods
            _logger.warning("AI response was not in JSON format, using fallback extraction")
            
            # Set summary to the raw response if we couldn't parse it
            self.summary = "AI provided a non-structured response. See raw response for details."
            
            # Try to extract scores using simple heuristics
            import re
            
            # Try to find productivity score
            productivity_match = re.search(r'productivity\s*(?:score|rating)?\s*:?\s*(\d+)', response, re.IGNORECASE)
            if productivity_match:
                self.productivity_score = float(productivity_match.group(1))
                
            # Try to find efficiency rating
            efficiency_match = re.search(r'efficiency\s*(?:score|rating)?\s*:?\s*(\d+)', response, re.IGNORECASE)
            if efficiency_match:
                self.efficiency_rating = float(efficiency_match.group(1))
                
            # Try to find wellbeing assessment
            wellbeing_match = re.search(r'wellbeing\s*(?:score|assessment|rating)?\s*:?\s*(\d+)', response, re.IGNORECASE)
            if wellbeing_match:
                self.wellbeing_assessment = float(wellbeing_match.group(1))

    def action_view_day_plan(self):
        """Open the related day plan form view"""
        self.ensure_one()
        if not self.day_plan_id:
            return
            
        return {
            'name': 'Day Plan',
            'type': 'ir.actions.act_window',
            'res_model': 'day.plan',
            'view_mode': 'form',
            'res_id': self.day_plan_id.id,
            'target': 'current',
        }
        
    def action_view_work_report(self):
        """Open the related work report form view"""
        self.ensure_one()
        if not self.work_report_id:
            return
            
        return {
            'name': 'Work Report',
            'type': 'ir.actions.act_window',
            'res_model': 'work.report',
            'view_mode': 'form',
            'res_id': self.work_report_id.id,
            'target': 'current',
        }


class AIPromptTemplate(models.Model):
    _name = "ai.prompt.template"
    _description = "AI Prompt Templates"
    
    name = fields.Char(string="Template Name", required=True)
    analysis_type = fields.Selection([
        ('daily', 'Daily Plan Analysis'),
        ('work_report', 'Work Report Analysis'),
        ('weekly', 'Weekly Summary'),
        ('monthly', 'Monthly Review'),
        ('trend', 'Productivity Trend')
    ], string="Analysis Type", required=True)
    
    template = fields.Text(string="Prompt Template", required=True, 
                         help="Use {variable} syntax for dynamic content")
    description = fields.Text(string="Description", 
                            help="Explain what this template is designed to analyze")
    is_default = fields.Boolean(string="Default Template", 
                              help="Use this as the default template for this analysis type")
    
    _sql_constraints = [
        ('unique_default_per_type', 
         'UNIQUE(analysis_type, is_default)', 
         'Only one default template allowed per analysis type')
    ]
