from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

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
    completed_plans = fields.Integer(compute='_compute_dashboard_stats', string="Completed Plans")
    in_progress_plans = fields.Integer(compute='_compute_dashboard_stats', string="In Progress Plans")
    pending_tasks = fields.Integer(compute='_compute_dashboard_stats', string="Pending Tasks")
    overdue_tasks = fields.Integer(compute='_compute_dashboard_stats', string="Overdue Tasks")
    tasks_due_today = fields.Integer(compute='_compute_dashboard_stats', string="Tasks Due Today")
    
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
        user_plans = self.search([('employee_id', '=', self.env.user.employee_id.id)])
        
        # Get all tasks for the user
        tasks = self.env['day.plan.task'].search([
            ('day_plan_id.employee_id', '=', self.env.user.employee_id.id)
        ])
        
        # Compute stats for all records in self
        for plan in self:
            # Plan stats
            plan.plans_today = len(user_plans.filtered(
                lambda p: p.date == today
            ))
            plan.completed_plans = len(user_plans.filtered(
                lambda p: p.state == 'completed' and p.date.month == today.month
            ))
            plan.in_progress_plans = len(user_plans.filtered(
                lambda p: p.state == 'in_progress'
            ))
            
            # Task stats - handle cases where deadline might not exist
            plan.pending_tasks = len(tasks.filtered(
                lambda t: t.status in ['todo', 'in_progress']
            ))
            
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
            else:
                plan.overdue_tasks = 0
                plan.tasks_due_today = 0
    
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