# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


class SolarQuote(models.Model):
    _name = "solar.quote"
    _description = "Solar Installation Quote/Proposal"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "quote_date desc, id desc"

    quote_number = fields.Char(
        string="Quote Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('solar.quote') or "New"
    )
    project_id = fields.Many2one(
        comodel_name="solar.project",
        string="Related Project",
        required=True,
        ondelete="cascade",
        tracking=True
    )
    quote_date = fields.Date(
        string="Quote Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    validity_days = fields.Integer(
        string="Validity (Days)",
        default=30,
        help="Number of days until the quote expires"
    )
    expiration_date = fields.Date(
        string="Expiration Date",
        compute="_compute_expiration_date",
        inverse="_inverse_expiration_date",
        store=True,
        tracking=True
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        related="project_id.customer_id",
        readonly=True,
        store=True
    )

    # Quotation Lines
    quote_line_ids = fields.One2many(
        comodel_name="solar.quote.line",
        inverse_name="quote_id",
        string="Quote Lines",
        copy=True
    )

    # Totals & Taxes
    untaxed_amount = fields.Monetary(
        string="Untaxed Amount",
        compute="_compute_amounts",
        store=True
    )
    tax_amount = fields.Monetary(
        string="Total Taxes",
        compute="_compute_amounts",
        store=True
    )
    total_amount = fields.Monetary(
        string="Total Amount",
        compute="_compute_amounts",
        store=True
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id
    )

    # Status & Workflow
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
            ('expired', 'Expired')
        ],
        string="Quote Status",
        default='draft',
        tracking=True
    )
    notes = fields.Text(string="Customer Notes")
    internal_notes = fields.Text(string="Internal Notes")

    @api.depends('quote_date', 'validity_days')
    def _compute_expiration_date(self):
        for rec in self:
            rec.expiration_date = rec.quote_date + timedelta(days=rec.validity_days)

    def _inverse_expiration_date(self):
        for rec in self:
            if rec.expiration_date and rec.quote_date:
                delta = rec.expiration_date - rec.quote_date
                rec.validity_days = delta.days

    @api.depends('quote_line_ids.price_subtotal')
    def _compute_amounts(self):
        TAX_RATE = 0.18  # 18% GST placeholder
        for rec in self:
            untaxed = sum(rec.quote_line_ids.mapped('price_subtotal'))
            tax = untaxed * TAX_RATE
            rec.untaxed_amount = untaxed
            rec.tax_amount = tax
            rec.total_amount = untaxed + tax

    @api.constrains('quote_date', 'expiration_date')
    def _check_dates(self):
        for rec in self:
            if rec.expiration_date < rec.quote_date:
                raise models.ValidationError("Expiration date cannot be before Quote date.")

    def action_send(self):
        for rec in self:
            if not rec.quote_line_ids:
                raise models.UserError("Cannot send a quote without any line items.")
            rec.state = 'sent'

    def action_accept(self):
        for rec in self:
            if rec.state != 'sent':
                raise models.UserError("Only sent quotes can be accepted.")
            if rec.expiration_date < fields.Date.context_today(rec):
                raise models.UserError("Cannot accept an expired quote.")
            rec.state = 'accepted'
            rec.project_id.state = 'confirmed'

    def action_refuse(self):
        for rec in self:
            if rec.state not in ['sent', 'draft']:
                raise models.UserError("Only draft or sent quotes can be refused.")
            rec.state = 'refused'
            rec.project_id.state = 'draft'