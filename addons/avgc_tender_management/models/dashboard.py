from odoo import models, fields, api, _
from datetime import datetime, timedelta
import json

class Dashboard(models.TransientModel):
    _name = 'avgc.dashboard'
    _description = 'Tender Dashboard'

    # KPI Fields
    active_tender_count = fields.Integer('Active Tenders', compute='_compute_kpis')
    active_tender_value = fields.Monetary('Active Tender Value', 
                                        currency_field='currency_id',
                                        compute='_compute_kpis')
    active_gem_bid_count = fields.Integer('Active GeM Bids', compute='_compute_kpis')
    active_gem_bid_value = fields.Monetary('Active GeM Bid Value',
                                         currency_field='currency_id',
                                         compute='_compute_kpis')
    win_rate = fields.Float('Win Rate', compute='_compute_kpis')
    pending_task_count = fields.Integer('Pending Tasks', compute='_compute_kpis')
    due_this_week = fields.Integer('Due This Week', compute='_compute_kpis')
    
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    
    # Chart Data
    tender_status_chart = fields.Text('Tender Status Chart', compute='_compute_charts')
    category_analysis_chart = fields.Text('Category Analysis Chart', compute='_compute_charts')
    financial_metrics_chart = fields.Text('Financial Metrics Chart', compute='_compute_charts')
    vendor_performance_chart = fields.Text('Vendor Performance Chart', compute='_compute_charts')
    ai_analysis_chart = fields.Text('AI Analysis Chart', compute='_compute_charts')
    
    # Related Data
    recent_activity_ids = fields.Many2many('avgc.activity.log', 
                                         compute='_compute_related_data')
    upcoming_deadline_ids = fields.Many2many('avgc.tender',
                                           compute='_compute_related_data')
    high_priority_task_ids = fields.Many2many('avgc.task',
                                            compute='_compute_related_data')

    @api.depends()
    def _compute_kpis(self):
        for record in self:
            # Active Tenders
            active_tenders = self.env['avgc.tender'].search([
                ('status', 'in', ['published', 'in_progress', 'evaluation'])
            ])
            record.active_tender_count = len(active_tenders)
            record.active_tender_value = sum(active_tenders.mapped('estimated_value'))
            
            # Active GeM Bids
            active_gem_bids = self.env['avgc.gem.bid'].search([
                ('status', 'in', ['draft', 'submitted', 'under_review'])
            ])
            record.active_gem_bid_count = len(active_gem_bids)
            record.active_gem_bid_value = sum(active_gem_bids.mapped('bid_amount'))
            
            # Win Rate (last 3 months)
            three_months_ago = datetime.now() - timedelta(days=90)
            recent_submissions = self.env['avgc.tender.submission'].search([
                ('submission_date', '>=', three_months_ago)
            ])
            awarded_submissions = recent_submissions.filtered(lambda s: s.status == 'awarded')
            record.win_rate = (len(awarded_submissions) / len(recent_submissions) * 100
                             if recent_submissions else 0)
            
            # Pending Tasks
            pending_tasks = self.env['avgc.task'].search([
                ('status', 'in', ['pending', 'in_progress'])
            ])
            record.pending_task_count = len(pending_tasks)
            
            # Due This Week
            week_end = datetime.now() + timedelta(days=7)
            due_this_week = pending_tasks.filtered(
                lambda t: t.deadline and t.deadline <= week_end.date()
            )
            record.due_this_week = len(due_this_week)

    @api.depends()
    def _compute_charts(self):
        for record in self:
            # Tender Status Chart
            tender_statuses = self.env['avgc.tender'].read_group(
                [], ['status'], ['status']
            )
            record.tender_status_chart = json.dumps({
                'type': 'pie',
                'data': {
                    'labels': [item['status'] for item in tender_statuses],
                    'datasets': [{
                        'data': [item['status_count'] for item in tender_statuses],
                        'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
                    }]
                }
            })
            
            # Category Analysis Chart
            category_data = self.env['avgc.tender'].read_group(
                [], ['category'], ['category']
            )
            record.category_analysis_chart = json.dumps({
                'type': 'bar',
                'data': {
                    'labels': [item['category'] for item in category_data],
                    'datasets': [{
                        'label': 'Tender Count',
                        'data': [item['category_count'] for item in category_data],
                        'backgroundColor': '#36A2EB'
                    }]
                }
            })
            
            # Financial Metrics Chart
            record.financial_metrics_chart = json.dumps({
                'type': 'line',
                'data': {
                    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'datasets': [{
                        'label': 'Tender Value',
                        'data': [100000, 150000, 120000, 180000, 200000, 250000],
                        'borderColor': '#FF6384'
                    }]
                }
            })
            
            # Vendor Performance Chart
            record.vendor_performance_chart = json.dumps({
                'type': 'radar',
                'data': {
                    'labels': ['Quality', 'Delivery', 'Price', 'Service', 'Innovation'],
                    'datasets': [{
                        'label': 'Average Score',
                        'data': [85, 90, 75, 88, 70],
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'borderColor': '#36A2EB'
                    }]
                }
            })
            
            # AI Analysis Chart
            record.ai_analysis_chart = json.dumps({
                'type': 'doughnut',
                'data': {
                    'labels': ['Completed', 'In Progress', 'Failed'],
                    'datasets': [{
                        'data': [75, 20, 5],
                        'backgroundColor': ['#4BC0C0', '#FFCE56', '#FF6384']
                    }]
                }
            })

    @api.depends()
    def _compute_related_data(self):
        for record in self:
            # Recent Activity (if activity log model exists)
            try:
                recent_activities = self.env['avgc.activity.log'].search(
                    [], order='date desc', limit=10
                )
                record.recent_activity_ids = recent_activities
            except:
                record.recent_activity_ids = False
            
            # Upcoming Deadlines
            upcoming_deadlines = self.env['avgc.tender'].search([
                ('submission_deadline', '>=', fields.Date.today()),
                ('submission_deadline', '<=', fields.Date.today() + timedelta(days=30))
            ], order='submission_deadline', limit=10)
            record.upcoming_deadline_ids = upcoming_deadlines
            
            # High Priority Tasks
            high_priority_tasks = self.env['avgc.task'].search([
                ('priority', '=', 'high'),
                ('status', 'in', ['pending', 'in_progress'])
            ], limit=10)
            record.high_priority_task_ids = high_priority_tasks


