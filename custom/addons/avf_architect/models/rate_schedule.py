# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AvfRateSchedule(models.Model):
    _name = 'avf.rate.schedule'
    _description = 'Rate Schedule for Government Projects'
    _order = 'effective_date desc'

    name = fields.Char(string='Rate Schedule Name', required=True)
    code = fields.Char(string='Schedule Code', required=True)
    description = fields.Text(string='Description')

    # Dates
    effective_date = fields.Date(string='Effective Date', required=True, default=fields.Date.today)
    expiry_date = fields.Date(string='Expiry Date')

    # Government details
    government_agency = fields.Char(string='Government Agency')
    notification_number = fields.Char(string='Notification Number')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

    # Rate lines
    line_ids = fields.One2many('avf.rate.schedule.line', 'schedule_id', string='Rate Lines')

    # Currency
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                default=lambda self: self.env.company.currency_id)

    # Approval
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Date(string='Approval Date')

    @api.constrains('effective_date', 'expiry_date')
    def _check_dates(self):
        for record in self:
            if record.expiry_date and record.effective_date > record.expiry_date:
                raise ValidationError(_('Effective date cannot be later than expiry date.'))

    def action_activate(self):
        self.state = 'active'
        self.approval_date = fields.Date.today()
        self.approved_by = self.env.user


class AvfRateScheduleLine(models.Model):
    _name = 'avf.rate.schedule.line'
    _description = 'Rate Schedule Lines'
    _order = 'sequence, item_code'

    schedule_id = fields.Many2one('avf.rate.schedule', string='Rate Schedule', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    # Item details
    item_code = fields.Char(string='Item Code', required=True)
    item_description = fields.Text(string='Item Description', required=True)
    unit_of_measure = fields.Char(string='Unit of Measure', required=True)

    # Rates
    base_rate = fields.Float(string='Base Rate', required=True)
    current_rate = fields.Float(string='Current Rate', required=True)

    # Classification
    category = fields.Selection([
        ('labour', 'Labour'),
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('overhead', 'Overhead'),
        ('miscellaneous', 'Miscellaneous')
    ], string='Category', required=True)

    # Additional details
    specifications = fields.Text(string='Specifications')
    remarks = fields.Text(string='Remarks')

    # Status
    active = fields.Boolean(string='Active', default=True)

    @api.constrains('base_rate', 'current_rate')
    def _check_rates(self):
        for record in self:
            if record.base_rate < 0 or record.current_rate < 0:
                raise ValidationError(_('Rates cannot be negative.'))