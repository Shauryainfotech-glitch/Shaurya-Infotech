# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ArchitectTeam(models.Model):
    _name = 'architect.team'
    _description = 'Architect Team'
    _rec_name = 'name'

    name = fields.Char(string='Team Name', required=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    team_lead_id = fields.Many2one('res.users', string='Team Lead', required=True)
    member_ids = fields.One2many('architect.team.member', 'team_id', string='Team Members')

    description = fields.Text(string='Team Description')
    active = fields.Boolean(string='Active', default=True)

    # Computed fields for statistics
    member_count = fields.Integer(string='Member Count', compute='_compute_member_count')
    active_project_count = fields.Integer(string='Active Projects', compute='_compute_project_stats')

    @api.depends('member_ids')
    def _compute_member_count(self):
        for team in self:
            team.member_count = len(team.member_ids)

    @api.depends('project_id', 'project_id.stage_id')
    def _compute_project_stats(self):
        for team in self:
            # Count active projects for this team
            active_projects = self.env['architect.project'].search_count([
                ('team_ids', 'in', team.ids),
                ('stage_id.name', '!=', 'Completed')
            ])
            team.active_project_count = active_projects

class ArchitectTeamMember(models.Model):
    _name = 'architect.team.member'
    _description = 'Architect Team Member'
    _rec_name = 'user_id'

    team_id = fields.Many2one('architect.team', string='Team', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)

    role = fields.Selection([
        ('architect', 'Architect'),
        ('engineer', 'Engineer'),
        ('drafter', 'Drafter'),
        ('surveyor', 'Surveyor'),
        ('consultant', 'Consultant'),
        ('coordinator', 'Project Coordinator')
    ], string='Role', required=True)

    # Rename to avoid conflict with hr module
    member_skill_ids = fields.Many2many('architect.skill', string='Member Skills')

    join_date = fields.Date(string='Join Date', default=fields.Date.today)
    hourly_rate = fields.Float(string='Hourly Rate')

    is_active = fields.Boolean(string='Active', default=True)
    availability = fields.Selection([
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('consultant', 'Consultant')
    ], string='Availability', default='full_time')

class ArchitectSkill(models.Model):
    _name = 'architect.skill'
    _description = 'Architect Skills'
    _rec_name = 'name'

    name = fields.Char(string='Skill Name', required=True)
    category = fields.Selection([
        ('technical', 'Technical'),
        ('design', 'Design'),
        ('management', 'Management'),
        ('software', 'Software'),
        ('compliance', 'Compliance')
    ], string='Category', required=True)

    description = fields.Text(string='Description')
    level_required = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], string='Required Level', default='intermediate')

class TeamCollaboration(models.Model):
    _name = 'architect.team.collaboration'
    _description = 'Team Collaboration'
    _rec_name = 'name'

    name = fields.Char(string='Collaboration Name', required=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    team_id = fields.Many2one('architect.team', string='Team', required=True)

    collaboration_type = fields.Selection([
        ('meeting', 'Team Meeting'),
        ('review', 'Design Review'),
        ('coordination', 'Coordination Session'),
        ('training', 'Training Session')
    ], string='Type', required=True)

    scheduled_date = fields.Datetime(string='Scheduled Date')
    duration = fields.Float(string='Duration (hours)')
    location = fields.Char(string='Location')

    participant_ids = fields.Many2many('res.users', string='Participants')
    agenda = fields.Text(string='Agenda')
    minutes = fields.Text(string='Minutes')
    action_items = fields.Text(string='Action Items')

    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='scheduled')