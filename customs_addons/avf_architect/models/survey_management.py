# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ArchitectSurvey(models.Model):
    _name = 'architect.survey'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Site Survey'
    _order = 'survey_date desc, id desc'

    name = fields.Char(string='Survey Reference', required=True, tracking=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    # Survey Details
    survey_type = fields.Selection([
        ('preliminary', 'Preliminary Survey'),
        ('detailed', 'Detailed Survey'),
        ('topographical', 'Topographical Survey'),
        ('soil', 'Soil Investigation'),
        ('environmental', 'Environmental Survey'),
        ('structural', 'Structural Assessment'),
        ('utilities', 'Utilities Survey')
    ], string='Survey Type', required=True)
    
    survey_date = fields.Date(string='Survey Date', required=True, default=fields.Date.today)
    location = fields.Text(string='Survey Location', required=True)
    area_surveyed = fields.Float(string='Area Surveyed (sq.m)')
    
    # Survey Team
    surveyor_id = fields.Many2one('res.users', string='Lead Surveyor', 
                                 default=lambda self: self.env.user)
    team_member_ids = fields.Many2many('res.users', string='Survey Team')
    
    # Equipment Used
    equipment_ids = fields.Many2many('architect.survey.equipment', string='Equipment Used')
    
    # Weather Conditions
    weather_condition = fields.Selection([
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('windy', 'Windy'),
        ('stormy', 'Stormy')
    ], string='Weather Condition')
    temperature = fields.Float(string='Temperature (°C)')
    humidity = fields.Float(string='Humidity (%)')
    
    # Survey Data
    site_features = fields.Html(string='Site Features')
    observations = fields.Html(string='Observations')
    measurements = fields.Html(string='Key Measurements')
    constraints = fields.Html(string='Site Constraints')
    recommendations = fields.Html(string='Recommendations')
    
    # Technical Data
    elevation_data = fields.Text(string='Elevation Data')
    soil_conditions = fields.Text(string='Soil Conditions')
    ground_water = fields.Text(string='Ground Water Details')
    existing_structures = fields.Text(string='Existing Structures')
    
    # Utilities Information
    water_supply = fields.Text(string='Water Supply')
    electricity = fields.Text(string='Electricity')
    drainage = fields.Text(string='Drainage')
    telecom = fields.Text(string='Telecommunications')
    
    # Environmental Factors
    vegetation = fields.Text(string='Vegetation')
    water_bodies = fields.Text(string='Water Bodies')
    special_features = fields.Text(string='Special Features')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved')
    ], string='Status', default='draft', tracking=True)
    
    # Attachments
    attachment_count = fields.Integer(compute='_compute_attachment_count', store=True)
    
    # Coordinates
    latitude = fields.Float(string='Latitude', digits=(16, 8))
    longitude = fields.Float(string='Longitude', digits=(16, 8))
    
    # Survey Report
    report_generated = fields.Boolean(string='Report Generated', default=False)
    report_date = fields.Date(string='Report Date')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('architect.survey')
        return super().create(vals_list)
    
    @api.depends('message_attachment_count')
    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'architect.survey'),
                ('res_id', '=', record.id)
            ])
    
    def action_start_survey(self):
        self.ensure_one()
        if not self.surveyor_id:
            raise ValidationError(_("Please assign a lead surveyor before starting."))
        self.write({'state': 'in_progress'})
        self.message_post(body=_("Survey started."))
    
    def action_complete_survey(self):
        self.ensure_one()
        self.write({
            'state': 'completed',
            'report_generated': True,
            'report_date': fields.Date.today()
        })
        self.message_post(body=_("Survey completed."))
    
    def action_review_survey(self):
        self.ensure_one()
        self.write({'state': 'reviewed'})
        self.message_post(body=_("Survey reviewed."))
    
    def action_approve_survey(self):
        self.ensure_one()
        self.write({'state': 'approved'})
        self.message_post(body=_("Survey approved."))
    
    def action_generate_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_name': 'avf_architect.report_survey_template',
            'report_type': 'qweb-pdf',
            'data': {'survey_id': self.id}
        }


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
