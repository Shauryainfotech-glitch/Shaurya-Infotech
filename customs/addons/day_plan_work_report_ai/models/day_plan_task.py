from odoo import models, fields, api

class DayPlanTask(models.Model):
    _name = "day.plan.task"
    _description = "Task in a Day Plan"
    _order = "priority desc, deadline, id"

    name = fields.Char(string="Task", required=True)
    description = fields.Text(string="Description")
    deadline = fields.Datetime(string="Deadline")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string="Priority", default='1')
    status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], default='todo', string="Status")
    estimated_hours = fields.Float(string="Estimated Hours")
    actual_hours = fields.Float(string="Actual Hours")
    progress = fields.Float(string="Progress %", default=0.0)
    day_plan_id = fields.Many2one('day.plan', string="Day Plan", ondelete='cascade')
    
    # Enhanced Task Categorization
    project_id = fields.Many2one('project.project', string="Project")
    task_type = fields.Selection([
        ('development', 'Development'),
        ('meeting', 'Meeting'),
        ('documentation', 'Documentation'),
        ('research', 'Research'),
        ('planning', 'Planning'),
        ('testing', 'Testing'),
        ('review', 'Review'),
        ('support', 'Support'),
        ('other', 'Other')
    ], string="Task Type")
    tag_ids = fields.Many2many('day.plan.task.tag', string="Tags")
    blocker_notes = fields.Text(string="Blockers", 
                              help="Document any blockers preventing task completion")
    
    # Time tracking
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    
    @api.onchange('start_time', 'end_time')
    def _onchange_time_tracking(self):
        """Calculate actual hours when start/end times change"""
        for task in self:
            if task.start_time and task.end_time and task.end_time > task.start_time:
                # Calculate hours difference
                delta = task.end_time - task.start_time
                task.actual_hours = delta.total_seconds() / 3600
    
    @api.onchange('actual_hours', 'estimated_hours')
    def _onchange_hours(self):
        """Update progress based on hours"""
        for task in self:
            if task.estimated_hours:
                if task.actual_hours >= task.estimated_hours:
                    if task.status != 'done':
                        task.progress = 100.0
                else:
                    task.progress = (task.actual_hours / task.estimated_hours) * 100
    
    def action_start_task(self):
        """Mark task as started and record start time"""
        self.ensure_one()
        self.write({
            'status': 'in_progress',
            'start_time': fields.Datetime.now()
        })
    
    def action_complete_task(self):
        """Mark task as completed and record end time"""
        self.ensure_one()
        self.write({
            'status': 'done',
            'progress': 100.0,
            'end_time': fields.Datetime.now()
        })
        
        # Update actual hours if start time exists
        if self.start_time and not self.actual_hours:
            delta = fields.Datetime.now() - self.start_time
            self.actual_hours = delta.total_seconds() / 3600
    
    def action_cancel_task(self):
        """Mark task as cancelled"""
        self.ensure_one()
        self.write({
            'status': 'cancelled'
        })


class DayPlanTaskTag(models.Model):
    _name = "day.plan.task.tag"
    _description = "Task Tag"
    
    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string="Color Index")
