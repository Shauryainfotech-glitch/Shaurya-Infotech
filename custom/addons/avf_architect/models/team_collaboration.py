
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AVFTeamCollaboration(models.Model):
    _name = 'avf.team.collaboration'
    _description = 'Team Collaboration'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Task/Discussion Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    
    collaboration_type = fields.Selection([
        ('task', 'Task Assignment'),
        ('discussion', 'Team Discussion'),
        ('review', 'Design Review'),
        ('meeting', 'Team Meeting'),
        ('decision', 'Decision Making'),
        ('brainstorm', 'Brainstorming')
    ], string='Collaboration Type', required=True)
    
    description = fields.Text(string='Description')
    
    # Team Members
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    team_member_ids = fields.Many2many('res.users', string='Team Members')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    
    # Status and Priority
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='medium')
    
    # Dates
    start_date = fields.Datetime(string='Start Date')
    due_date = fields.Datetime(string='Due Date')
    completion_date = fields.Datetime(string='Completion Date')
    
    # Progress
    progress_percentage = fields.Float(string='Progress %')
    
    # Communication
    message_ids = fields.One2many('avf.team.message', 'collaboration_id', string='Messages')
    file_ids = fields.Many2many('ir.attachment', string='Shared Files')
    
    # Meeting specific fields
    meeting_date = fields.Datetime(string='Meeting Date')
    meeting_location = fields.Char(string='Meeting Location')
    agenda = fields.Text(string='Agenda')
    minutes = fields.Text(string='Minutes of Meeting')
    
    def action_start(self):
        """Start collaboration"""
        self.ensure_one()
        self.state = 'active'
        self.start_date = fields.Datetime.now()

    def action_complete(self):
        """Complete collaboration"""
        self.ensure_one()
        self.state = 'completed'
        self.completion_date = fields.Datetime.now()
        self.progress_percentage = 100.0

    def action_cancel(self):
        """Cancel collaboration"""
        self.ensure_one()
        self.state = 'cancelled'

class AVFTeamMessage(models.Model):
    _name = 'avf.team.message'
    _description = 'Team Messages'
    _order = 'create_date desc'

    collaboration_id = fields.Many2one('avf.team.collaboration', string='Collaboration', 
                                     required=True, ondelete='cascade')
    
    message = fields.Text(string='Message', required=True)
    author_id = fields.Many2one('res.users', string='Author', 
                               default=lambda self: self.env.user, required=True)
    
    message_type = fields.Selection([
        ('comment', 'Comment'),
        ('update', 'Status Update'),
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('file_share', 'File Share')
    ], string='Message Type', default='comment')
    
    # Files
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Replies
    parent_message_id = fields.Many2one('avf.team.message', string='Reply To')
    reply_ids = fields.One2many('avf.team.message', 'parent_message_id', string='Replies')
    
    # Mentions
    mentioned_user_ids = fields.Many2many('res.users', 'team_message_mention_rel', 
                                        string='Mentioned Users')
    
    # Status
    is_read = fields.Boolean(string='Read', default=False)
    read_date = fields.Datetime(string='Read Date')

class ArchitectTeam(models.Model):
    _name = 'architect.team'
    _description = 'Architect Team'
    _rec_name = 'name'

    name = fields.Char(string='Team Name', required=True)
    description = fields.Text(string='Description')
    team_lead_id = fields.Many2one('res.users', string='Team Leader', required=True)
    
    # Team Members
    member_ids = fields.One2many('architect.team.member', 'team_id', string='Team Members')
    member_count = fields.Integer(string='Member Count', compute='_compute_member_count')
    
    # Projects
    project_ids = fields.Many2many('project.project', string='Assigned Projects')
    
    # Skills
    skill_ids = fields.Many2many('architect.skill', string='Team Skills')
    
    # Status
    active = fields.Boolean(default=True)
    created_date = fields.Date(string='Created Date', default=fields.Date.today)

    @api.depends('member_ids')
    def _compute_member_count(self):
        for team in self:
            team.member_count = len(team.member_ids.filtered('active'))

class ArchitectTeamMember(models.Model):
    _name = 'architect.team.member'
    _description = 'Team Member'
    _rec_name = 'user_id'

    team_id = fields.Many2one('architect.team', string='Team', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Team Member', required=True)
    role = fields.Selection([
        ('architect', 'Architect'),
        ('engineer', 'Engineer'),
        ('draftsman', 'Draftsman'),
        ('surveyor', 'Surveyor'),
        ('coordinator', 'Project Coordinator'),
        ('assistant', 'Assistant')
    ], string='Role', required=True)

    join_date = fields.Date(string='Join Date', default=fields.Date.today)
    active = fields.Boolean(string='Active', default=True)
    responsibilities = fields.Text(string='Responsibilities')
    
    # Skills
    skill_ids = fields.Many2many('architect.skill', string='Skills')
    experience_years = fields.Float(string='Experience (Years)')
    
    # Performance
    current_workload = fields.Float(string='Current Workload %')
    performance_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Below Average'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string='Performance Rating')

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
    
    certification_required = fields.Boolean(string='Certification Required')
    active = fields.Boolean(default=True)
