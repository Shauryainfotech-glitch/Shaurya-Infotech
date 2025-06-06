# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class ArchitectDPR(models.Model):
    _name = 'architect.dpr'
    _description = 'Detailed Project Report (DPR)'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='DPR Name', required=True)
    code = fields.Char(string='DPR Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    dpr_code = fields.Char(string='DPR Code Number', help='Official DPR code from department')

    project_id = fields.Many2one('architect.project', string='Project', required=True)

    dpr_type = fields.Selection([
        ('feasibility', 'Feasibility Study'),
        ('detailed', 'Detailed Project Report'),
        ('revised', 'Revised DPR'),
        ('supplementary', 'Supplementary DPR')
    ], string='DPR Type', required=True, default='detailed')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    department = fields.Char(string='Department')
    estimated_cost = fields.Monetary(string='Estimated Cost', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)

    submission_date = fields.Date(string='Submission Date')
    approval_date = fields.Date(string='Approval Date')

    description = fields.Text(string='Description')
    objectives = fields.Text(string='Project Objectives')
    scope_of_work = fields.Text(string='Scope of Work')

    technical_specifications = fields.Text(string='Technical Specifications')
    environmental_impact = fields.Text(string='Environmental Impact Assessment')

    # Financial breakdown
    land_cost = fields.Monetary(string='Land Cost', currency_field='currency_id')
    construction_cost = fields.Monetary(string='Construction Cost', currency_field='currency_id')
    equipment_cost = fields.Monetary(string='Equipment Cost', currency_field='currency_id')
    contingency_cost = fields.Monetary(string='Contingency Cost', currency_field='currency_id')

    user_id = fields.Many2one('res.users', string='Responsible User', 
                              default=lambda self: self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'dpr_code' not in vals or not vals['dpr_code']:
                vals['dpr_code'] = self.env['ir.sequence'].next_by_code('architect.dpr') or 'New'
        return super(ArchitectDPR, self).create(vals_list)

    @api.depends('land_cost', 'construction_cost', 'equipment_cost', 'contingency_cost')
    def _compute_total_cost(self):
        for record in self:
            record.estimated_cost = (record.land_cost + record.construction_cost + 
                                   record.equipment_cost + record.contingency_cost)

    def action_submit_for_review(self):
        self.state = 'under_review'
        self.submission_date = fields.Date.today()

    def action_approve(self):
        self.state = 'approved'
        self.approval_date = fields.Date.today()

    def action_reject(self):
        self.state = 'rejected'

    def action_reset_to_draft(self):
        self.state = 'draft'

class DPRSection(models.Model):
    _name = 'architect.dpr.section'
    _description = 'DPR Section'
    _order = 'sequence'

    name = fields.Char(string='Section Name', required=True)
    dpr_id = fields.Many2one('architect.dpr', string='DPR', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    content = fields.Html(string='Content')
    is_mandatory = fields.Boolean(string='Mandatory Section', default=True)
    template_content = fields.Html(string='Template Content')

    # AI Features
    ai_generated = fields.Boolean(string='AI Generated')
    ai_confidence = fields.Float(string='AI Confidence Score')


class DPRTemplate(models.Model):
    _name = 'architect.dpr.template'
    _description = 'DPR Template'

    name = fields.Char(string='Template Name', required=True)
    description = fields.Text(string='Description')
    project_type = fields.Selection([
        ('architectural', 'Architectural'),
        ('infrastructure', 'Infrastructure'),
        ('urban_planning', 'Urban Planning'),
        ('ecotourism', 'Ecotourism')
    ], string='Project Type')

    department = fields.Char(string='Department/Ministry')
    template_sections = fields.One2many('architect.dpr.template.section', 'template_id', string='Template Sections')

    active = fields.Boolean(string='Active', default=True)


class DPRTemplateSection(models.Model):
    _name = 'architect.dpr.template.section'
    _description = 'DPR Template Section'
    _order = 'sequence'

    name = fields.Char(string='Section Name', required=True)
    template_id = fields.Many2one('architect.dpr.template', string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    content_template = fields.Html(string='Content Template')
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
    field_mappings = fields.Text(string='Field Mappings (JSON)')

    # AI Enhancement
    ai_prompt = fields.Text(string='AI Generation Prompt')
    requires_manual_input = fields.Boolean(string='Requires Manual Input')