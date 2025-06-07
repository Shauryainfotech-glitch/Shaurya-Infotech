# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class SolarSiteSurvey(models.Model):
    _name = "solar.site.survey"
    _description = "Solar Site Survey"
    _inherit = ['mail.thread']

    name = fields.Char(
        string="Survey Reference",
        required=True,
        copy=False,
        readonly=True,
        # default=lambda self: self.env['ir.sequence'].next_by_code('solar.site.survey') or "New"
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

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Site Details
    site_type = fields.Selection(
        selection=[
            ('rooftop', 'Rooftop'),
            ('ground_mount', 'Ground Mount'),
            ('carport', 'Carport'),
            ('hybrid', 'Hybrid Installation')
        ],
        string="Site Type",
        required=True,
        default='rooftop',
        tracking=True
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

    # Additional Site Details
    site_accessibility = fields.Selection([
        ('easy', 'Easy Access'),
        ('moderate', 'Moderate Access'),
        ('difficult', 'Difficult Access')
    ], string="Site Accessibility", required=True, default='easy')
    
    roof_material = fields.Selection([
        ('asphalt', 'Asphalt Shingle'),
        ('metal', 'Metal'),
        ('tile', 'Tile'),
        ('flat', 'Flat/Built-up'),
        ('other', 'Other')
    ], string="Roof Material")
    
    roof_condition = fields.Selection([
        ('new', 'New/Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor/Needs Replacement')
    ], string="Roof Condition")
    
    roof_age = fields.Integer(string="Roof Age (Years)")
    
    # Recommendations & Analysis
    recommended_capacity_kw = fields.Float(
        string="Recommended System Size (kW)",
        compute="_compute_recommended_capacity",
        store=True
    )
    recommended_products_ids = fields.Many2many(
        comodel_name="solar.product.product",
        string="Recommended Products",
        domain="[('product_type', 'in', ['panel','inverter','battery']), ('active', '=', True)]",
        help="Based on sizing and site conditions"
    )
    
    estimated_annual_production = fields.Float(
        string="Estimated Annual Production (kWh)",
        compute="_compute_estimated_production",
        store=True
    )
    
    estimated_payback_years = fields.Float(
        string="Estimated Payback Period (Years)",
        compute="_compute_payback_period",
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
        readonly=True
    )

    estimated_install_cost = fields.Monetary(
        string="Estimated Installation Cost",
        compute="_compute_estimated_install_cost",
        store=True,
        currency_field='currency_id'
    )
    
    # Attachments and Documentation
    survey_report = fields.Binary(
        string="Survey Report (PDF)",
        attachment=True
    )
    site_photos = fields.Many2many(
        'ir.attachment',
        string="Site Photos",
        domain=[('mimetype', 'ilike', 'image')],
        context={'default_res_model': 'solar.site.survey'}
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default='draft', tracking=True)
    
    notes = fields.Text(string="Survey Notes")
    technical_notes = fields.Text(string="Technical Notes")

    @api.constrains('roof_area_sqft')
    def _check_roof_area(self):
        for record in self:
            if record.roof_area_sqft <= 0:
                raise ValidationError("Roof area must be greater than 0 square feet!")

    @api.constrains('avg_sun_hours')
    def _check_sun_hours(self):
        for record in self:
            if record.avg_sun_hours < 0 or record.avg_sun_hours > 24:
                raise ValidationError("Average sun hours must be between 0 and 24!")

    @api.depends('roof_area_sqft', 'avg_sun_hours', 'roof_orientation', 'nearby_shading_sources')
    def _compute_recommended_capacity(self):
        """Calculate recommended system size based on multiple factors"""
        SQFT_PER_KW = 15.0  # Base square footage needed per kW
        for rec in self:
            if rec.roof_area_sqft and rec.avg_sun_hours:
                # Base calculation
                base_capacity = rec.roof_area_sqft / SQFT_PER_KW
                
                # Apply orientation factor
                orientation_factor = {
                    'south': 1.0,
                    'east': 0.85,
                    'west': 0.85,
                    'north': 0.7,
                    'flat': 0.95
                }.get(rec.roof_orientation, 1.0)
                
                # Calculate final capacity
                rec.recommended_capacity_kw = round(base_capacity * orientation_factor, 2)
            else:
                rec.recommended_capacity_kw = 0.0

    @api.depends('recommended_capacity_kw', 'avg_sun_hours')
    def _compute_estimated_production(self):
        """Calculate estimated annual production in kWh"""
        EFFICIENCY_FACTOR = 0.85  # System efficiency factor
        DAYS_PER_YEAR = 365
        
        for rec in self:
            if rec.recommended_capacity_kw and rec.avg_sun_hours:
                daily_production = (
                    rec.recommended_capacity_kw * 
                    rec.avg_sun_hours * 
                    EFFICIENCY_FACTOR
                )
                rec.estimated_annual_production = round(
                    daily_production * DAYS_PER_YEAR, 2
                )
            else:
                rec.estimated_annual_production = 0.0

    @api.depends('recommended_capacity_kw', 'site_type')
    def _compute_estimated_install_cost(self):
        """Calculate estimated installation cost based on system size and type"""
        base_rate_per_kw = {
            'rooftop': 1000.0,
            'ground_mount': 1200.0,
            'carport': 1500.0,
            'hybrid': 1300.0
        }
        
        for rec in self:
            rate = base_rate_per_kw.get(rec.site_type, 1000.0)
            rec.estimated_install_cost = rec.recommended_capacity_kw * rate

    @api.depends('estimated_install_cost', 'estimated_annual_production')
    def _compute_payback_period(self):
        """Calculate estimated payback period in years"""
        AVG_ELECTRICITY_RATE = 0.12  # Average electricity rate per kWh
        
        for rec in self:
            if rec.estimated_annual_production and rec.estimated_install_cost:
                annual_savings = rec.estimated_annual_production * AVG_ELECTRICITY_RATE
                if annual_savings > 0:
                    rec.estimated_payback_years = round(
                        rec.estimated_install_cost / annual_savings, 1
                    )
                else:
                    rec.estimated_payback_years = 0.0
            else:
                rec.estimated_payback_years = 0.0

    def action_start_survey(self):
        """Start the survey process"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Survey can only be started from draft state.")
        self.write({'state': 'in_progress'})

    def action_submit_for_review(self):
        """Submit survey for review"""
        self.ensure_one()
        if not self.survey_report:
            raise UserError("Please attach the survey report before submitting for review.")
        self.write({'state': 'review'})

    def action_complete_survey(self):
        """Mark survey as completed"""
        self.ensure_one()
        if self.state not in ['review', 'in_progress']:
            raise UserError("Only surveys under review or in progress can be completed.")
        self.write({'state': 'completed'})
        if self.project_id.state == 'draft':
            self.project_id.write({'state': 'surveyed'})

    def action_cancel_survey(self):
        """Cancel the survey"""
        self.ensure_one()
        if self.state == 'completed':
            raise UserError("Cannot cancel a completed survey.")
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        """Reset survey to draft state"""
        self.ensure_one()
        if self.state not in ['cancelled']:
            raise UserError("Only cancelled surveys can be reset to draft.")
        self.write({'state': 'draft'})
