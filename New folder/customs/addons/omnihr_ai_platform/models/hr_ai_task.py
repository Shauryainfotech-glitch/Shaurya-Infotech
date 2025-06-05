from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class HRAITask(models.Model):
    _name = 'hr.ai.task'
    _description = 'AI-Powered HR Tasks'
    _rec_name = 'task_name'
    _order = 'priority desc, create_date desc'
    
    task_name = fields.Char('Task Name', required=True)
    task_type = fields.Selection([
        ('employee_onboarding', 'Employee Onboarding'),
        ('performance_review', 'Performance Review'),
        ('training_assignment', 'Training Assignment'),
        ('policy_update', 'Policy Update'),
        ('compliance_check', 'Compliance Check'),
        ('sentiment_monitoring', 'Sentiment Monitoring'),
        ('recruitment_screening', 'Recruitment Screening'),
        ('exit_interview', 'Exit Interview'),
        ('benefits_enrollment', 'Benefits Enrollment'),
        ('document_generation', 'Document Generation'),
    ], 'Task Type', required=True)
    
    # Task Details
    description = fields.Text('Task Description')
    instructions = fields.Text('AI Instructions')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], 'Priority', default='medium')
    
    # Assignment
    assigned_to = fields.Many2one('res.users', 'Assigned To')
    employee_id = fields.Many2one('hr.employee', 'Related Employee')
    department_id = fields.Many2one('hr.department', 'Related Department')
    
    # Status and Progress
    task_status = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('in_progress', 'In Progress'),
        ('ai_processing', 'AI Processing'),
        ('human_review', 'Human Review Required'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], 'Task Status', default='draft')
    
    progress_percentage = fields.Float('Progress %', default=0)
    completion_date = fields.Datetime('Completion Date')
    
    # AI Processing
    ai_model_used = fields.Char('AI Model Used')
    ai_confidence = fields.Float('AI Confidence Score')
    ai_processing_time = fields.Float('AI Processing Time (seconds)')
    ai_result = fields.Text('AI Processing Result')
    
    # Automation
    is_automated = fields.Boolean('Automated Task', default=True)
    automation_trigger = fields.Selection([
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('event_based', 'Event-Based'),
        ('condition_based', 'Condition-Based'),
    ], 'Automation Trigger', default='manual')
    
    schedule_date = fields.Datetime('Scheduled Date')
    recurring = fields.Boolean('Recurring Task')
    recurrence_pattern = fields.Char('Recurrence Pattern')
    
    # Dependencies
    dependency_ids = fields.Many2many('hr.ai.task', 'hr_ai_task_dependency_rel', 
                                     'task_id', 'dependency_id', 'Dependencies')
    dependent_task_ids = fields.Many2many('hr.ai.task', 'hr_ai_task_dependency_rel', 
                                         'dependency_id', 'task_id', 'Dependent Tasks')
    
    # Results and Output
    output_data = fields.Text('Output Data')
    generated_documents = fields.Text('Generated Documents')
    recommendations = fields.Text('AI Recommendations')
    
    # Metrics
    execution_time = fields.Float('Total Execution Time (minutes)')
    human_intervention_required = fields.Boolean('Human Intervention Required')
    quality_score = fields.Float('Quality Score')
    
    def execute_task(self):
        """Execute the AI task"""
        if self.task_status not in ['draft', 'queued']:
            raise UserError(_('Task can only be executed from draft or queued status'))
        
        self.task_status = 'in_progress'
        self.progress_percentage = 10
        
        try:
            # Check dependencies
            if not self._check_dependencies():
                raise UserError(_('Task dependencies are not met'))
            
            self.task_status = 'ai_processing'
            self.progress_percentage = 30
            
            # Execute based on task type
            result = self._execute_by_type()
            
            # Process AI result
            self._process_ai_result(result)
            
            # Check if human review is needed
            if self._requires_human_review(result):
                self.task_status = 'human_review'
                self.progress_percentage = 80
                self._notify_human_reviewer()
            else:
                self._complete_task(result)
            
        except Exception as e:
            self._handle_task_failure(str(e))
    
    def _check_dependencies(self):
        """Check if all task dependencies are completed"""
        for dependency in self.dependency_ids:
            if dependency.task_status != 'completed':
                return False
        return True
    
    def _execute_by_type(self):
        """Execute task based on its type"""
        ai_orchestrator = self.env['hr.ai.orchestrator']
        
        if self.task_type == 'employee_onboarding':
            return self._execute_onboarding_task(ai_orchestrator)
        elif self.task_type == 'performance_review':
            return self._execute_performance_review_task(ai_orchestrator)
        elif self.task_type == 'training_assignment':
            return self._execute_training_assignment_task(ai_orchestrator)
        elif self.task_type == 'compliance_check':
            return self._execute_compliance_check_task(ai_orchestrator)
        elif self.task_type == 'sentiment_monitoring':
            return self._execute_sentiment_monitoring_task(ai_orchestrator)
        elif self.task_type == 'recruitment_screening':
            return self._execute_recruitment_screening_task(ai_orchestrator)
        elif self.task_type == 'document_generation':
            return self._execute_document_generation_task(ai_orchestrator)
        else:
            return self._execute_generic_task(ai_orchestrator)
    
    def _execute_onboarding_task(self, ai_orchestrator):
        """Execute employee onboarding task"""
        if not self.employee_id:
            raise UserError(_('Employee is required for onboarding task'))
        
        employee_data = {
            'employee_id': self.employee_id.id,
            'name': self.employee_id.name,
            'department': self.employee_id.department_id.name if self.employee_id.department_id else '',
            'job_title': self.employee_id.job_title or '',
            'start_date': self.employee_id.create_date.strftime('%Y-%m-%d'),
        }
        
        return ai_orchestrator.generate_onboarding_plan(employee_data)
    
    def _execute_performance_review_task(self, ai_orchestrator):
        """Execute performance review task"""
        if not self.employee_id:
            raise UserError(_('Employee is required for performance review task'))
        
        # Get performance data
        performance_data = self._gather_performance_data()
        
        return ai_orchestrator.generate_performance_review(performance_data)
    
    def _execute_training_assignment_task(self, ai_orchestrator):
        """Execute training assignment task"""
        if self.employee_id:
            # Individual training assignment
            employee_data = self._gather_employee_training_data()
            return ai_orchestrator.recommend_training(employee_data)
        elif self.department_id:
            # Department-wide training assignment
            department_data = self._gather_department_training_data()
            return ai_orchestrator.recommend_department_training(department_data)
        else:
            raise UserError(_('Employee or Department is required for training assignment'))
    
    def _execute_compliance_check_task(self, ai_orchestrator):
        """Execute compliance check task"""
        compliance_data = {
            'employee_id': self.employee_id.id if self.employee_id else None,
            'department_id': self.department_id.id if self.department_id else None,
            'check_type': 'general_compliance',
            'regulations': self._get_applicable_regulations(),
        }
        
        return ai_orchestrator.perform_compliance_check(compliance_data)
    
    def _execute_sentiment_monitoring_task(self, ai_orchestrator):
        """Execute sentiment monitoring task"""
        if self.employee_id:
            # Individual sentiment monitoring
            sentiment_data = self._gather_employee_sentiment_data()
            return ai_orchestrator.monitor_employee_sentiment(sentiment_data)
        elif self.department_id:
            # Department sentiment monitoring
            department_sentiment_data = self._gather_department_sentiment_data()
            return ai_orchestrator.monitor_department_sentiment(department_sentiment_data)
        else:
            # Company-wide sentiment monitoring
            company_sentiment_data = self._gather_company_sentiment_data()
            return ai_orchestrator.monitor_company_sentiment(company_sentiment_data)
    
    def _execute_recruitment_screening_task(self, ai_orchestrator):
        """Execute recruitment screening task"""
        # Get recent applicants for screening
        applicants = self.env['hr.applicant'].search([
            ('stage_id.name', 'ilike', 'initial'),
        ], limit=10)
        
        screening_data = {
            'applicants': [self._get_applicant_data(app) for app in applicants],
            'job_requirements': self._get_job_requirements(),
        }
        
        return ai_orchestrator.screen_candidates(screening_data)
    
    def _execute_document_generation_task(self, ai_orchestrator):
        """Execute document generation task"""
        document_data = {
            'document_type': self.instructions,
            'employee_id': self.employee_id.id if self.employee_id else None,
            'template_data': self._gather_template_data(),
        }
        
        return ai_orchestrator.generate_hr_document(document_data)
    
    def _execute_generic_task(self, ai_orchestrator):
        """Execute generic AI task"""
        task_data = {
            'task_type': self.task_type,
            'instructions': self.instructions,
            'context_data': self._gather_context_data(),
        }
        
        return ai_orchestrator.execute_generic_task(task_data)
    
    def _process_ai_result(self, result):
        """Process the AI task result"""
        self.ai_result = json.dumps(result) if isinstance(result, dict) else str(result)
        self.ai_confidence = result.get('confidence', 0) if isinstance(result, dict) else 0
        self.recommendations = result.get('recommendations', '') if isinstance(result, dict) else ''
        self.output_data = result.get('output_data', '') if isinstance(result, dict) else ''
        
        # Update progress
        self.progress_percentage = 70
    
    def _requires_human_review(self, result):
        """Determine if human review is required"""
        if isinstance(result, dict):
            # Check confidence threshold
            if result.get('confidence', 0) < 0.8:
                return True
            
            # Check for sensitive content
            if result.get('requires_human_review', False):
                return True
            
            # Check for high-risk decisions
            if self.task_type in ['compliance_check', 'performance_review'] and result.get('risk_level', 'low') == 'high':
                return True
        
        return False
    
    def _complete_task(self, result):
        """Complete the task"""
        self.task_status = 'completed'
        self.progress_percentage = 100
        self.completion_date = fields.Datetime.now()
        
        # Execute post-completion actions
        self._execute_post_completion_actions(result)
        
        # Trigger dependent tasks
        self._trigger_dependent_tasks()
    
    def _handle_task_failure(self, error_message):
        """Handle task failure"""
        self.task_status = 'failed'
        self.ai_result = f"Task failed: {error_message}"
        
        _logger.error(f"AI Task {self.task_name} failed: {error_message}")
        
        # Notify assigned user
        if self.assigned_to:
            self.env['mail.mail'].create({
                'subject': f'AI Task Failed: {self.task_name}',
                'body_html': f'''
                    <p>AI Task has failed and requires attention.</p>
                    <p><strong>Task:</strong> {self.task_name}</p>
                    <p><strong>Error:</strong> {error_message}</p>
                    <p><a href="/web#id={self.id}&model=hr.ai.task">View Task</a></p>
                ''',
                'email_to': self.assigned_to.email,
            }).send()
    
    def _notify_human_reviewer(self):
        """Notify human reviewer"""
        if self.assigned_to:
            self.env['mail.mail'].create({
                'subject': f'AI Task Requires Review: {self.task_name}',
                'body_html': f'''
                    <p>AI Task requires human review before completion.</p>
                    <p><strong>Task:</strong> {self.task_name}</p>
                    <p><strong>AI Confidence:</strong> {self.ai_confidence:.2f}</p>
                    <p><a href="/web#id={self.id}&model=hr.ai.task">Review Task</a></p>
                ''',
                'email_to': self.assigned_to.email,
            }).send()
    
    def approve_task(self):
        """Approve task after human review"""
        if self.task_status != 'human_review':
            raise UserError(_('Task is not in human review status'))
        
        result = json.loads(self.ai_result) if self.ai_result else {}
        self._complete_task(result)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Task approved and completed successfully'),
                'type': 'success'
            }
        }
    
    def reject_task(self, reason):
        """Reject task after human review"""
        if self.task_status != 'human_review':
            raise UserError(_('Task is not in human review status'))
        
        self.task_status = 'failed'
        self.ai_result = f"Task rejected by human reviewer: {reason}"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Task rejected'),
                'type': 'warning'
            }
        }
    
    def _trigger_dependent_tasks(self):
        """Trigger dependent tasks when this task is completed"""
        for dependent_task in self.dependent_task_ids:
            if dependent_task.task_status == 'queued' and dependent_task._check_dependencies():
                dependent_task.execute_task()
    
    def _execute_post_completion_actions(self, result):
        """Execute actions after task completion"""
        # This can be overridden for specific task types
        pass
    
    # Helper methods for gathering data
    def _gather_performance_data(self):
        """Gather performance data for the employee"""
        return {
            'employee_id': self.employee_id.id,
            'performance_records': [],  # Would get actual performance data
            'goals': [],  # Would get employee goals
            'feedback': [],  # Would get feedback data
        }
    
    def _gather_employee_training_data(self):
        """Gather training data for employee"""
        return {
            'employee_id': self.employee_id.id,
            'current_skills': [],
            'skill_gaps': [],
            'career_goals': [],
            'training_history': [],
        }
    
    def _gather_department_training_data(self):
        """Gather training data for department"""
        return {
            'department_id': self.department_id.id,
            'employees': [],
            'skill_matrix': {},
            'training_budget': 0,
        }
    
    def _get_applicable_regulations(self):
        """Get applicable regulations for compliance check"""
        return ['GDPR', 'SOX', 'OSHA']  # Placeholder
    
    def _gather_employee_sentiment_data(self):
        """Gather sentiment data for employee"""
        return {
            'employee_id': self.employee_id.id,
            'recent_communications': [],
            'survey_responses': [],
            'performance_indicators': {},
        }
    
    def _gather_department_sentiment_data(self):
        """Gather sentiment data for department"""
        return {
            'department_id': self.department_id.id,
            'employee_count': 0,
            'recent_surveys': [],
            'turnover_rate': 0,
        }
    
    def _gather_company_sentiment_data(self):
        """Gather sentiment data for company"""
        return {
            'total_employees': 0,
            'department_breakdown': {},
            'recent_initiatives': [],
            'overall_metrics': {},
        }
    
    def _get_applicant_data(self, applicant):
        """Get applicant data for screening"""
        return {
            'applicant_id': applicant.id,
            'name': applicant.partner_name,
            'email': applicant.email_from,
            'resume': '',  # Would extract resume content
            'application_date': applicant.create_date.strftime('%Y-%m-%d'),
        }
    
    def _get_job_requirements(self):
        """Get job requirements for screening"""
        return {
            'required_skills': [],
            'experience_level': '',
            'education_requirements': '',
            'cultural_fit_criteria': [],
        }
    
    def _gather_template_data(self):
        """Gather data for document template"""
        return {
            'employee_data': {},
            'company_data': {},
            'custom_fields': {},
        }
    
    def _gather_context_data(self):
        """Gather context data for generic task"""
        return {
            'employee_id': self.employee_id.id if self.employee_id else None,
            'department_id': self.department_id.id if self.department_id else None,
            'task_context': self.description,
        } 