# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class RateSchedule(models.Model):
    _name = 'avf.rate.schedule'
    _description = 'Rate Schedule Management'
    _rec_name = 'name'

    name = fields.Char(string='Rate Schedule Name', required=True)
    schedule_type = fields.Selection([
        ('dsr', 'District Schedule of Rates'),
        ('ssr', 'State Schedule of Rates'),
        ('custom', 'Custom Rates')
    ], string='Schedule Type', required=True)
    state = fields.Char(string='State')
    district = fields.Char(string='District')
    effective_date = fields.Date(string='Effective Date', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    
    rate_line_ids = fields.One2many('avf.rate.schedule.line', 'schedule_id', string='Rate Lines')

class RateScheduleLine(models.Model):
    _name = 'avf.rate.schedule.line'
    _description = 'Rate Schedule Line'
    
    schedule_id = fields.Many2one('avf.rate.schedule', string='Rate Schedule', required=True)
    item_code = fields.Char(string='Item Code', required=True)
    description = fields.Text(string='Description', required=True)
    unit = fields.Char(string='Unit', required=True)
    rate = fields.Float(string='Rate', required=True)
    labour_rate = fields.Float(string='Labour Rate')
    material_rate = fields.Float(string='Material Rate')

class ArchitectRateSchedule(models.Model):
    _name = 'architect.rate.schedule'
    _description = 'Rate Schedule (DSR/SSR)'
    _order = 'state_id, district, name'

    name = fields.Char(string='Schedule Name', required=True)
    code = fields.Char(string='Schedule Code', required=True)
    schedule_type = fields.Selection([
        ('dsr', 'District Schedule of Rates (DSR)'),
        ('ssr', 'State Schedule of Rates (SSR)'),
        ('market', 'Market Rate'),
        ('custom', 'Custom Rate')
    ], string='Schedule Type', required=True, default='dsr')

    # Location
    state_id = fields.Many2one('res.country.state', string='State', required=True)
    district = fields.Char(string='District')

    # Validity
    valid_from = fields.Date(string='Valid From', required=True)
    valid_to = fields.Date(string='Valid To')
    active = fields.Boolean(string='Active', default=True)

    # Rate Items
    rate_item_ids = fields.One2many('architect.rate.item', 'schedule_id', string='Rate Items')

    # Approval
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Date(string='Approval Date')
    approval_reference = fields.Char(string='Approval Reference')

    # Metadata
    version = fields.Char(string='Version', default='1.0')
    source_document = fields.Binary(string='Source Document')
    source_filename = fields.Char(string='Source Filename')
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

class ArchitectRateItem(models.Model):
    _name = 'architect.rate.item'
    _description = 'Rate Schedule Item'

    schedule_id = fields.Many2one('architect.rate.schedule', string='Rate Schedule', required=True, ondelete='cascade')
    name = fields.Char(string='Item Description', required=True)
    code = fields.Char(string='Item Code', required=True)
    category = fields.Selection([
        ('material', 'Material'),
        ('labor', 'Labor'),
        ('equipment', 'Equipment'),
        ('transport', 'Transport'),
        ('overhead', 'Overhead')
    ], string='Category', required=True)

    unit = fields.Char(string='Unit of Measurement', required=True)
    rate = fields.Float(string='Rate', required=True, digits=(16, 2))
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Analysis
    basic_rate = fields.Float(string='Basic Rate', digits=(16, 2))
    overhead_percentage = fields.Float(string='Overhead %')
    profit_percentage = fields.Float(string='Profit %')
    tax_percentage = fields.Float(string='Tax %')

    # Additional Info
    specification = fields.Text(string='Specification')
    remarks = fields.Text(string='Remarks')
    active = fields.Boolean(string='Active', default=True)

class ArchitectCostEstimate(models.Model):
    _name = 'architect.cost.estimate'
    _description = 'Cost Estimate'

    name = fields.Char(string='Estimate Name', required=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    schedule_id = fields.Many2one('architect.rate.schedule', string='Rate Schedule')

    # Estimate Details
    estimate_date = fields.Date(string='Estimate Date', default=fields.Date.today)
    prepared_by = fields.Many2one('res.users', string='Prepared By', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By')

    # Totals
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_totals', store=True)
    overhead_amount = fields.Monetary(string='Overhead', compute='_compute_totals', store=True)
    profit_amount = fields.Monetary(string='Profit', compute='_compute_totals', store=True)
    tax_amount = fields.Monetary(string='Tax', compute='_compute_totals', store=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_totals', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')

    @api.depends('schedule_id')
    def _compute_totals(self):
        for estimate in self:
            estimate.subtotal = 0.0
            estimate.overhead_amount = 0.0
            estimate.profit_amount = 0.0
            estimate.tax_amount = 0.0
            estimate.total_amount = 0.0