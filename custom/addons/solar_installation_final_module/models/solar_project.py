# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class SolarProject(models.Model):
    _name = "solar.project"
    _description = "Solar Installation Project"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    # Basic Identifiers
    name = fields.Char(
        string="Project Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('solar.project') or "New",
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain=[('is_company', '=', True)],
        tracking=True
    )

    project_name = fields.Char(
        string="Project Name",
        required=True,
        tracking=True
    )

    # Address and Location
    site_address = fields.Char(
        string="Site Address",
        tracking=True
    )
    site_city = fields.Char(string="City")
    site_state = fields.Char(string="State/Province")
    site_zip = fields.Char(string="ZIP")
    site_country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country"
    )
    gps_latitude = fields.Float(string="Latitude", digits=(9, 6))
    gps_longitude = fields.Float(string="Longitude", digits=(9, 6))

    project_id = fields.Many2one(
        comodel_name="solar.project",
        string="Related Project",
        required=True,
        ondelete="cascade",
        tracking=True
    )

    active_id = fields.Many2one('survey.survey', string="Survey", help="Survey related to the project")
    # Relationship to Site Survey
    survey_id = fields.Many2one(
        comodel_name="solar.site.survey",
        string="Site Survey",
        ondelete="set null",
        tracking=True,
        help="Linked site survey for this project",
        context="{'default_project_id': project_id}"  # Corrected context for linking survey_id
    )

    # Relationship to Quotes/Proposals
    quote_ids = fields.One2many(
        comodel_name="solar.quote",
        inverse_name="project_id",
        string="Quotations",
        readonly=True,
        copy=False
    )
    current_quote_id = fields.Many2one(
        comodel_name="solar.quote",
        string="Current Active Quote",
        compute="_compute_current_quote",
        store=True
    )

    # Relationship to Installation Schedule
    schedule_ids = fields.One2many(
        comodel_name="solar.install.schedule",
        inverse_name="project_id",
        string="Installation Schedules",
        copy=False
    )

    # Relationship to Product BOM Lines
    product_line_ids = fields.One2many(
        comodel_name="solar.project.product.line",
        inverse_name="project_id",
        string="Project Product Lines",
        copy=False
    )

    # Relationship to Installation Teams (computed)
    team_ids = fields.Many2many(
        comodel_name="solar.install.team",
        string="Assigned Teams",
        compute="_compute_assigned_teams",
        store=True
    )

    # Dates and Status
    inquiry_date = fields.Datetime(
        string="Inquiry Date",
        default=fields.Datetime.now,
        readonly=True,
        tracking=True
    )
    scheduled_start_date = fields.Date(
        string="Scheduled Start Date",
        compute="_compute_schedule_dates",
        store=True
    )
    scheduled_end_date = fields.Date(
        string="Scheduled End Date",
        compute="_compute_schedule_dates",
        store=True
    )
    actual_start_date = fields.Date(string="Actual Start Date")
    actual_end_date = fields.Date(string="Actual End Date")
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('surveyed', 'Survey Completed'),
            ('quoted', 'Quotation Sent'),
            ('confirmed', 'Quotation Accepted'),
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string="Project Status",
        default='draft',
        tracking=True
    )

    # Financials
    total_quote_amount = fields.Monetary(
        string="Total Quoted Amount",
        compute="_compute_total_quote_amount",
        store=True
    )
    total_cost = fields.Monetary(
        string="Total Cost",
        compute="_compute_total_cost",
        store=True
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id
    )

    # Computed Counts & Metrics
    product_count = fields.Integer(
        string="Product Lines",
        compute="_compute_product_count",
        help="Number of distinct product lines associated"
    )
    schedule_count = fields.Integer(
        string="Number of Schedules",
        compute="_compute_schedule_count"
    )

    # Additional computed fields for analytics
    progress = fields.Float(
        string="Progress",
        compute="_compute_progress",
        store=True,
        help="Project completion progress in percentage"
    )
    days_to_deadline = fields.Integer(
        string="Days to Deadline",
        compute="_compute_days_to_deadline",
        store=True
    )

    # Miscellaneous
    notes = fields.Text(string="Internal Notes")
    description = fields.Html(string="Project Description")
    related_model = fields.Many2one('related.model', string='Related Model')

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        related="project_id.customer_id",
        readonly=True,
        store=True
    )

    # Method to compute the current active quote
    @api.depends('quote_ids', 'quote_ids.total_amount', 'quote_ids.state')
    def _compute_current_quote(self):
        for rec in self:
            accepted = rec.quote_ids.filtered(lambda q: q.state == 'accepted')
            if accepted:
                rec.current_quote_id = accepted.sorted(key='quote_date', reverse=True)[0]
            else:
                if rec.quote_ids:
                    rec.current_quote_id = rec.quote_ids.sorted(key='quote_date', reverse=True)[0]
                else:
                    rec.current_quote_id = False

    # Constraints
    @api.constrains('scheduled_start_date', 'scheduled_end_date')
    def _check_dates(self):
        for record in self:
            if record.scheduled_start_date and record.scheduled_end_date:
                if record.scheduled_end_date < record.scheduled_start_date:
                    raise ValidationError("End date cannot be before start date!")

    @api.constrains('state')
    def _check_state_transition(self):
        for record in self:
            if record.state == 'in_progress' and not record.schedule_ids:
                raise ValidationError("Cannot start project without scheduling installation!")
            if record.state == 'completed' and not record.actual_end_date:
                raise ValidationError("Please set actual end date before marking project as completed!")

    # Method to compute schedule dates
    @api.depends('schedule_ids.start_datetime', 'schedule_ids.end_datetime')
    def _compute_schedule_dates(self):
        for rec in self:
            dates = rec.schedule_ids.mapped('start_datetime')
            ends = rec.schedule_ids.mapped('end_datetime')
            rec.scheduled_start_date = min(dates).date() if dates else False
            rec.scheduled_end_date = max(ends).date() if ends else False

    # Method to compute the total quoted amount
    @api.depends('quote_ids', 'quote_ids.total_amount')
    def _compute_total_quote_amount(self):
        for rec in self:
            accepted_quotes = rec.quote_ids.filtered(lambda q: q.state == 'accepted')
            rec.total_quote_amount = sum(accepted_quotes.mapped('total_amount')) if accepted_quotes else 0.0

    # Method to compute the total cost
    @api.depends('product_line_ids', 'product_line_ids.subtotal')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.product_line_ids.mapped('subtotal')) if rec.product_line_ids else 0.0

    # Method to compute product count
    @api.depends('product_line_ids')
    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_line_ids)

    # Method to compute schedule count
    @api.depends('schedule_ids')
    def _compute_schedule_count(self):
        for rec in self:
            rec.schedule_count = len(rec.schedule_ids)

    # Method to compute project progress
    @api.depends('state', 'schedule_ids.state')
    def _compute_progress(self):
        state_progress = {
            'draft': 0,
            'surveyed': 20,
            'quoted': 40,
            'confirmed': 60,
            'scheduled': 70,
            'in_progress': 80,
            'completed': 100,
            'cancelled': 0
        }
        for record in self:
            if record.state == 'in_progress' and record.schedule_ids:
                completed_schedules = len(record.schedule_ids.filtered(lambda s: s.state == 'done'))
                total_schedules = len(record.schedule_ids)
                base_progress = state_progress['in_progress']
                additional_progress = (completed_schedules / total_schedules) * 20 if total_schedules else 0
                record.progress = base_progress + additional_progress
            else:
                record.progress = state_progress.get(record.state, 0)

    # Method to compute days to deadline
    @api.depends('scheduled_end_date')
    def _compute_days_to_deadline(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.scheduled_end_date:
                if record.scheduled_end_date > today:
                    record.days_to_deadline = (record.scheduled_end_date - today).days
                else:
                    record.days_to_deadline = 0
            else:
                record.days_to_deadline = 0

    # Method to update project info on customer change
    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.site_address = self.customer_id.street
            self.site_city = self.customer_id.city
            self.site_state = self.customer_id.state_id.name
            self.site_zip = self.customer_id.zip
            self.site_country_id = self.customer_id.country_id
            if not self.project_name:
                self.project_name = f"{self.customer_id.name}'s Solar Installation"

    # Method to compute assigned teams
    @api.depends('schedule_ids.team_id')
    def _compute_assigned_teams(self):
        for rec in self:
            rec.team_ids = rec.schedule_ids.mapped('team_id')

    # Action Methods
    def action_set_to_draft(self):
        self.ensure_one()
        if self.state not in ['cancelled', 'completed']:
            raise UserError("Only cancelled or completed projects can be reset to draft.")
        self.write({'state': 'draft'})

    def action_cancel_project(self):
        self.ensure_one()
        if self.state == 'completed':
            raise UserError("Cannot cancel a completed project.")
        self.write({'state': 'cancelled'})

    def action_mark_completed(self):
        self.ensure_one()
        if not self.actual_end_date:
            self.actual_end_date = fields.Date.context_today(self)
        self.write({'state': 'completed'})

    @api.model
    def create(self, vals):
        if vals.get('related_model'):
            related_record = self.env['related.model'].browse(vals['related_model'])
            if not related_record:
                raise ValidationError('The related model record does not exist!')
        return super(SolarProject, self).create(vals)

    @api.constrains('partner_id')
    def _check_partner(self):
        for record in self:
            if not record.partner_id:
                raise ValidationError("Partner is required for this project!")
