# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SolarInstallTeam(models.Model):
    _name = "solar.install.team"
    _description = "Installation Team"
    _inherit = ['mail.thread']
    _order = "name"

    name = fields.Char(
        string="Team Name",
        required=True,
        tracking=True
    )
    code = fields.Char(
        string="Team Code", 
        required=True,
        copy=False,
        help="Unique team identifier"
    )
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    
    # Team composition
    team_leader_id = fields.Many2one(
        'hr.employee',
        string="Team Leader",
        domain="[('active', '=', True)]",
        tracking=True
    )
    member_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Team Members",
        domain="[('active', '=', True)]",
        help="Employees assigned to this installation team"
    )
    member_count = fields.Integer(
        string="Team Size",
        compute="_compute_member_count",
        store=True
    )
    
    # Skills and capabilities
    skill_ids = fields.Many2many(
        comodel_name="solar.install.skill",
        string="Skills/Certifications",
        help="List of skills or certifications held by this team"
    )
    specialization = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
        ('maintenance', 'Maintenance'),
        ('all', 'All Types')
    ], string="Specialization", default='all')
    
    # Capacity management
    capacity = fields.Integer(
        string="Max Simultaneous Projects",
        default=1,
        help="Max number of projects this team can handle concurrently"
    )
    schedule_ids = fields.One2many(
        comodel_name="solar.install.schedule",
        inverse_name="team_id",
        string="Assigned Schedules",
        readonly=True
    )
    current_workload = fields.Integer(
        string="Current Workload",
        compute="_compute_current_workload",
        store=True,
        help="Number of active scheduled assignments (planned or in_progress)"
    )
    available_capacity = fields.Integer(
        string="Available Capacity",
        compute="_compute_available_capacity",
        store=True,
        help="Remaining capacity (capacity – current_workload)"
    )
    
    # Performance tracking
    completed_projects = fields.Integer(
        string="Completed Projects",
        compute="_compute_performance_metrics",
        store=True
    )
    avg_project_duration = fields.Float(
        string="Avg Project Duration (days)",
        compute="_compute_performance_metrics",
        store=True
    )

    @api.depends('member_ids')
    def _compute_member_count(self):
        for team in self:
            team.member_count = len(team.member_ids)

    @api.depends('schedule_ids', 'schedule_ids.state')
    def _compute_current_workload(self):
        for rec in self:
            active_schedules = rec.schedule_ids.filtered(
                lambda s: s.state in ['planned', 'in_progress']
            )
            rec.current_workload = len(active_schedules)

    @api.depends('capacity', 'current_workload')
    def _compute_available_capacity(self):
        for rec in self:
            rec.available_capacity = rec.capacity - rec.current_workload

    @api.depends('schedule_ids', 'schedule_ids.state', 'schedule_ids.project_id')
    def _compute_performance_metrics(self):
        for team in self:
            completed_schedules = team.schedule_ids.filtered(lambda s: s.state == 'done')
            completed_projects_ids = completed_schedules.mapped('project_id').filtered(
                lambda p: p.state == 'completed'
            )
            team.completed_projects = len(completed_projects_ids)
            
            if completed_projects_ids:
                total_duration = sum([
                    (p.actual_end_date - p.actual_start_date).days 
                    for p in completed_projects_ids 
                    if p.actual_start_date and p.actual_end_date
                ])
                projects_with_dates = len([
                    p for p in completed_projects_ids 
                    if p.actual_start_date and p.actual_end_date
                ])
                team.avg_project_duration = total_duration / projects_with_dates if projects_with_dates else 0
            else:
                team.avg_project_duration = 0

    @api.constrains('capacity')
    def _check_capacity(self):
        for team in self:
            if team.capacity <= 0:
                raise ValidationError("Team capacity must be greater than 0!")

    @api.constrains('code')
    def _check_unique_code(self):
        for team in self:
            if self.search_count([('code', '=', team.code), ('id', '!=', team.id)]) > 0:
                raise ValidationError(f"Team code '{team.code}' already exists!")

    @api.constrains('team_leader_id', 'member_ids')
    def _check_team_leader_in_members(self):
        for team in self:
            if team.team_leader_id and team.team_leader_id not in team.member_ids:
                raise ValidationError("Team leader must be included in team members!")

    def action_view_schedules(self):
        """Smart button action to view team schedules"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} Schedules',
            'res_model': 'solar.install.schedule',
            'view_mode': 'tree,form,calendar',
            'domain': [('team_id', '=', self.id)],
            'context': {'default_team_id': self.id}
        }

    def check_availability(self, start_date, end_date):
        """Check if team is available for given date range"""
        self.ensure_one()
        if self.available_capacity <= 0:
            return False
        
        conflicting_schedules = self.schedule_ids.filtered(
            lambda s: s.state in ['planned', 'in_progress'] and
            s.start_datetime.date() <= end_date and
            s.end_datetime.date() >= start_date
        )
        return len(conflicting_schedules) < self.capacity
