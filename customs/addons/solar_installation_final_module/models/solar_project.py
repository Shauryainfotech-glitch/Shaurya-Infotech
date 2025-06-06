# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


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
        default=lambda self: self.env['ir.sequence'].next_by_code('solar.project') or "New"
    )
    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        # domain="[('customer_rank', '>', 0)]",
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

    # Relationship to Site Survey
    survey_id = fields.Many2one(
        comodel_name="solar.site.survey",
        string="Site Survey",
        ondelete="set null",
        tracking=True,
        help="Linked site survey for this project"
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

    # Miscellaneous
    notes = fields.Text(string="Internal Notes")
    description = fields.Html(string="Project Description")

    @api.depends('quote_ids', 'quote_ids.total_amount', 'quote_ids.state')
    def _compute_current_quote(self):
        """
        Compute the current active quote:
          1. If any accepted, pick most recent accepted by quote_date.
          2. Otherwise pick latest by quote_date.
          3. If none exist, False.
        """
        for rec in self:
            accepted = rec.quote_ids.filtered(lambda q: q.state == 'accepted')
            if accepted:
                rec.current_quote_id = accepted.sorted(key='quote_date', reverse=True)[0]
            else:
                if rec.quote_ids:
                    rec.current_quote_id = rec.quote_ids.sorted(key='quote_date', reverse=True)[0]
                else:
                    rec.current_quote_id = False

    @api.depends('schedule_ids.start_datetime', 'schedule_ids.end_datetime')
    def _compute_schedule_dates(self):
        """
        Earliest planned start and latest planned end from schedules.
        """
        for rec in self:
            dates = rec.schedule_ids.mapped('start_datetime')
            ends = rec.schedule_ids.mapped('end_datetime')
            rec.scheduled_start_date = min(dates).date() if dates else False
            rec.scheduled_end_date = max(ends).date() if ends else False

    @api.depends('quote_ids', 'quote_ids.total_amount')
    def _compute_total_quote_amount(self):
        """
        Sum of all quote total_amounts (including drafts, sent, accepted).
        """
        for rec in self:
            rec.total_quote_amount = sum(rec.quote_ids.mapped('total_amount')) if rec.quote_ids else 0.0

    @api.depends('product_line_ids', 'product_line_ids.subtotal')
    def _compute_total_cost(self):
        """
        Sum of all BOM line subtotals (manual or standard cost).
        """
        for rec in self:
            rec.total_cost = sum(rec.product_line_ids.mapped('subtotal')) if rec.product_line_ids else 0.0

    @api.depends('product_line_ids')
    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_line_ids)

    @api.depends('schedule_ids')
    def _compute_schedule_count(self):
        for rec in self:
            rec.schedule_count = len(rec.schedule_ids)

    @api.depends('schedule_ids.team_id')
    def _compute_assigned_teams(self):
        for rec in self:
            rec.team_ids = rec.schedule_ids.mapped('team_id')
