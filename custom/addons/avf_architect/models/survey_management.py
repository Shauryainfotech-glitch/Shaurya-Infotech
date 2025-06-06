# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class SurveyType(models.Model):
    _name = 'avf.survey.type'
    _description = 'Survey Type'
    _rec_name = 'name'

    name = fields.Char(string='Survey Type', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

class SurveyManagement(models.Model):
    _name = 'avf.survey.management'
    _description = 'Survey Management'
    _rec_name = 'name'
    _order = 'survey_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Survey Name', required=True, default=lambda self: _('New'))
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    survey_number = fields.Char(string='Survey Number', readonly=True)
    survey_date = fields.Date(string='Survey Date', required=True, default=fields.Date.today)

    # Survey details
    survey_type_id = fields.Many2one('avf.survey.type', string='Survey Type', required=True)
    survey_purpose = fields.Text(string='Survey Purpose')
    survey_area = fields.Float(string='Survey Area (sq m)')

    # Location details
    latitude = fields.Float(string='Latitude', digits=(10, 6))
    longitude = fields.Float(string='Longitude', digits=(10, 6))
    elevation = fields.Float(string='Elevation (m)')

    # Survey team
    surveyor_id = fields.Many2one('res.users', string='Lead Surveyor', required=True)
    team_member_ids = fields.Many2many('res.users', string='Team Members')

    # Equipment used
    equipment_used = fields.Text(string='Equipment Used')
    weather_conditions = fields.Text(string='Weather Conditions')

    # Results
    survey_findings = fields.Text(string='Survey Findings')
    recommendations = fields.Text(string='Recommendations')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved')
    ], string='Status', default='draft', tracking=True)

    # Files
    survey_report = fields.Binary(string='Survey Report', attachment=True)
    survey_filename = fields.Char(string='Filename')
    survey_drawings = fields.Binary(string='Survey Drawings', attachment=True)
    drawings_filename = fields.Char(string='Drawings Filename')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('avf.survey.management') or _('New')
            if not vals.get('survey_number'):
                vals['survey_number'] = self.env['ir.sequence'].next_by_code('avf.survey.number') or 'SUR-001'
        return super(SurveyManagement, self).create(vals_list)

    def action_start_survey(self):
        """Start the survey"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_("Only draft surveys can be started."))
        self.state = 'in_progress'
        self.message_post(body=_("Survey started."))

    def action_complete_survey(self):
        """Complete the survey"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError(_("Only in-progress surveys can be completed."))
        self.state = 'completed'
        self.message_post(body=_("Survey completed."))

    def action_approve_survey(self):
        """Approve the survey"""
        self.ensure_one()
        if self.state != 'completed':
            raise ValidationError(_("Only completed surveys can be approved."))
        self.state = 'approved'
        self.message_post(body=_("Survey approved."))

class SurveyPoint(models.Model):
    _name = 'avf.survey.point'
    _description = 'Survey Points'
    _rec_name = 'point_name'

    survey_id = fields.Many2one('avf.survey.management', string='Survey', required=True, ondelete='cascade')
    point_name = fields.Char(string='Point Name', required=True)
    point_number = fields.Char(string='Point Number')

    # Coordinates
    x_coordinate = fields.Float(string='X Coordinate', digits=(12, 6))
    y_coordinate = fields.Float(string='Y Coordinate', digits=(12, 6))
    z_coordinate = fields.Float(string='Z Coordinate', digits=(12, 6))

    # Point details
    point_type = fields.Selection([
        ('boundary', 'Boundary Point'),
        ('control', 'Control Point'),
        ('reference', 'Reference Point'),
        ('feature', 'Feature Point')
    ], string='Point Type', required=True)

    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        return super(SurveyPoint, self).create(vals_list)

class SurveyEquipment(models.Model):
    _name = 'avf.survey.equipment'
    _description = 'Survey Equipment'
    _rec_name = 'name'

    name = fields.Char(string='Equipment Name', required=True)
    equipment_type = fields.Selection([
        ('total_station', 'Total Station'),
        ('gps', 'GPS/GNSS'),
        ('level', 'Level'),
        ('theodolite', 'Theodolite'),
        ('prism', 'Prism'),
        ('tripod', 'Tripod'),
        ('measuring_tape', 'Measuring Tape')
    ], string='Equipment Type', required=True)

    model = fields.Char(string='Model')
    serial_number = fields.Char(string='Serial Number')
    calibration_date = fields.Date(string='Last Calibration')
    next_calibration = fields.Date(string='Next Calibration')

    accuracy = fields.Char(string='Accuracy')
    status = fields.Selection([
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('calibration', 'Calibration Required')
    ], string='Status', default='available')

    @api.model_create_multi
    def create(self, vals_list):
        return super(SurveyEquipment, self).create(vals_list)