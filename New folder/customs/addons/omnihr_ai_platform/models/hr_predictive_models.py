from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class HRPredictiveModels(models.Model):
    _name = 'hr.predictive.models'
    _description = 'HR Predictive Analytics Models'
    _rec_name = 'model_name'
    
    model_name = fields.Char('Model Name', required=True)
    model_type = fields.Selection([
        ('turnover_prediction', 'Employee Turnover Prediction'),
        ('performance_forecast', 'Performance Forecasting'),
        ('hiring_success', 'Hiring Success Prediction'),
        ('promotion_readiness', 'Promotion Readiness'),
        ('training_effectiveness', 'Training Effectiveness'),
        ('team_dynamics', 'Team Dynamics Analysis'),
        ('compensation_optimization', 'Compensation Optimization'),
        ('workforce_planning', 'Workforce Planning'),
    ], 'Model Type', required=True)
    
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    
    # Model Configuration
    model_description = fields.Text('Model Description')
    input_features = fields.Text('Input Features', help='JSON list of features used by the model')
    target_variable = fields.Char('Target Variable')
    algorithm_type = fields.Selection([
        ('linear_regression', 'Linear Regression'),
        ('logistic_regression', 'Logistic Regression'),
        ('random_forest', 'Random Forest'),
        ('neural_network', 'Neural Network'),
        ('ensemble', 'Ensemble Method'),
    ], 'Algorithm Type')
    
    # Model Performance
    accuracy_score = fields.Float('Accuracy Score')
    precision_score = fields.Float('Precision Score')
    recall_score = fields.Float('Recall Score')
    f1_score = fields.Float('F1 Score')
    last_training_date = fields.Datetime('Last Training Date')
    
    # Model Status
    model_status = fields.Selection([
        ('draft', 'Draft'),
        ('training', 'Training'),
        ('trained', 'Trained'),
        ('deployed', 'Deployed'),
        ('deprecated', 'Deprecated'),
    ], 'Model Status', default='draft')
    
    # Predictions
    prediction_ids = fields.One2many('hr.predictive.prediction', 'model_id', 'Predictions')
    
    def train_model(self):
        """Train the predictive model"""
        try:
            self.model_status = 'training'
            
            # Get AI orchestrator service
            ai_orchestrator = self.env['hr.ai.orchestrator']
            
            # Gather training data based on model type
            training_data = self._gather_training_data()
            
            # Train the model
            training_result = ai_orchestrator.train_predictive_model(
                model_type=self.model_type,
                training_data=training_data,
                algorithm=self.algorithm_type
            )
            
            # Update model performance metrics
            self.accuracy_score = training_result.get('accuracy', 0)
            self.precision_score = training_result.get('precision', 0)
            self.recall_score = training_result.get('recall', 0)
            self.f1_score = training_result.get('f1_score', 0)
            self.last_training_date = fields.Datetime.now()
            self.model_status = 'trained'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Model training completed successfully'),
                    'type': 'success'
                }
            }
            
        except Exception as e:
            self.model_status = 'draft'
            _logger.error(f"Model training failed: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Model training failed: %s') % str(e),
                    'type': 'danger'
                }
            }
    
    def deploy_model(self):
        """Deploy the trained model for predictions"""
        if self.model_status != 'trained':
            raise UserError(_('Model must be trained before deployment'))
        
        self.model_status = 'deployed'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Model deployed successfully'),
                'type': 'success'
            }
        }
    
    def _gather_training_data(self):
        """Gather training data based on model type"""
        if self.model_type == 'turnover_prediction':
            return self._gather_turnover_data()
        elif self.model_type == 'performance_forecast':
            return self._gather_performance_data()
        elif self.model_type == 'hiring_success':
            return self._gather_hiring_data()
        elif self.model_type == 'promotion_readiness':
            return self._gather_promotion_data()
        elif self.model_type == 'training_effectiveness':
            return self._gather_training_data_effectiveness()
        else:
            return {}
    
    def _gather_turnover_data(self):
        """Gather data for turnover prediction model"""
        # Get historical employee data
        employees = self.env['hr.employee'].search([])
        
        training_data = []
        for employee in employees:
            # Get employee features
            features = {
                'employee_id': employee.id,
                'department': employee.department_id.name if employee.department_id else '',
                'job_title': employee.job_title or '',
                'tenure_months': self._calculate_tenure_months(employee),
                'salary': self._get_employee_salary(employee),
                'performance_score': self._get_latest_performance_score(employee),
                'sentiment_score': self._get_latest_sentiment_score(employee),
                'training_hours': self._get_training_hours(employee),
                'promotion_count': self._get_promotion_count(employee),
                'manager_changes': self._get_manager_changes(employee),
                'left_company': employee.active == False,  # Target variable
            }
            training_data.append(features)
        
        return training_data
    
    def _gather_performance_data(self):
        """Gather data for performance forecasting model"""
        performance_records = self.env['hr.performance.analytics'].search([
            ('analysis_status', '=', 'completed')
        ])
        
        training_data = []
        for record in performance_records:
            features = {
                'employee_id': record.employee_id.id,
                'current_performance': record.overall_performance_score,
                'productivity': record.productivity_score,
                'collaboration': record.collaboration_score,
                'innovation': record.innovation_score,
                'leadership': record.leadership_score,
                'tenure': self._calculate_tenure_months(record.employee_id),
                'training_participation': self._get_training_participation(record.employee_id),
                'sentiment': self._get_latest_sentiment_score(record.employee_id),
                'future_performance': record.future_performance_prediction,  # Target
            }
            training_data.append(features)
        
        return training_data
    
    def _gather_hiring_data(self):
        """Gather data for hiring success prediction model"""
        recruitment_records = self.env['hr.recruitment.ai'].search([
            ('analysis_status', '=', 'completed')
        ])
        
        training_data = []
        for record in recruitment_records:
            # Check if candidate was hired and their subsequent performance
            hired = self._was_candidate_hired(record.applicant_id)
            success_score = self._get_hire_success_score(record.applicant_id) if hired else 0
            
            features = {
                'applicant_id': record.applicant_id.id,
                'overall_score': record.overall_score,
                'skills_match': record.skills_match_score,
                'experience_relevance': record.experience_relevance,
                'cultural_fit': record.cultural_fit_score,
                'communication': record.communication_score,
                'technical_competency': record.technical_competency,
                'was_hired': hired,
                'hire_success': success_score,  # Target variable
            }
            training_data.append(features)
        
        return training_data
    
    def _calculate_tenure_months(self, employee):
        """Calculate employee tenure in months"""
        if employee.create_date:
            delta = datetime.now() - employee.create_date
            return delta.days / 30.44  # Average days per month
        return 0
    
    def _get_employee_salary(self, employee):
        """Get employee salary (placeholder)"""
        # This would integrate with payroll modules
        return 50000  # Placeholder
    
    def _get_latest_performance_score(self, employee):
        """Get latest performance score for employee"""
        performance = self.env['hr.performance.analytics'].search([
            ('employee_id', '=', employee.id),
            ('analysis_status', '=', 'completed')
        ], limit=1, order='last_updated desc')
        
        return performance.overall_performance_score if performance else 0
    
    def _get_latest_sentiment_score(self, employee):
        """Get latest sentiment score for employee"""
        sentiment = self.env['hr.sentiment.analysis'].search([
            ('employee_id', '=', employee.id),
            ('analysis_status', '=', 'completed')
        ], limit=1, order='analysis_date desc')
        
        return sentiment.overall_sentiment_score if sentiment else 0
    
    def _get_training_hours(self, employee):
        """Get total training hours for employee"""
        # This would integrate with training modules
        return 40  # Placeholder
    
    def _get_promotion_count(self, employee):
        """Get number of promotions for employee"""
        # This would track job title/position changes
        return 1  # Placeholder
    
    def _get_manager_changes(self, employee):
        """Get number of manager changes for employee"""
        # This would track parent_id changes
        return 0  # Placeholder
    
    def _get_training_participation(self, employee):
        """Get training participation rate"""
        return 0.8  # Placeholder
    
    def _was_candidate_hired(self, applicant):
        """Check if candidate was hired"""
        # Check if there's an employee record for this applicant
        employee = self.env['hr.employee'].search([
            ('name', '=', applicant.partner_name)
        ], limit=1)
        return bool(employee)
    
    def _get_hire_success_score(self, applicant):
        """Get success score for hired candidate"""
        employee = self.env['hr.employee'].search([
            ('name', '=', applicant.partner_name)
        ], limit=1)
        
        if employee:
            return self._get_latest_performance_score(employee)
        return 0


