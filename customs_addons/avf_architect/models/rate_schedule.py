# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class ArchitectRateSchedule(models.Model):
    _name = 'architect.rate.schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Rate Schedule (DSR/SSR)'
    _order = 'effective_date desc, state_id, district'

    name = fields.Char(string='Rate Schedule Name', required=True, tracking=True)
    #code = fields.Char(string='Schedule Code', required=True)
    code = fields.Char(
        string='Schedule Code',
        required=True,
        copy=False,
        readonly=True,
        tracking=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('architect.rate.schedule') or 'new'
    )
    quality_rating = fields.Float(string="Quality Rating")
    schedule_type = fields.Selection([
        ('dsr', 'District Schedule of Rates (DSR)'),
        ('ssr', 'State Schedule of Rates (SSR)'),
        ('market', 'Market Rate'),
        ('custom', 'Custom Rate')
    ], string='Schedule Type', required=True, default='dsr')

    state_id = fields.Many2one('res.country.state', string='State', required=True)
    district = fields.Char(string='District')
    region = fields.Char(string='Region/Circle')

    effective_date = fields.Date(string='Effective Date', required=True, default=fields.Date.today)
    expiry_date = fields.Date(string='Expiry Date')
    version = fields.Char(string='Version', required=True, default='1.0')

    issuing_authority = fields.Char(string='Issuing Authority', required=True)
    approval_reference = fields.Char(string='Approval Reference')
    approval_date = fields.Date(string='Approval Date')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id, required=True)

    rate_item_ids = fields.One2many('architect.rate.item', 'rate_schedule_id', string='Rate Items')
    item_count = fields.Integer(string='Item Count', compute='_compute_item_count')

    terms_conditions = fields.Html(string='Terms and Conditions')
    special_conditions = fields.Html(string='Special Conditions')
    notes = fields.Html(string='Notes')

    is_official = fields.Boolean(string='Official Government Rate', default=True)
    source_url = fields.Char(string='Source URL')

    last_update_date = fields.Date(string='Last Update Date', default=fields.Date.today)
    price_escalation_factor = fields.Float(string='Price Escalation Factor (%)', default=0.0)

    @api.depends('rate_item_ids')
    def _compute_item_count(self):
        for schedule in self:
            schedule.item_count = len(schedule.rate_item_ids)

    @api.model
    # def create(self, vals):
    #     if 'code' not in vals or not vals['code']:
    #         vals['code'] = self.env['ir.sequence'].next_by_code('architect.rate.schedule') or 'New'
    #     return super().create(vals)

    def action_publish(self):
        self.state = 'published'
        self.message_post(body=_("Rate schedule published."))

    def action_archive(self):
        self.state = 'archived'
        self.message_post(body=_("Rate schedule archived."))

    def action_duplicate_for_new_period(self):
        new_schedule = self.copy({
            'name': f"{self.name} - New Period",
            'effective_date': fields.Date.today(),
            'state': 'draft',
            'version': f"{float(self.version) + 0.1:.1f}"
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'architect.rate.schedule',
            'res_id': new_schedule.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_apply_escalation(self):
        if self.price_escalation_factor > 0:
            for item in self.rate_item_ids:
                item.unit_rate = item.unit_rate * (1 + self.price_escalation_factor / 100)
            self.message_post(body=_(f"Applied {self.price_escalation_factor}% escalation to all items."))


class ArchitectRateItem(models.Model):
    _name = 'architect.rate.item'
    _description = 'Rate Schedule Item'
    _order = 'item_code'

    name = fields.Char(string='Item Description', required=True)
    item_code = fields.Char(string='Item Code', required=True)
    rate_schedule_id = fields.Many2one('architect.rate.schedule', string='Rate Schedule',
                                       required=True, ondelete='cascade')

    category_id = fields.Many2one('architect.rate.category', string='Category')
    subcategory_id = fields.Many2one('architect.rate.subcategory', string='Subcategory')
    work_type = fields.Selection([
        ('civil', 'Civil Work'),
        ('electrical', 'Electrical Work'),
        ('plumbing', 'Plumbing Work'),
        ('hvac', 'HVAC Work'),
        ('structural', 'Structural Work'),
        ('finishing', 'Finishing Work'),
        ('landscape', 'Landscape Work'),
        ('other', 'Other')
    ], string='Work Type', required=True)

    unit_rate = fields.Monetary(string='Unit Rate', currency_field='currency_id', required=True)
    unit_of_measure = fields.Char(string='Unit of Measure', required=True)
    currency_id = fields.Many2one('res.currency', related='rate_schedule_id.currency_id', store=True)

    specification = fields.Html(string='Specification')
    quality_standards = fields.Text(string='Quality Standards')

    component_ids = fields.One2many('architect.rate.component', 'rate_item_id', string='Rate Components')
    is_composite = fields.Boolean(string='Composite Rate', default=False)

    market_rate = fields.Monetary(string='Market Rate', currency_field='currency_id')
    rate_variance = fields.Float(string='Variance (%)', compute='_compute_rate_variance')

    applicable_from = fields.Date(string='Applicable From')
    applicable_to = fields.Date(string='Applicable To')

    notes = fields.Text(string='Notes')
    tags = fields.Char(string='Tags')

    gst_rate = fields.Float(string='GST Rate (%)', default=18.0)
    inclusive_of_gst = fields.Boolean(string='Rate Inclusive of GST', default=False)

    @api.depends('unit_rate', 'market_rate')
    def _compute_rate_variance(self):
        for item in self:
            if item.market_rate and item.market_rate > 0:
                item.rate_variance = ((item.unit_rate - item.market_rate) / item.market_rate) * 100
            else:
                item.rate_variance = 0.0

    @api.onchange('is_composite')
    def _onchange_is_composite(self):
        if not self.is_composite:
            self.component_ids = False


class ArchitectRateComponent(models.Model):
    _name = 'architect.rate.component'
    _description = 'Rate Component'
    _order = 'sequence'

    name = fields.Char(string='Component Description', required=True)
    rate_item_id = fields.Many2one('architect.rate.item', string='Rate Item', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    component_type = fields.Selection([
        ('material', 'Material'),
        ('labour', 'Labour'),
        ('equipment', 'Equipment'),
        ('overhead', 'Overhead'),
        ('profit', 'Profit'),
        ('other', 'Other')
    ], string='Component Type', required=True)

    quantity = fields.Float(string='Quantity', default=1.0)
    unit = fields.Char(string='Unit')
    rate = fields.Monetary(string='Rate', currency_field='currency_id', required=True)
    amount = fields.Monetary(string='Amount', compute='_compute_amount', store=True, currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='rate_item_id.currency_id', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'rate')
    def _compute_amount(self):
        for component in self:
            component.amount = component.quantity * component.rate


class ArchitectRateCategory(models.Model):
    _name = 'architect.rate.category'
    _description = 'Rate Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category Name', required=True)
    #code = fields.Char(string='Category Code', required=True)
    code = fields.Char(
        string='Category Code',
        required=True,
        copy=False,
        readonly=True,
        tracking=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('architect.rate.category') or 'new'
    )

    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    parent_id = fields.Many2one('architect.rate.category', string='Parent Category')
    child_ids = fields.One2many('architect.rate.category', 'parent_id', string='Child Categories')

    active = fields.Boolean(string='Active', default=True)


class ArchitectRateSubcategory(models.Model):
    _name = 'architect.rate.subcategory'
    _description = 'Rate Subcategory'
    _order = 'category_id, sequence, name'

    name = fields.Char(string='Subcategory Name', required=True)
    code = fields.Char(string='Subcategory Code', required=True)
    category_id = fields.Many2one('architect.rate.category', string='Category', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)

    active = fields.Boolean(string='Active', default=True)


class ArchitectEstimation(models.Model):
    _name = 'architect.estimation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Estimation'
    _order = 'create_date desc'

    name = fields.Char(string='Estimation Name', required=True, tracking=True)
    code = fields.Char(string='Estimation Code', required=True, copy=False)
    project_id = fields.Many2one('architect.project', string='Project', required=True)

    rate_schedule_id = fields.Many2one('architect.rate.schedule', string='Rate Schedule', required=True)

    total_area = fields.Float(string='Total Area (sq.ft/sq.m)')
    built_up_area = fields.Float(string='Built-up Area (sq.ft/sq.m)')

    subtotal = fields.Monetary(string='Subtotal', compute='_compute_amounts', store=True, currency_field='currency_id')
    overhead_percentage = fields.Float(string='Overhead (%)', default=10.0)
    overhead_amount = fields.Monetary(string='Overhead Amount', compute='_compute_amounts', store=True,
                                      currency_field='currency_id')
    profit_percentage = fields.Float(string='Profit (%)', default=10.0)
    profit_amount = fields.Monetary(string='Profit Amount', compute='_compute_amounts', store=True,
                                    currency_field='currency_id')
    total_before_tax = fields.Monetary(string='Total Before Tax', compute='_compute_amounts', store=True,
                                       currency_field='currency_id')
    tax_amount = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True,
                                 currency_field='currency_id')
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_amounts', store=True,
                                   currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    estimation_line_ids = fields.One2many('architect.estimation.line', 'estimation_id', string='Estimation Lines')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    estimation_date = fields.Date(string='Estimation Date', default=fields.Date.today)
    validity_date = fields.Date(string='Valid Until')

    assumptions = fields.Html(string='Assumptions')
    exclusions = fields.Html(string='Exclusions')
    notes = fields.Html(string='Notes')

    @api.depends('estimation_line_ids.total_amount', 'overhead_percentage', 'profit_percentage')
    def _compute_amounts(self):
        for estimation in self:
            estimation.subtotal = sum(estimation.estimation_line_ids.mapped('total_amount'))
            estimation.overhead_amount = estimation.subtotal * (estimation.overhead_percentage / 100)
            estimation.profit_amount = estimation.subtotal * (estimation.profit_percentage / 100)
            estimation.total_before_tax = estimation.subtotal + estimation.overhead_amount + estimation.profit_amount
            estimation.tax_amount = estimation.total_before_tax * 0.18
            estimation.total_amount = estimation.total_before_tax + estimation.tax_amount

    @api.model
    def create(self, vals):
        if 'code' not in vals or not vals['code']:
            vals['code'] = self.env['ir.sequence'].next_by_code('architect.estimation') or 'New'
        return super().create(vals)

    def action_submit(self):
        self.state = 'submitted'
        self.message_post(body=_("Estimation submitted for approval."))

    def action_approve(self):
        self.state = 'approved'
        self.message_post(body=_("Estimation approved."))

    def action_reject(self):
        self.state = 'rejected'
        self.message_post(body=_("Estimation rejected."))


class ArchitectEstimationLine(models.Model):
    _name = 'architect.estimation.line'
    _description = 'Estimation Line'
    _order = 'sequence, id'

    estimation_id = fields.Many2one('architect.estimation', string='Estimation', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    rate_item_id = fields.Many2one('architect.rate.item', string='Rate Item', required=True)
    description = fields.Char(string='Description', required=True)

    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    unit = fields.Char(string='Unit', related='rate_item_id.unit_of_measure', readonly=True)
    unit_rate = fields.Monetary(string='Unit Rate', related='rate_item_id.unit_rate', readonly=True,
                                currency_field='currency_id')
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', store=True,
                                   currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='estimation_id.currency_id', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'unit_rate')
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = line.quantity * line.unit_rate

    @api.onchange('rate_item_id')
    def _onchange_rate_item_id(self):
        if self.rate_item_id:
            self.description = self.rate_item_id.name
