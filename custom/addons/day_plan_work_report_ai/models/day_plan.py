import logging
import json
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class DayPlanRecentActivity(models.Model):
    _name = "day.plan.recent.activity"
    _description = "Recent Activities for Dashboard"
    _transient = True  # Make it transient as it's only for display purposes
    
    day_plan_id = fields.Many2one('day.plan', string="Day Plan")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_name = fields.Char(string="Employee Name", related="employee_id.name", store=False)
    title = fields.Char(string="Title")
    description = fields.Text(string="Description")
    time = fields.Char(string="Time")
    activity_date = fields.Datetime(string="Activity Date")


class DayPlanTeamPerformance(models.Model):
    _name = "day.plan.team.performance"
    _description = "Team Performance for Dashboard"
    _transient = True  # Make it transient as it's only for display purposes
    
    day_plan_id = fields.Many2one('day.plan', string="Day Plan")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    completed_tasks = fields.Integer(string="Completed Tasks")
    completion_rate = fields.Float(string="Completion Rate")
    productivity_score = fields.Float(string="Productivity Score")


class DayPlan(models.Model):
    _name = "day.plan"
    _description = "Daily Work Plan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # Basic Information
    name = fields.Char(string="Plan Title", required=True, tracking=True, default="New")
    sequence = fields.Char(string="Reference", readonly=True, copy=False, index=True)
    date = fields.Date(string="Plan Date", required=True, default=fields.Date.context_today, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, 
                                 default=lambda self: self.env.user.employee_id, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                default=lambda self: self.env.company, tracking=True)
    
    # Time Management
    planned_start = fields.Datetime(string="Planned Start Time", tracking=True)
    planned_end = fields.Datetime(string="Planned End Time", tracking=True)
    actual_start = fields.Datetime(string="Actual Start Time", tracking=True)
    actual_end = fields.Datetime(string="Actual End Time", tracking=True)
    estimated_hours = fields.Float(string="Estimated Hours", tracking=True, 
                                 help="Total estimated hours for all tasks")
    actual_hours = fields.Float(string="Actual Hours", compute='_compute_actual_hours', 
                              store=True, help="Total actual hours spent on all tasks")
    
    # Goals and Focus Areas
    main_goals = fields.Text(string="Main Goals", tracking=True, 
                           help="Primary objectives for the day")
    key_results = fields.Text(string="Key Results", tracking=True,
                            help="Measurable outcomes to achieve")
    focus_areas = fields.Text(string="Focus Areas", tracking=True,
                            help="Specific areas to concentrate on")
    potential_blockers = fields.Text(string="Potential Blockers", tracking=True,
                                   help="Anticipated challenges or obstacles")
    
    # Progress Tracking
    progress = fields.Float(string="Completion %", compute='_compute_progress', 
                          store=True, tracking=True, group_operator="avg")
    tasks_completed = fields.Integer(compute='_compute_task_stats', string="Tasks Completed")
    total_tasks = fields.Integer(compute='_compute_task_stats', string="Total Tasks")
    completion_ratio = fields.Char(compute='_compute_task_stats', string="Completion Ratio")
    
    # Task Management
    task_ids = fields.One2many('day.plan.task', 'day_plan_id', string="Tasks")
    
    # Task Statistics
    todo_task_count = fields.Integer(compute='_compute_task_stats', string="To Do")
    in_progress_task_count = fields.Integer(compute='_compute_task_stats', string="In Progress")
    done_task_count = fields.Integer(compute='_compute_task_stats', string="Done")
    cancelled_task_count = fields.Integer(compute='_compute_task_stats', string="Cancelled")
    high_priority_count = fields.Integer(compute='_compute_task_stats', string="High Priority")
    
    # AI Integration
    ai_analysis_ids = fields.One2many('ai.analysis', 'day_plan_id', string="AI Analysis")
    productivity_score = fields.Float(compute='_compute_ai_metrics', string="Productivity Score",
                                    store=True, group_operator="avg")
    efficiency_rating = fields.Float(compute='_compute_ai_metrics', string="Efficiency Rating",
                                   store=True, group_operator="avg")
    wellbeing_assessment = fields.Float(compute='_compute_ai_metrics', string="Wellbeing Score",
                                      store=True, group_operator="avg")
    
    # Dashboard Fields
    plans_today = fields.Integer(compute='_compute_dashboard_stats', string="Plans Today")
    total_plans = fields.Integer(compute='_compute_dashboard_stats', string="Total Plans")
    completed_plans = fields.Integer(compute='_compute_dashboard_stats', string="Completed Plans")
    in_progress_plans = fields.Integer(compute='_compute_dashboard_stats', string="In Progress Plans")
    pending_tasks = fields.Integer(compute='_compute_dashboard_stats', string="Pending Tasks")
    plans_change = fields.Float(compute='_compute_dashboard_stats', string="Plans Change %")
    tasks_change = fields.Float(compute='_compute_dashboard_stats', string="Tasks Change %")
    completion_rate = fields.Float(compute='_compute_dashboard_stats', string="Completion Rate")
    avg_productivity = fields.Float(compute='_compute_dashboard_stats', string="Avg Productivity")
    tasks_due_today = fields.Integer(compute='_compute_dashboard_stats', string="Tasks Due Today")
    overdue_tasks = fields.Integer(compute='_compute_dashboard_stats', string="Overdue Tasks")
    attention_items = fields.Integer(compute='_compute_dashboard_stats', string="Attention Items")
    
    # Chart data fields
    productivity_chart = fields.Text(compute='_compute_dashboard_stats', string="Productivity Chart Data")
    task_distribution_chart = fields.Text(compute='_compute_dashboard_stats', string="Task Distribution Chart")
    performance_chart = fields.Text(compute='_compute_dashboard_stats', string="Performance Chart")
    task_priority_chart = fields.Text(compute='_compute_dashboard_stats', string="Task Priority Chart")
    team_performance = fields.One2many('day.plan.team.performance', 'day_plan_id', string="Team Performance", compute='_compute_dashboard_stats', store=False)
    recent_activities = fields.One2many('day.plan.recent.activity', 'day_plan_id', string="Recent Activities", compute='_compute_dashboard_stats', store=False)
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', tracking=True)
    
    # Computed Methods
    @api.depends('task_ids.actual_hours')
    def _compute_actual_hours(self):
        for plan in self:
            plan.actual_hours = sum(task.actual_hours for task in plan.task_ids)
    
    @api.depends('task_ids', 'task_ids.progress')
    def _compute_progress(self):
        for plan in self:
            if plan.task_ids:
                total = len(plan.task_ids)
                completed = sum(1 for task in plan.task_ids if task.status == 'done')
                plan.progress = (completed / total) * 100 if total > 0 else 0
            else:
                plan.progress = 0
    
    @api.depends('task_ids', 'task_ids.status')
    def _compute_task_stats(self):
        for plan in self:
            plan.total_tasks = len(plan.task_ids)
            plan.tasks_completed = len(plan.task_ids.filtered(lambda t: t.status == 'done'))
            plan.completion_ratio = f"{plan.tasks_completed}/{plan.total_tasks}"
            plan.todo_task_count = len(plan.task_ids.filtered(lambda t: t.status == 'todo'))
            plan.in_progress_task_count = len(plan.task_ids.filtered(lambda t: t.status == 'in_progress'))
            plan.done_task_count = len(plan.task_ids.filtered(lambda t: t.status == 'done'))
            plan.cancelled_task_count = len(plan.task_ids.filtered(lambda t: t.status == 'cancelled'))
            plan.high_priority_count = len(plan.task_ids.filtered(lambda t: t.priority in ['2', '3']))
    
    @api.depends('ai_analysis_ids')
    def _compute_ai_metrics(self):
        for plan in self:
            if plan.ai_analysis_ids:
                latest_analysis = plan.ai_analysis_ids[0]  # Get the most recent analysis
                plan.productivity_score = latest_analysis.productivity_score
                plan.efficiency_rating = latest_analysis.efficiency_rating
                plan.wellbeing_assessment = latest_analysis.wellbeing_assessment
            else:
                plan.productivity_score = 0
                plan.efficiency_rating = 0
                plan.wellbeing_assessment = 0
    
    @api.depends('date', 'state', 'task_ids.status')
    def _compute_dashboard_stats(self):
        """Compute dashboard statistics for the current user"""
        today = fields.Date.today()
        last_month = today - timedelta(days=30)
        
        # Get user plans for current and previous periods
        user_plans = self.search([('employee_id', '=', self.env.user.employee_id.id)])
        current_month_plans = user_plans.filtered(lambda p: p.date >= last_month)
        previous_month_plans = user_plans.filtered(lambda p: p.date < last_month and p.date >= (last_month - timedelta(days=30)))
        
        # Get all tasks for the user
        tasks = self.env['day.plan.task'].search([
            ('day_plan_id.employee_id', '=', self.env.user.employee_id.id)
        ])
        current_month_tasks = tasks.filtered(lambda t: t.day_plan_id.date >= last_month)
        previous_month_tasks = tasks.filtered(lambda t: t.day_plan_id.date < last_month and t.day_plan_id.date >= (last_month - timedelta(days=30)))
        
        # Get AI analysis records for productivity calculation
        ai_analyses = self.env['ai.analysis'].search([
            ('day_plan_id.employee_id', '=', self.env.user.employee_id.id),
            ('create_date', '>=', fields.Datetime.to_string(last_month))
        ])
        
        # Compute stats for all records in self
        for plan in self:
            # Basic plan stats
            plan.total_plans = len(user_plans)
            plan.plans_today = len(user_plans.filtered(lambda p: p.date == today))
            plan.completed_plans = len(user_plans.filtered(lambda p: p.state == 'completed' and p.date.month == today.month))
            plan.in_progress_plans = len(user_plans.filtered(lambda p: p.state == 'in_progress'))
            
            # Task stats
            plan.pending_tasks = len(tasks.filtered(lambda t: t.status in ['todo', 'in_progress']))
            
            # Calculate change percentages
            current_plan_count = len(current_month_plans)
            previous_plan_count = len(previous_month_plans)
            plan.plans_change = ((current_plan_count - previous_plan_count) / max(previous_plan_count, 1)) * 100 if previous_plan_count else 0
            
            current_task_count = len(current_month_tasks)
            previous_task_count = len(previous_month_tasks)
            plan.tasks_change = ((current_task_count - previous_task_count) / max(previous_task_count, 1)) * 100 if previous_task_count else 0
            
            # Calculate completion rate
            completed_tasks = tasks.filtered(lambda t: t.status == 'done')
            total_task_count = len(tasks)
            plan.completion_rate = (len(completed_tasks) / total_task_count * 100) if total_task_count else 0
            
            # Calculate average productivity from AI analyses
            if ai_analyses:
                plan.avg_productivity = sum(ai_analyses.mapped('productivity_score')) / len(ai_analyses)
            else:
                plan.avg_productivity = plan.productivity_score if plan.productivity_score else 0
            
            # Calculate attention items (tasks that need attention)
            plan.attention_items = plan.overdue_tasks + len(tasks.filtered(lambda t: t.status == 'blocked'))
            
            # Only check deadline if the field exists
            if 'deadline' in self.env['day.plan.task']._fields:
                plan.overdue_tasks = len(tasks.filtered(
                    lambda t: t.deadline and 
                             t.deadline.date() < today and 
                             t.status != 'done'
                ))
                plan.tasks_due_today = len(tasks.filtered(
                    lambda t: t.deadline and 
                             t.deadline.date() == today and 
                             t.status != 'done'
                ))
                
                # Update attention_items to include high priority tasks due today
                high_priority_due_today = len(tasks.filtered(
                    lambda t: t.deadline and
                             t.deadline.date() == today and
                             t.status != 'done' and
                             t.priority == 'high'
                ))
                plan.attention_items += high_priority_due_today
            else:
                plan.overdue_tasks = 0
                plan.tasks_due_today = 0
                
            # Generate chart data
            
            # 1. Productivity chart - shows productivity score over time
            date_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            productivity_data = []
            
            # Get productivity data from AI analyses
            for i in range(7):
                day_date = today - timedelta(days=today.weekday()) + timedelta(days=i)  # Start from Monday of current week
                analyses = self.env['ai.analysis'].search([
                    ('day_plan_id.date', '=', day_date),
                    ('day_plan_id.employee_id', '=', self.env.user.employee_id.id)
                ])
                
                if analyses:
                    avg_score = sum(analyses.mapped('productivity_score')) / len(analyses)
                    productivity_data.append(round(avg_score, 2))
                else:
                    productivity_data.append(0)
            
            # Create productivity chart data
            plan.productivity_chart = json.dumps({
                'labels': date_labels,
                'datasets': [{
                    'label': 'Productivity Score',
                    'data': productivity_data,
                    'fill': False,
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'tension': 0.1
                }]
            })
            
            # 2. Task distribution chart - pie chart showing task status distribution
            task_status_data = self.env['day.plan.task'].read_group(
                [
                    ('day_plan_id.employee_id', '=', self.env.user.employee_id.id),
                    ('day_plan_id.date', '>=', today - timedelta(days=30)),
                    ('status', '!=', False)
                ],
                ['status'], 
                ['status']
            )
            
            status_labels = []
            status_data = []
            status_colors = [
                'rgba(255, 99, 132, 0.8)',  # Red
                'rgba(54, 162, 235, 0.8)',   # Blue
                'rgba(255, 206, 86, 0.8)',   # Yellow
                'rgba(75, 192, 192, 0.8)',   # Green
                'rgba(153, 102, 255, 0.8)'   # Purple
            ]
            
            if task_status_data:
                for idx, group in enumerate(task_status_data):
                    status_labels.append(group['status'])
                    status_data.append(group['status_count'])
            else:
                status_labels = ['No Data']
                status_data = [100]
                
            plan.task_distribution_chart = json.dumps({
                'labels': status_labels,
                'datasets': [{
                    'data': status_data,
                    'backgroundColor': status_colors[:len(status_data)]
                }]
            })
            
            # 3. Performance chart - radar chart with various metrics
            # Calculate metrics based on plans and tasks
            planning_score = min(5, plan.total_plans / 10) if plan.total_plans else 0
            execution_score = min(5, len(completed_tasks) / max(total_task_count, 1) * 5) if total_task_count else 0
            timeliness_score = 0
            if 'deadline' in self.env['day.plan.task']._fields and total_task_count:
                on_time_tasks = len(tasks.filtered(lambda t: t.status == 'done' and t.deadline and t.write_date <= t.deadline))
                timeliness_score = min(5, on_time_tasks / max(len(completed_tasks), 1) * 5) if completed_tasks else 0
            
            plan.performance_chart = json.dumps({
                'labels': ['Planning', 'Execution', 'Productivity', 'Timeliness', 'Completion'],
                'datasets': [{
                    'label': 'Performance',
                    'data': [
                        round(planning_score, 1),
                        round(execution_score, 1),
                        round(min(5, plan.avg_productivity / 20), 1),  # Scale 0-100 to 0-5
                        round(timeliness_score, 1),
                        round(min(5, plan.completion_rate / 20), 1)   # Scale 0-100 to 0-5
                    ],
                    'fill': True,
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'pointBackgroundColor': 'rgba(54, 162, 235, 1)',
                    'pointBorderColor': '#fff',
                    'pointHoverBackgroundColor': '#fff',
                    'pointHoverBorderColor': 'rgba(54, 162, 235, 1)'
                }]
            })
            
            # 4. Task priority chart - pie chart showing task priority distribution
            priority_field_exists = 'priority' in self.env['day.plan.task']._fields
            
            if priority_field_exists:
                task_priority_data = self.env['day.plan.task'].read_group(
                    [
                        ('day_plan_id.employee_id', '=', self.env.user.employee_id.id),
                        ('day_plan_id.date', '>=', today - timedelta(days=30)),
                        ('priority', '!=', False)
                    ],
                    ['priority'], 
                    ['priority']
                )
                
                priority_labels = []
                priority_data = []
                priority_colors = {
                    'high': '#e74a3b',     # Red
                    'medium': '#f6c23e',   # Yellow
                    'low': '#1cc88a'       # Green
                }
                colors_list = []
                
                if task_priority_data:
                    for group in task_priority_data:
                        priority = group.get('priority', 'low')
                        priority_labels.append(priority)
                        priority_data.append(group['priority_count'])
                        colors_list.append(priority_colors.get(priority, '#858796'))
                else:
                    priority_labels = ['No Data']
                    priority_data = [100]
                    colors_list = ['#858796']
                    
                plan.task_priority_chart = json.dumps({
                    'labels': priority_labels,
                    'datasets': [{
                        'data': priority_data,
                        'backgroundColor': colors_list
                    }]
                })
            else:
                # If priority field doesn't exist, create empty chart
                plan.task_priority_chart = json.dumps({
                    'labels': ['No Priority Data'],
                    'datasets': [{
                        'data': [100],
                        'backgroundColor': ['#858796']
                    }]
                })
                
            # 5. Team Performance - generate performance data for team members
            # First, find all employees in the team (same department as current user)
            current_employee = self.env.user.employee_id
            if current_employee and current_employee.department_id:
                team_employees = self.env['hr.employee'].search([
                    ('department_id', '=', current_employee.department_id.id)
                ])
            else:
                # If no department, just show all employees as a fallback
                team_employees = self.env['hr.employee'].search([], limit=10)
                
            # Clean up old team performance records for this plan
            self.env['day.plan.team.performance'].search([('day_plan_id', '=', plan.id)]).unlink()
            
            # Create performance records for each team member
            team_performances = []
            for employee in team_employees:
                # Get employee's plans from the last month
                employee_plans = self.search([
                    ('employee_id', '=', employee.id),
                    ('date', '>=', last_month)
                ])
                
                # Get employee's tasks from the last month
                employee_tasks = self.env['day.plan.task'].search([
                    ('day_plan_id.employee_id', '=', employee.id),
                    ('day_plan_id.date', '>=', last_month)
                ])
                
                # Calculate metrics
                completed_tasks = len(employee_tasks.filtered(lambda t: t.status == 'done'))
                task_completion_rate = (completed_tasks / len(employee_tasks) * 100) if employee_tasks else 0
                
                # Get average productivity score from AI analysis if available
                employee_ai_analyses = self.env['ai.analysis'].search([
                    ('day_plan_id.employee_id', '=', employee.id),
                    ('create_date', '>=', fields.Datetime.to_string(last_month))
                ])
                productivity_score = 0
                if employee_ai_analyses:
                    productivity_score = sum(employee_ai_analyses.mapped('productivity_score')) / len(employee_ai_analyses)
                
                # Create and add the performance record
                perf_record = self.env['day.plan.team.performance'].create({
                    'day_plan_id': plan.id,
                    'employee_id': employee.id,
                    'completed_tasks': completed_tasks,
                    'completion_rate': round(task_completion_rate, 2),
                    'productivity_score': round(productivity_score, 2),
                })
                team_performances.append(perf_record.id)
            
            # Assign the created records to the plan
            plan.team_performance = [(6, 0, team_performances)]
            
            # 6. Recent Activities - generate recent activity data
            # Clean up old activity records for this plan
            self.env['day.plan.recent.activity'].search([('day_plan_id', '=', plan.id)]).unlink()
            
            # Get recent activities data from various sources
            recent_activities = []
            
            # 1. Recently completed tasks
            recent_tasks = self.env['day.plan.task'].search([
                ('status', '=', 'done'),
                ('write_date', '>=', fields.Datetime.now() - timedelta(days=7)),
                ('day_plan_id.employee_id', '!=', False)  # Ensure employee is set
            ], order='write_date desc', limit=5)
            
            for task in recent_tasks:
                time_ago = self._get_time_ago(task.write_date)
                
                activity = self.env['day.plan.recent.activity'].create({
                    'day_plan_id': plan.id,
                    'employee_id': task.day_plan_id.employee_id.id,
                    'title': 'Task Completed',
                    'description': task.name,
                    'time': time_ago,
                    'activity_date': task.write_date,
                })
                recent_activities.append(activity.id)
            
            # 2. New plans created
            recent_plans = self.search([
                ('create_date', '>=', fields.Datetime.now() - timedelta(days=7)),
                ('employee_id', '!=', False)  # Ensure employee is set
            ], order='create_date desc', limit=3)
            
            for recent_plan in recent_plans:
                time_ago = self._get_time_ago(recent_plan.create_date)
                
                activity = self.env['day.plan.recent.activity'].create({
                    'day_plan_id': plan.id,
                    'employee_id': recent_plan.employee_id.id,
                    'title': 'New Plan Created',
                    'description': f'{recent_plan.name or "Plan"} for {recent_plan.date}',
                    'time': time_ago,
                    'activity_date': recent_plan.create_date,
                })
                recent_activities.append(activity.id)
                
            # 3. Recent AI analyses
            recent_analyses = self.env['ai.analysis'].search([
                ('create_date', '>=', fields.Datetime.now() - timedelta(days=7)),
                ('day_plan_id.employee_id', '!=', False)  # Ensure employee is set
            ], order='create_date desc', limit=3)
            
            for analysis in recent_analyses:
                time_ago = self._get_time_ago(analysis.create_date)
                
                activity = self.env['day.plan.recent.activity'].create({
                    'day_plan_id': plan.id,
                    'employee_id': analysis.day_plan_id.employee_id.id,
                    'title': 'AI Analysis Completed',
                    'description': f'Productivity Score: {analysis.productivity_score}',
                    'time': time_ago,
                    'activity_date': analysis.create_date,
                })
                recent_activities.append(activity.id)
                
            # Assign the activity records to the plan
            plan.recent_activities = [(6, 0, recent_activities)]
    
    # Helper Methods
    def _get_time_ago(self, dt):
        """Format a datetime as a human-readable time ago string"""
        if not dt:
            return "Unknown time"
            
        now = fields.Datetime.now()
        delta = now - dt
        
        # Convert to days/hours/minutes
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif minutes > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    # Action Methods
    def action_start_plan(self):
        self.write({'state': 'in_progress', 'actual_start': fields.Datetime.now()})
        return True
    
    def action_complete_plan(self):
        self.write({'state': 'completed', 'actual_end': fields.Datetime.now()})
        return True
    
    def action_cancel_plan(self):
        self.write({'state': 'cancelled'})
        return True
    
    def action_view_tasks(self):
        """Open the task view filtered for this day plan's tasks."""
        self.ensure_one()
        return {
            'name': _('Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'day.plan.task',
            'view_mode': 'kanban,list,calendar,pivot,graph,form',
            'domain': [('day_plan_id', '=', self.id)],
            'context': {'default_day_plan_id': self.id},
        }
    
    def action_new_day_plan(self):
        """Action to create a new day plan"""
        return {
            'name': _('New Day Plan'),
            'type': 'ir.actions.act_window',
            'res_model': 'day.plan',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_employee_id': self.env.user.employee_id.id}
        }

    def action_generate_work_report(self):
        """Action to generate a work report using a wizard popup"""
        self.ensure_one()
        
        # Create context with default values from the current day plan
        context = {
            'default_date_from': self.date,
            'default_date_to': self.date,
            'default_employee_id': self.employee_id.id if self.employee_id else False,
        }
        
        # Return an action to open the report generator wizard
        return {
            'name': _('Generate Work Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'day.plan.report.generator',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }
    
    # Constraints
    @api.constrains('planned_start', 'planned_end')
    def _check_dates(self):
        for plan in self:
            if plan.planned_start and plan.planned_end and plan.planned_end < plan.planned_start:
                raise ValidationError(_("Planned end time cannot be before planned start time"))
    
    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('day.plan') or 'New'
        return super(DayPlan, self).create(vals)
    
    def name_get(self):
        result = []
        for plan in self:
            name = f"[{plan.sequence}] {plan.name}" if plan.sequence else plan.name
            result.append((plan.id, name))
        return result
        
    # Dashboard methods required by client action
    @api.model
    def _ensure_dashboard_exists(self):
        """Ensure dashboard exists - called by client action before loading dashboard"""
        try:
            # No need to create anything - just return success
            return True
        except Exception as e:
            _logger.error("Error in _ensure_dashboard_exists: %s", str(e))
            return True
            
    @api.model
    def _get_default_dashboard(self):
        """Get the user's current day plan or create a new one"""
        try:
            # Get today's plan for the current user
            today = fields.Date.today()
            dashboard = self.search([('employee_id', '=', self.env.user.employee_id.id),
                                ('date', '=', today)], limit=1)
            if not dashboard:
                # Create a new plan for today
                dashboard = self.create({
                    'name': 'Today\'s Plan',
                    'date': today,
                    'employee_id': self.env.user.employee_id.id
                })
            return dashboard
        except Exception as e:
            _logger.error("Error in _get_default_dashboard: %s", str(e))
            # Create an empty non-persistent record to prevent client-side errors
            return self.new({'name': 'Dashboard (Temporary)'})
    
    @api.model
    def action_refresh_dashboard(self):
        """Refresh the dashboard by forcing recomputation of fields"""
        dashboard = self._get_default_dashboard()
        dashboard.invalidate_recordset([
            'total_plans', 'plans_today', 'completed_plans',
            'pending_tasks', 'productivity_chart', 'task_distribution_chart',
            'performance_chart', 'task_priority_chart'
        ])
        return {
            'type': 'ir.actions.client',
            'tag': 'day_plan_work_report_ai.dashboard_action',
            'params': {'message': 'Dashboard refreshed successfully!'}
        }