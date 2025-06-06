# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ArchitectSurvey(models.Model):
    _name = 'architect.survey'
    _description = 'Survey Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Survey Name', required=True, tracking=True)
    survey_code = fields.Char(string='Survey Code', required=True, copy=False, readonly=True,
                              default=lambda self: _('New'))

    project_id = fields.Many2one('architect.project', string='Project', required=True)

    survey_type = fields.Selection([
        ('topographical', 'Topographical Survey'),
        ('boundary', 'Boundary Survey'),
        ('soil', 'Soil Survey'),
        ('environmental', 'Environmental Survey'),
        ('traffic', 'Traffic Survey'),
        ('utility', 'Utility Survey')
    ], string='Survey Type', required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    survey_date = fields.Date(string='Survey Date')
    completion_date = fields.Date(string='Completion Date')

    surveyor_id = fields.Many2one('res.users', string='Surveyor', required=True)
    survey_team = fields.Many2many('res.users', string='Survey Team')

    location = fields.Text(string='Survey Location')
    coordinates = fields.Char(string='GPS Coordinates')

    # Results and findings
    findings = fields.Text(string='Survey Findings')
    recommendations = fields.Text(string='Recommendations')

    # File attachments - rename to avoid conflict
    survey_attachment_count = fields.Integer(string='Survey Attachments', compute='_compute_survey_attachment_count')

    # Survey specific fields
    area_surveyed = fields.Float(string='Area Surveyed (sq m)')
    survey_accuracy = fields.Selection([
        ('high', 'High Precision'),
        ('medium', 'Medium Precision'),
        ('standard', 'Standard Precision')
    ], string='Survey Accuracy', default='standard')

    equipment_used = fields.Text(string='Equipment Used')
    weather_conditions = fields.Char(string='Weather Conditions')

    user_id = fields.Many2one('res.users', string='Survey Responsible', 
                              default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'survey_code' not in vals or not vals['survey_code']:
                vals['survey_code'] = self.env['ir.sequence'].next_by_code('architect.survey') or 'New'
        return super(ArchitectSurvey, self).create(vals_list)

    @api.depends('message_ids.attachment_ids')
    def _compute_survey_attachment_count(self):
        for record in self:
            record.survey_attachment_count = len(record.message_ids.attachment_ids)

    def action_start_survey(self):
        self.state = 'in_progress'
        self.survey_date = fields.Date.today()

    def action_complete_survey(self):
        self.state = 'completed'
        self.completion_date = fields.Date.today()

    def action_cancel_survey(self):
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        self.state = 'draft'

class SurveyManagement(models.Model):
    _name = 'avf.survey.management'
    _description = 'Survey Management'
    _rec_name = 'name'
    _order = 'survey_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Survey Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    survey_number = fields.Char(string='Survey Number', readonly=True)

    survey_type = fields.Selection([
        ('topographic', 'Topographic Survey'),
        ('boundary', 'Boundary Survey'),
        ('building', 'Building Survey'),
        ('site', 'Site Survey'),
        ('utility', 'Utility Survey'),
        ('environmental', 'Environmental Survey')
    ], string='Survey Type', required=True)

    survey_date = fields.Date(string='Survey Date', required=True)
    surveyor_id = fields.Many2one('res.users', string='Surveyor', required=True)
    team_members = fields.Many2many('res.users', string='Team Members')

    # Location details
    location = fields.Char(string='Location', required=True)
    coordinates = fields.Char(string='GPS Coordinates')
    area_covered = fields.Float(string='Area Covered (sq.m)')

    # Survey data
    survey_data = fields.Text(string='Survey Data')
    equipment_used = fields.Text(string='Equipment Used')
    weather_conditions = fields.Char(string='Weather Conditions')

    # Results
    survey_report = fields.Binary(string='Survey Report', attachment=True)
    report_filename = fields.Char(string='Report Filename')
    drawings = fields.Binary(string='Survey Drawings', attachment=True)
    drawings_filename = fields.Char(string='Drawings Filename')

    # Status
    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved')
    ], string='Status', default='planned', tracking=True)

    # Additional info
    notes = fields.Text(string='Notes')
    issues_encountered = fields.Text(string='Issues Encountered')
    recommendations = fields.Text(string='Recommendations')

    @api.model
    def create(self, vals):
        if not vals.get('survey_number'):
            vals['survey_number'] = self.env['ir.sequence'].next_by_code('avf.survey.management') or _('SUR001')
        return super(SurveyManagement, self).create(vals)

    def action_start_survey(self):
        """Start the survey"""
        self.ensure_one()
        if self.status != 'planned':
            raise ValidationError(_("Only planned surveys can be started."))
        self.status = 'in_progress'
        self.message_post(body=_("Survey started."))

    def action_complete_survey(self):
        """Complete the survey"""
        self.ensure_one()
        if self.status != 'in_progress':
            raise ValidationError(_("Only in-progress surveys can be completed."))
        self.status = 'completed'
        self.message_post(body=_("Survey completed."))

    def action_approve_survey(self):
        """Approve the survey"""
        self.ensure_one()
        if self.status != 'reviewed':
            raise ValidationError(_("Only reviewed surveys can be approved."))
        self.status = 'approved'
        self.message_post(body=_("Survey approved."))

class SurveyPoint(models.Model):
    _name = 'avf.survey.point'
    _description = 'Survey Point'
    _rec_name = 'point_name'

    survey_id = fields.Many2one('avf.survey.management', string='Survey', required=True, ondelete='cascade')
    point_name = fields.Char(string='Point Name', required=True)
    point_type = fields.Selection([
        ('benchmark', 'Benchmark'),
        ('control', 'Control Point'),
        ('boundary', 'Boundary Point'),
        ('elevation', 'Elevation Point'),
        ('utility', 'Utility Point')
    ], string='Point Type', required=True)

    # Coordinates
    latitude = fields.Float(string='Latitude', digits=(10, 6))
    longitude = fields.Float(string='Longitude', digits=(10, 6))
    elevation = fields.Float(string='Elevation (m)')

    # Additional data
    description = fields.Text(string='Description')
    accuracy = fields.Float(string='Accuracy (cm)')
    measurement_date = fields.Datetime(string='Measurement Date', default=fields.Datetime.now)

class SurveyEquipment(models.Model):
    _name = 'avf.survey.equipment'
    _description = 'Survey Equipment'
    _rec_name = 'equipment_name'

    equipment_name = fields.Char(string='Equipment Name', required=True)
    equipment_type = fields.Selection([
        ('total_station', 'Total Station'),
        ('gps', 'GPS Receiver'),
        ('level', 'Level'),
        ('theodolite', 'Theodolite'),
        ('laser_scanner', 'Laser Scanner'),
        ('drone', 'Drone')
    ], string='Equipment Type', required=True)

    model = fields.Char(string='Model')
    serial_number = fields.Char(string='Serial Number')
    accuracy = fields.Char(string='Accuracy')
    calibration_date = fields.Date(string='Last Calibration Date')
    next_calibration = fields.Date(string='Next Calibration Due')

    status = fields.Selection([
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('calibration', 'Under Calibration')
    ], string='Status', default='available')

    notes = fields.Text(string='Notes')