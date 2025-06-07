from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Task(models.Model):
    _name = 'avgc.task'
    _description = 'Task Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, due_date, name'
    
    # Basic Information
    name = fields.Char('Task Title', required=True, tracking=True)
    description = fields.Html('Description')
    
    # Related Records
    tender_id = fields.Many2one('avgc.tender', string='Related Tender', ondelete='cascade')
    gem_bid_id = fields.Many2one('avgc.gem.bid', string='Related GeM Bid', ondelete='cascade')
    project_id = fields.Many2one('project.project', string='Project')
    
    # Task Classification
    task_type = fields.Selection([
        ('tender_preparation', 'Tender Preparation'),
        ('document_review', 'Document Review'),
        ('compliance_check', 'Compliance Check'),
        ('vendor_evaluation', 'Vendor Evaluation'),
        ('technical_review', 'Technical Review'),
        ('financial_analysis', 'Financial Analysis'),
        ('approval_workflow', 'Approval Workflow'),
        ('follow_up', 'Follow-up'),
        ('other', 'Other'),
    ], string='Task Type', required=True, tracking=True)
    
    category = fields.Selection([
        ('administrative', 'Administrative'),
        ('technical', 'Technical'),
        ('financial', 'Financial'),
        ('legal', 'Legal'),
        ('compliance', 'Compliance'),
    ], string='Category', required=True)
    
    # Assignment and Ownership
    assigned_to = fields.Many2one('res.users', string='Assigned To', tracking=True)
    created_by = fields.Many2one('res.users', string='Created By', 
                                default=lambda self: self.env.user, tracking=True)
    team_id = fields.Many2one('hr.department', string='Team/Department')
    
    # Status and Priority
    status = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('pending_review', 'Pending Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='medium', required=True, tracking=True)
    
    # Dates and Timeline
    start_date = fields.Date('Start Date', default=fields.Date.today)
    due_date = fields.Date('Due Date', required=True, tracking=True)
    completion_date = fields.Date('Completion Date')
    
    # Progress Tracking
    progress = fields.Float('Progress (%)', digits=(5, 2), default=0.0)
    estimated_hours = fields.Float('Estimated Hours', digits=(16, 2))
    actual_hours = fields.Float('Actual Hours', compute='_compute_actual_hours', store=True)
    
    # Dependencies
    dependency_ids = fields.Many2many('avgc.task', 'task_dependency_rel', 
                                     'task_id', 'dependency_id', 
                                     string='Dependencies')
    dependent_task_ids = fields.Many2many('avgc.task', 'task_dependency_rel', 
                                         'dependency_id', 'task_id', 
                                         string='Dependent Tasks')
    
    # Subtasks
    parent_task_id = fields.Many2one('avgc.task', string='Parent Task')
    child_task_ids = fields.One2many('avgc.task', 'parent_task_id', string='Subtasks')
    
    # Time Tracking
    timesheet_ids = fields.One2many('avgc.task.timesheet', 'task_id', string='Timesheets')
    
    # Checklist
    checklist_ids = fields.One2many('avgc.task.checklist', 'task_id', string='Checklist')
    checklist_progress = fields.Float('Checklist Progress (%)', 
                                     compute='_compute_checklist_progress', digits=(5, 2))
    
    # Comments and Notes
    notes = fields.Text('Notes')
    completion_notes = fields.Text('Completion Notes')
    
    # Computed Fields
    is_overdue = fields.Boolean('Is Overdue', compute='_compute_is_overdue')
    days_overdue = fields.Integer('Days Overdue', compute='_compute_days_overdue')
    can_start = fields.Boolean('Can Start', compute='_compute_can_start')
    
    @api.depends('timesheet_ids.hours')
    def _compute_actual_hours(self):
        for record in self:
            record.actual_hours = sum(record.timesheet_ids.mapped('hours'))
    
    @api.depends('checklist_ids.is_completed')
    def _compute_checklist_progress(self):
        for record in self:
            total_items = len(record.checklist_ids)
            if total_items > 0:
                completed_items = len(record.checklist_ids.filtered('is_completed'))
                record.checklist_progress = (completed_items / total_items) * 100
            else:
                record.checklist_progress = 0
    
    @api.depends('due_date', 'status')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (
                record.due_date and 
                record.due_date < today and 
                record.status not in ['completed', 'cancelled']
            )
    
    @api.depends('due_date', 'status')
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.is_overdue:
                delta = today - record.due_date
                record.days_overdue = delta.days
            else:
                record.days_overdue = 0
    
    @api.depends('dependency_ids.status')
    def _compute_can_start(self):
        for record in self:
            if record.dependency_ids:
                completed_dependencies = record.dependency_ids.filtered(
                    lambda d: d.status == 'completed'
                )
                record.can_start = len(completed_dependencies) == len(record.dependency_ids)
            else:
                record.can_start = True
    
    @api.constrains('start_date', 'due_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.due_date and record.start_date > record.due_date:
                raise ValidationError(_('Start date cannot be after due date.'))
    
    @api.constrains('progress')
    def _check_progress(self):
        for record in self:
            if record.progress < 0 or record.progress > 100:
                raise ValidationError(_('Progress must be between 0 and 100.'))
    
    def action_start(self):
        """Start the task"""
        for record in self:
            if record.status == 'assigned' and record.can_start:
                record.status = 'in_progress'
                record.message_post(body=_('Task started.'))
    
    def action_complete(self):
        """Complete the task"""
        for record in self:
            if record.status in ['in_progress', 'pending_review']:
                record.status = 'completed'
                record.completion_date = fields.Date.today()
                record.progress = 100.0
                record.message_post(body=_('Task completed.'))
    
    def action_submit_for_review(self):
        """Submit task for review"""
        for record in self:
            if record.status == 'in_progress':
                record.status = 'pending_review'
                record.message_post(body=_('Task submitted for review.'))
    
    def action_put_on_hold(self):
        """Put task on hold"""
        for record in self:
            record.status = 'on_hold'
            record.message_post(body=_('Task put on hold.'))
    
    def action_cancel(self):
        """Cancel the task"""
        for record in self:
            record.status = 'cancelled'
            record.message_post(body=_('Task cancelled.'))
    
    def action_create_subtask(self):
        """Create a subtask"""
        return {
            'name': _('Create Subtask'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'avgc.task',
            'target': 'new',
            'context': {
                'default_parent_task_id': self.id,
                'default_tender_id': self.tender_id.id,
                'default_gem_bid_id': self.gem_bid_id.id,
                'default_assigned_to': self.assigned_to.id,
            },
        }


class TaskTimesheet(models.Model):
    _name = 'avgc.task.timesheet'
    _description = 'Task Timesheet'
    _order = 'date desc'
    
    task_id = fields.Many2one('avgc.task', string='Task', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True, 
                             default=lambda self: self.env.user)
    
    # Time Entry
    date = fields.Date('Date', required=True, default=fields.Date.today)
    hours = fields.Float('Hours', digits=(16, 2), required=True)
    description = fields.Text('Work Description', required=True)
    
    # Classification
    work_type = fields.Selection([
        ('development', 'Development'),
        ('analysis', 'Analysis'),
        ('review', 'Review'),
        ('documentation', 'Documentation'),
        ('meeting', 'Meeting'),
        ('testing', 'Testing'),
        ('other', 'Other'),
    ], string='Work Type', required=True, default='development')
    
    @api.constrains('hours')
    def _check_hours(self):
        for record in self:
            if record.hours <= 0 or record.hours > 24:
                raise ValidationError(_('Hours must be between 0 and 24.'))


class TaskChecklist(models.Model):
    _name = 'avgc.task.checklist'
    _description = 'Task Checklist Item'
    _order = 'sequence, name'
    
    task_id = fields.Many2one('avgc.task', string='Task', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    name = fields.Char('Checklist Item', required=True)
    description = fields.Text('Description')
    
    is_completed = fields.Boolean('Completed', default=False)
    completed_by = fields.Many2one('res.users', string='Completed By')
    completion_date = fields.Datetime('Completion Date')
    
    # Requirements
    is_mandatory = fields.Boolean('Mandatory', default=True)
    due_date = fields.Date('Due Date')
    
    def action_complete(self):
        """Mark checklist item as completed"""
        for record in self:
            record.is_completed = True
            record.completed_by = self.env.user
            record.completion_date = fields.Datetime.now()


class TaskTemplate(models.Model):
    _name = 'avgc.task.template'
    _description = 'Task Template'
    _order = 'name'
    
    # Basic Information
    name = fields.Char('Template Name', required=True)
    description = fields.Html('Description')
    
    # Template Configuration
    task_type = fields.Selection([
        ('tender_preparation', 'Tender Preparation'),
        ('document_review', 'Document Review'),
        ('compliance_check', 'Compliance Check'),
        ('vendor_evaluation', 'Vendor Evaluation'),
        ('technical_review', 'Technical Review'),
        ('financial_analysis', 'Financial Analysis'),
        ('approval_workflow', 'Approval Workflow'),
        ('follow_up', 'Follow-up'),
        ('other', 'Other'),
    ], string='Task Type', required=True)
    
    category = fields.Selection([
        ('administrative', 'Administrative'),
        ('technical', 'Technical'),
        ('financial', 'Financial'),
        ('legal', 'Legal'),
        ('compliance', 'Compliance'),
    ], string='Category', required=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Default Priority', default='medium')
    
    # Timeline
    estimated_hours = fields.Float('Estimated Hours', digits=(16, 2))
    duration_days = fields.Integer('Duration (Days)', default=1)
    
    # Template Items
    checklist_template_ids = fields.One2many('avgc.task.checklist.template', 'template_id', 
                                            string='Checklist Template')
    
    # Usage
    is_active = fields.Boolean('Active', default=True)
    usage_count = fields.Integer('Usage Count', default=0)
    
    def action_create_task(self):
        """Create task from template"""
        return {
            'name': _('Create Task from Template'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'avgc.task.create.wizard',
            'target': 'new',
            'context': {'default_template_id': self.id},
        }


class TaskChecklistTemplate(models.Model):
    _name = 'avgc.task.checklist.template'
    _description = 'Task Checklist Template'
    _order = 'sequence, name'
    
    template_id = fields.Many2one('avgc.task.template', string='Template', 
                                 required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    name = fields.Char('Checklist Item', required=True)
    description = fields.Text('Description')
    is_mandatory = fields.Boolean('Mandatory', default=True)
    
    # Timeline
    days_offset = fields.Integer('Days Offset', default=0, 
                               help='Number of days from task start date')


class TaskReport(models.Model):
    _name = 'avgc.task.report'
    _description = 'Task Report'
    _auto = False
    _rec_name = 'task_name'
    
    task_id = fields.Many2one('avgc.task', string='Task')
    task_name = fields.Char('Task Name')
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('pending_review', 'Pending Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ], string='Status')
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority')
    
    due_date = fields.Date('Due Date')
    completion_date = fields.Date('Completion Date')
    estimated_hours = fields.Float('Estimated Hours')
    actual_hours = fields.Float('Actual Hours')
    progress = fields.Float('Progress (%)')
    
    is_overdue = fields.Boolean('Is Overdue')
    days_overdue = fields.Integer('Days Overdue')
    
    tender_id = fields.Many2one('avgc.tender', string='Tender')
    gem_bid_id = fields.Many2one('avgc.gem.bid', string='GeM Bid')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    t.id,
                    t.id as task_id,
                    t.name as task_name,
                    t.assigned_to,
                    t.status,
                    t.priority,
                    t.due_date,
                    t.completion_date,
                    t.estimated_hours,
                    t.actual_hours,
                    t.progress,
                    CASE 
                        WHEN t.due_date < CURRENT_DATE AND t.status NOT IN ('completed', 'cancelled') 
                        THEN true 
                        ELSE false 
                    END as is_overdue,
                    CASE 
                        WHEN t.due_date < CURRENT_DATE AND t.status NOT IN ('completed', 'cancelled') 
                        THEN CURRENT_DATE - t.due_date 
                        ELSE 0 
                    END as days_overdue,
                    t.tender_id,
                    t.gem_bid_id
                FROM avgc_task t
            )
        """ % self._table)