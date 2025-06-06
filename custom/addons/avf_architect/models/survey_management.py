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

    name = fields.Char(string='Survey Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    survey_type = fields.Selection([
        ('topographical', 'Topographical Survey'),
        ('boundary', 'Boundary Survey'),
        ('condition', 'Condition Survey'),
        ('soil', 'Soil Survey')
    ], string='Survey Type', required=True)

    survey_date = fields.Date(string='Survey Date')
    surveyor_name = fields.Char(string='Surveyor Name')
    location = fields.Text(string='Survey Location')

    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='planned')

    survey_data = fields.Text(string='Survey Data')
    coordinates = fields.Text(string='Coordinates')
    area_measured = fields.Float(string='Area Measured (sq ft)')

    attachments = fields.Many2many('ir.attachment', string='Survey Documents')

class ArchitectSurveyEquipment(models.Model):
    _name = 'architect.survey.equipment'
    _description = 'Survey Equipment'

    name = fields.Char(string='Equipment Name', required=True)
    equipment_type = fields.Selection([
        ('measurement', 'Measurement Tools'),
        ('surveying', 'Surveying Equipment'),
        ('testing', 'Testing Equipment'),
        ('recording', 'Recording Devices'),
        ('safety', 'Safety Equipment')
    ], string='Equipment Type')
    description = fields.Text(string='Description')
    specifications = fields.Text(string='Specifications')
    calibration_date = fields.Date(string='Last Calibration')
    next_calibration = fields.Date(string='Next Calibration Due')

    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')


class ArchitectSurveyPoint(models.Model):
    _name = 'architect.survey.point'
    _description = 'Survey Point'
    _order = 'sequence, id'

    name = fields.Char(string='Point Reference', required=True)
    survey_id = fields.Many2one('architect.survey', string='Survey', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    # Coordinates
    latitude = fields.Float(string='Latitude', digits=(16, 8))
    longitude = fields.Float(string='Longitude', digits=(16, 8))
    elevation = fields.Float(string='Elevation')

    # Point Details
    point_type = fields.Selection([
        ('boundary', 'Boundary Point'),
        ('control', 'Control Point'),
        ('feature', 'Feature Point'),
        ('elevation', 'Elevation Point'),
        ('reference', 'Reference Point')
    ], string='Point Type')

    description = fields.Text(string='Description')
    remarks = fields.Text(string='Remarks')

    _sql_constraints = [
        ('unique_point_ref', 'unique(name, survey_id)', 
         'Point reference must be unique per survey!')
    ]