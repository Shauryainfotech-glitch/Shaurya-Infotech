# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SolarInstallTeam(models.Model):
    _name = "solar.install.team"
    _description = "Installation Team"
    _inherit = ['mail.thread']

    name = fields.Char(
        string="Team Name",
        required=True,
        tracking=True
    )
    code = fields.Char(string="Team Code", required=True)
    description = fields.Text(string="Description")
    member_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Team Members",
        domain="[('active', '=', True)]",
        help="Employees assigned to this installation team"
    )
    skill_ids = fields.Many2many(
        comodel_name="solar.install.skill",
        string="Skills/Certifications",
        help="List of skills or certifications held by this team"
    )
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
        help="Number of active scheduled assignments (planned or in_progress)"
    )
    available_capacity = fields.Integer(
        string="Available Capacity",
        compute="_compute_available_capacity",
        help="Remaining capacity (capacity – current_workload)"
    )

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