class HRPredictivePrediction(models.Model):
    _name = 'hr.predictive.prediction'
    _description = 'HR Predictive Model Predictions'
    _rec_name = 'prediction_id'
    _order = 'prediction_date desc'
    
    prediction_id = fields.Char('Prediction ID', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('hr.predictive.prediction'))
    model_id = fields.Many2one('hr.predictive.models', 'Predictive Model', required=True, ondelete='cascade')
    
    # Prediction Target
    employee_id = fields.Many2one('hr.employee', 'Employee')
    applicant_id = fields.Many2one('hr.applicant', 'Applicant')
    department_id = fields.Many2one('hr.department', 'Department')
    
    # Prediction Results
    prediction_value = fields.Float('Predicted Value')
    confidence_score = fields.Float('Confidence Score')
    prediction_category = fields.Selection([
        ('low_risk', 'Low Risk'),
        ('medium_risk', 'Medium Risk'),
        ('high_risk', 'High Risk'),
        ('very_high_risk', 'Very High Risk'),
    ], 'Risk Category')
    
    # Prediction Details
    input_features = fields.Text('Input Features Used')
    prediction_explanation = fields.Text('Prediction Explanation')
    contributing_factors = fields.Text('Contributing Factors')
    
    # Metadata
    prediction_date = fields.Datetime('Prediction Date', default=fields.Datetime.now)
    prediction_horizon = fields.Selection([
        ('1_month', '1 Month'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
    ], 'Prediction Horizon')
    
    # Validation
    actual_outcome = fields.Float('Actual Outcome')
    outcome_date = fields.Date('Outcome Date')
    prediction_accuracy = fields.Float('Prediction Accuracy', compute='_compute_accuracy')
    
    @api.depends('prediction_value', 'actual_outcome')
    def _compute_accuracy(self):
        for record in self:
            if record.actual_outcome and record.prediction_value:
                error = abs(record.prediction_value - record.actual_outcome)
                max_value = max(abs(record.prediction_value), abs(record.actual_outcome))
                if max_value > 0:
                    record.prediction_accuracy = 1 - (error / max_value)
                else:
                    record.prediction_accuracy = 1.0
            else:
                record.prediction_accuracy = 0.0
    
    def generate_prediction_report(self):
        """Generate detailed prediction report"""
        return {
            'prediction_id': self.prediction_id,
            'model_type': self.model_id.model_type,
            'target': self.employee_id.name if self.employee_id else self.applicant_id.partner_name,
            'prediction_value': self.prediction_value,
            'confidence': self.confidence_score,
            'risk_category': self.prediction_category,
            'horizon': self.prediction_horizon,
            'explanation': self.prediction_explanation,
            'contributing_factors': self.contributing_factors,
            'date': self.prediction_date.strftime('%Y-%m-%d %H:%M'),
        } 