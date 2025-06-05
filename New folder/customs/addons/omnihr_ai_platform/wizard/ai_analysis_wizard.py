from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AIAnalysisWizard(models.TransientModel):
    _name = 'hr.ai.analysis.wizard'
    _description = 'AI Analysis Wizard'
    
    analysis_type = fields.Selection([
        ('employee_intelligence', 'Employee Intelligence'),
        ('performance_analytics', 'Performance Analytics'),
        ('sentiment_analysis', 'Sentiment Analysis'),
        ('recruitment_screening', 'Recruitment Screening'),
    ], 'Analysis Type', required=True)
    
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    applicant_ids = fields.Many2many('hr.applicant', string='Applicants')
    department_ids = fields.Many2many('hr.department', string='Departments')
    
    def run_analysis(self):
        """Run the selected AI analysis"""
        if self.analysis_type == 'employee_intelligence':
            return self._run_employee_intelligence()
        elif self.analysis_type == 'performance_analytics':
            return self._run_performance_analytics()
        elif self.analysis_type == 'sentiment_analysis':
            return self._run_sentiment_analysis()
        elif self.analysis_type == 'recruitment_screening':
            return self._run_recruitment_screening()
    
    def _run_employee_intelligence(self):
        """Run employee intelligence analysis"""
        for employee in self.employee_ids:
            intelligence = self.env['hr.employee.intelligence'].search([
                ('employee_id', '=', employee.id)
            ], limit=1)
            
            if not intelligence:
                intelligence = self.env['hr.employee.intelligence'].create({
                    'employee_id': employee.id
                })
            
            intelligence.run_comprehensive_analysis()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Employee intelligence analysis started'),
                'type': 'success'
            }
        }
    
    def _run_performance_analytics(self):
        """Run performance analytics"""
        for employee in self.employee_ids:
            analytics = self.env['hr.performance.analytics'].search([
                ('employee_id', '=', employee.id)
            ], limit=1)
            
            if not analytics:
                analytics = self.env['hr.performance.analytics'].create({
                    'employee_id': employee.id
                })
            
            analytics.run_performance_analysis()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Performance analytics started'),
                'type': 'success'
            }
        }
    
    def _run_sentiment_analysis(self):
        """Run sentiment analysis"""
        for employee in self.employee_ids:
            sentiment = self.env['hr.sentiment.analysis'].create({
                'employee_id': employee.id
            })
            sentiment.run_sentiment_analysis()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Sentiment analysis started'),
                'type': 'success'
            }
        }
    
    def _run_recruitment_screening(self):
        """Run recruitment screening"""
        for applicant in self.applicant_ids:
            screening = self.env['hr.recruitment.ai'].search([
                ('applicant_id', '=', applicant.id)
            ], limit=1)
            
            if not screening:
                screening = self.env['hr.recruitment.ai'].create({
                    'applicant_id': applicant.id
                })
            
            screening.run_comprehensive_assessment()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Recruitment screening started'),
                'type': 'success'
            }
        } 