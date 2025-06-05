# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


class SolarInstallSchedule(models.Model):
    _name = "solar.install.schedule"
    _description = "Installation Schedule for Solar Projects"
    _inherit = ['mail.thread']

    project_id = fields.Many2one(
        comodel_name="solar.project",
        string="Project",
        required=True,
        ondelete="cascade",
        tracking=True
    )
    team_id = fields.Many2one(
        comodel_name="solar.install.team",
        string="Installation Team",
        required=True,
        ondelete="restrict",
        tracking=True,
        help="Team assigned to this schedule entry"
    )
    scheduled_by = fields.Many2one(
        comodel_name="res.users",
        string="Scheduled By",
        default=lambda self: self.env.user
    )
    start_datetime = fields.Datetime(
        string="Start DateTime",
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    duration_hours = fields.Float(
        string="Duration (Hours)",
        required=True,
        default=8.0
    )
    end_datetime = fields.Datetime(
        string="End DateTime",
        compute="_compute_end_datetime",
        store=True
    )
    assigned_employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Assigned Employees",
        domain="[('id', 'in', team_id.member_ids)]",
        help="Specific employees from the team to assign to this shift"
    )
    state = fields.Selection(
        selection=[
            ('planned', 'Planned'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string="Schedule Status",
        default='planned',
        tracking=True
    )
    notes = fields.Text(string="Schedule Notes")

    @api.depends('start_datetime', 'duration_hours')
    def _compute_end_datetime(self):
        for rec in self:
            if rec.start_datetime and rec.duration_hours >= 0:
                rec.end_datetime = rec.start_datetime + timedelta(hours=rec.duration_hours)
            else:
                rec.end_datetime = rec.start_datetime

    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_consistency(self):
        for rec in self:
            if rec.end_datetime and rec.start_datetime:
                if rec.end_datetime < rec.start_datetime:
                    raise models.ValidationError("End date/time cannot be earlier than start date/time.")

    def action_start(self):
        for rec in self:
            if rec.state != 'planned':
                raise models.UserError("Only planned schedules can be started.")
            rec.state = 'in_progress'
            if rec.project_id.state == 'scheduled':
                rec.project_id.state = 'in_progress'

    def action_done(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise models.UserError("Only in-progress schedules can be marked as done.")
            rec.state = 'done'
            other_scheds = rec.project_id.schedule_ids.filtered(
                lambda s: s.id != rec.id and s.state not in ['done', 'cancelled']
            )
            if not other_scheds:
                rec.project_id.state = 'completed'

    def action_cancel(self):
        for rec in self:
            if rec.state in ['done']:
                raise models.UserError("Cannot cancel a done schedule.")
            rec.state = 'cancelled'
            active_scheds = rec.project_id.schedule_ids.filtered(
                lambda s: s.state in ['planned', 'in_progress']
            )
            if not active_scheds:
                rec.project_id.state = 'confirmed'
