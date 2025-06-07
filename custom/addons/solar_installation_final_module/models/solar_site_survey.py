# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class SolarSiteSurvey(models.Model):
    _name = "solar.site.survey"
    _description = "Solar Site Survey"
    _inherit = ['mail.thread']

    name = fields.Char(
        string="Survey Reference",
        required=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('solar.site.survey') or "New"
    )
    project_id = fields.Many2one(
        comodel_name="solar.project",
        string="Related Project",
        required=True,
        ondelete="cascade",
        tracking=True
    )
    survey_date = fields.Datetime(
        string="Survey Date",
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    surveyed_by = fields.Many2one(
        comodel_name="hr.employee",
        string="Surveyed By",
        domain="[('active', '=', True)]"
    )

    # Site Details
    site_type = fields.Selection(
        selection=[
            ('rooftop', 'Rooftop'),
            ('ground_mount', 'Ground Mount'),
            ('carport', 'Carport'),
        ],
        string="Site Type",
        required=True,
        default='rooftop'
    )
    roof_area_sqft = fields.Float(string="Roof Area (sq. ft.)")
    roof_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
            ('flat', 'Flat')
        ],
        string="Roof Orientation"
    )
    roof_pitch_degree = fields.Float(string="Roof Pitch (°)")
    nearby_shading_sources = fields.Text(string="Shading Observations")

    # Electrical Infrastructure
    main_panel_capacity_kw = fields.Float(string="Main Panel Capacity (kW)")
    conduit_conditions = fields.Text(string="Conduit / Wiring Condition")
    inverter_location = fields.Char(string="Proposed Inverter Location")

    # Environmental Conditions
    avg_sun_hours = fields.Float(
        string="Estimated Sunlight Hours (per day)",
        help="Used for sizing the system"
    )
    soil_condition = fields.Selection(
        selection=[
            ('loamy', 'Loamy'),
            ('sandy', 'Sandy'),
            ('clay', 'Clay'),
            ('rocky', 'Rocky'),
        ],
        string="Soil Condition (Ground Mount Only)"
    )
    ground_mount_depth = fields.Float(string="In-Ground Mount Depth (ft)")

    # Recommendations & Outcomes
    recommended_capacity_kw = fields.Float(
        string="Recommended System Size (kW)",
        compute="_compute_recommended_capacity",
        store=True
    )
    recommended_products_ids = fields.Many2many(
        comodel_name="solar.product.product",
        string="Recommended Products",
        domain="[('product_type', 'in', ['panel','inverter','battery'])]",
        help="Based on sizing and site conditions"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
        readonly=True,
    )

    estimated_install_cost = fields.Monetary(
        string="Estimated Installation Cost",
        compute="_compute_estimated_install_cost",
        store=True,
        currency_field='currency_id',
    )
    survey_report = fields.Binary(
        string="Survey Report (PDF)",
        attachment=True
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        string="Status",
        default='draft',
        tracking=True
    )
    notes = fields.Text(string="Survey Notes")

    @api.depends('roof_area_sqft', 'avg_sun_hours')
    def _compute_recommended_capacity(self):
        for rec in self:
            if rec.roof_area_sqft and rec.avg_sun_hours:
                installable_kw = rec.roof_area_sqft / 15.0
                rec.recommended_capacity_kw = round(installable_kw, 2)
            else:
                rec.recommended_capacity_kw = 0.0

    @api.depends('recommended_capacity_kw')
    def _compute_estimated_install_cost(self):
        RATE_PER_KW = 1000.0
        for rec in self:
            rec.estimated_install_cost = rec.recommended_capacity_kw * RATE_PER_KW