
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AVFRateSchedule(models.Model):
    _name = 'avf.rate.schedule'
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
    rate_item_ids = fields.One2many('avf.rate.schedule.line', 'schedule_id', string='Rate Items')

    # Approval
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Date(string='Approval Date')
    approval_reference = fields.Char(string='Approval Reference')

    # Additional Information
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    version = fields.Char(string='Version', default='1.0')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('superseded', 'Superseded')
    ], string='Status', default='draft')

    def action_activate(self):
        """Activate the rate schedule"""
        self.ensure_one()
        self.state = 'active'
        self.message_post(body=_("Rate schedule activated."))

    def action_expire(self):
        """Mark rate schedule as expired"""
        self.ensure_one()
        self.state = 'expired'
        self.message_post(body=_("Rate schedule marked as expired."))

class AVFRateScheduleLine(models.Model):
    _name = 'avf.rate.schedule.line'
    _description = 'Rate Schedule Line'
    _order = 'item_code, description'

    schedule_id = fields.Many2one('avf.rate.schedule', string='Rate Schedule', required=True, ondelete='cascade')
    item_code = fields.Char(string='Item Code', required=True)
    description = fields.Text(string='Description', required=True)

    # Classification
    category = fields.Selection([
        ('earthwork', 'Earthwork'),
        ('concrete', 'Concrete Work'),
        ('masonry', 'Masonry'),
        ('steel', 'Steel Work'),
        ('carpentry', 'Carpentry'),
        ('flooring', 'Flooring'),
        ('roofing', 'Roofing'),
        ('plastering', 'Plastering'),
        ('painting', 'Painting'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('hvac', 'HVAC'),
        ('finishing', 'Finishing'),
        ('other', 'Other')
    ], string='Category', required=True)

    subcategory = fields.Char(string='Subcategory')

    # Rate Information
    unit = fields.Char(string='Unit', required=True)
    rate = fields.Float(string='Rate', required=True, digits=(12, 2))
    material_cost = fields.Float(string='Material Cost', digits=(12, 2))
    labor_cost = fields.Float(string='Labor Cost', digits=(12, 2))
    equipment_cost = fields.Float(string='Equipment Cost', digits=(12, 2))
    overhead_percentage = fields.Float(string='Overhead %', default=10.0)
    profit_percentage = fields.Float(string='Profit %', default=10.0)

    # Specifications
    specifications = fields.Text(string='Specifications')
    includes = fields.Text(string='Includes')
    excludes = fields.Text(string='Excludes')

    # Additional fields
    min_quantity = fields.Float(string='Minimum Quantity')
    max_quantity = fields.Float(string='Maximum Quantity')
    lead_time = fields.Integer(string='Lead Time (Days)')
    
    active = fields.Boolean(default=True)
    sequence = fields.Integer(string='Sequence', default=10)

    @api.depends('material_cost', 'labor_cost', 'equipment_cost', 'overhead_percentage', 'profit_percentage')
    def _compute_total_rate(self):
        """Compute total rate from components"""
        for line in self:
            base_cost = line.material_cost + line.labor_cost + line.equipment_cost
            overhead = base_cost * (line.overhead_percentage / 100)
            profit = (base_cost + overhead) * (line.profit_percentage / 100)
            line.rate = base_cost + overhead + profit

class ArchitectRateSchedule(models.Model):
    _name = 'architect.rate.schedule'
    _description = 'Architect Rate Schedule'
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

class ArchitectRateItem(models.Model):
    _name = 'architect.rate.item'
    _description = 'Architect Rate Item'

    schedule_id = fields.Many2one('architect.rate.schedule', string='Rate Schedule', required=True, ondelete='cascade')
    item_code = fields.Char(string='Item Code', required=True)
    description = fields.Text(string='Description', required=True)
    unit = fields.Char(string='Unit', required=True)
    rate = fields.Float(string='Rate', required=True, digits=(12, 2))
    category = fields.Char(string='Category')
    active = fields.Boolean(default=True)