class Analytics(models.TransientModel):
    _name = 'avgc.analytics'
    _description = 'Analytics'

    # Tender Analytics
    total_tender_count = fields.Integer('Total Tenders', compute='_compute_tender_analytics')
    total_tender_value = fields.Monetary('Total Tender Value',
                                       currency_field='currency_id',
                                       compute='_compute_tender_analytics')
    average_tender_value = fields.Monetary('Average Tender Value',
                                         currency_field='currency_id',
                                         compute='_compute_tender_analytics')
    success_rate = fields.Float('Success Rate', compute='_compute_tender_analytics')
    tender_growth_rate = fields.Float('Growth Rate', compute='_compute_tender_analytics')
    average_processing_time = fields.Float('Avg Processing Time (days)',
                                         compute='_compute_tender_analytics')
    compliance_score = fields.Float('Compliance Score', compute='_compute_tender_analytics')
    risk_score = fields.Float('Risk Score', compute='_compute_tender_analytics')
    
    # GeM Analytics
    total_gem_bid_count = fields.Integer('Total GeM Bids', compute='_compute_gem_analytics')
    total_gem_bid_value = fields.Monetary('Total GeM Bid Value',
                                        currency_field='currency_id',
                                        compute='_compute_gem_analytics')
    average_gem_bid_value = fields.Monetary('Average GeM Bid Value',
                                          currency_field='currency_id',
                                          compute='_compute_gem_analytics')
    gem_success_rate = fields.Float('GeM Success Rate', compute='_compute_gem_analytics')
    gem_growth_rate = fields.Float('GeM Growth Rate', compute='_compute_gem_analytics')
    average_gem_processing_time = fields.Float('Avg GeM Processing Time',
                                             compute='_compute_gem_analytics')
    gem_compliance_score = fields.Float('GeM Compliance Score',
                                      compute='_compute_gem_analytics')
    gem_risk_score = fields.Float('GeM Risk Score', compute='_compute_gem_analytics')
    
    # AI Analytics
    total_ai_analysis_count = fields.Integer('Total AI Analysis',
                                           compute='_compute_ai_analytics')
    successful_analysis_count = fields.Integer('Successful Analysis',
                                             compute='_compute_ai_analytics')
    average_confidence_score = fields.Float('Avg Confidence Score',
                                          compute='_compute_ai_analytics')
    ai_processing_time = fields.Float('AI Processing Time',
                                    compute='_compute_ai_analytics')
    ai_success_rate = fields.Float('AI Success Rate', compute='_compute_ai_analytics')
    ai_cost_savings = fields.Monetary('AI Cost Savings',
                                    currency_field='currency_id',
                                    compute='_compute_ai_analytics')
    ai_efficiency_gain = fields.Float('AI Efficiency Gain',
                                    compute='_compute_ai_analytics')
    ai_error_rate = fields.Float('AI Error Rate', compute='_compute_ai_analytics')
    
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    
    # Chart Data
    tender_trend_chart = fields.Text('Tender Trend Chart', compute='_compute_charts')
    gem_trend_chart = fields.Text('GeM Trend Chart', compute='_compute_charts')
    ai_performance_chart = fields.Text('AI Performance Chart', compute='_compute_charts')

    @api.depends()
    def _compute_tender_analytics(self):
        for record in self:
            tenders = self.env['avgc.tender'].search([])
            record.total_tender_count = len(tenders)
            record.total_tender_value = sum(tenders.mapped('estimated_value'))
            record.average_tender_value = (record.total_tender_value / 
                                         record.total_tender_count 
                                         if record.total_tender_count else 0)
            
            awarded_tenders = tenders.filtered(lambda t: t.status == 'awarded')
            record.success_rate = (len(awarded_tenders) / len(tenders) * 100
                                 if tenders else 0)
            
            # Mock data for other fields
            record.tender_growth_rate = 15.5
            record.average_processing_time = 45.2
            record.compliance_score = 92.5
            record.risk_score = 12.3

    @api.depends()
    def _compute_gem_analytics(self):
        for record in self:
            gem_bids = self.env['avgc.gem.bid'].search([])
            record.total_gem_bid_count = len(gem_bids)
            record.total_gem_bid_value = sum(gem_bids.mapped('bid_amount'))
            record.average_gem_bid_value = (record.total_gem_bid_value /
                                          record.total_gem_bid_count
                                          if record.total_gem_bid_count else 0)
            
            # Mock data for other fields
            record.gem_success_rate = 68.5
            record.gem_growth_rate = 22.1
            record.average_gem_processing_time = 28.5
            record.gem_compliance_score = 89.2
            record.gem_risk_score = 8.7

    @api.depends()
    def _compute_ai_analytics(self):
        for record in self:
            try:
                ai_analyses = self.env['avgc.ai.analysis'].search([])
                record.total_ai_analysis_count = len(ai_analyses)
                successful = ai_analyses.filtered(lambda a: a.status == 'completed')
                record.successful_analysis_count = len(successful)
                record.ai_success_rate = (len(successful) / len(ai_analyses) * 100
                                        if ai_analyses else 0)
            except:
                record.total_ai_analysis_count = 0
                record.successful_analysis_count = 0
                record.ai_success_rate = 0
            
            # Mock data for other fields
            record.average_confidence_score = 87.3
            record.ai_processing_time = 2.5
            record.ai_cost_savings = 125000
            record.ai_efficiency_gain = 35.2
            record.ai_error_rate = 3.1

    @api.depends()
    def _compute_charts(self):
        for record in self:
            # Mock chart data
            record.tender_trend_chart = json.dumps({
                'type': 'line',
                'data': {
                    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'datasets': [{
                        'label': 'Tender Count',
                        'data': [12, 19, 15, 25, 22, 30],
                        'borderColor': '#36A2EB'
                    }]
                }
            })
            
            record.gem_trend_chart = json.dumps({
                'type': 'line',
                'data': {
                    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'datasets': [{
                        'label': 'GeM Bid Count',
                        'data': [8, 12, 10, 18, 15, 22],
                        'borderColor': '#FF6384'
                    }]
                }
            })
            
            record.ai_performance_chart = json.dumps({
                'type': 'bar',
                'data': {
                    'labels': ['Accuracy', 'Speed', 'Cost Savings', 'Efficiency'],
                    'datasets': [{
                        'label': 'Performance %',
                        'data': [87, 95, 78, 92],
                        'backgroundColor': '#4BC0C0'
                    }]
                }
            })
