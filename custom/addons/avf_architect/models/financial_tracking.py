# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AvfFinancialTracking(models.Model):
    _name = 'avf.financial.tracking'
    _description = 'Financial Tracking for Architectural Projects'
    _order = 'date desc'

    name = fields.Char(string='Transaction Reference', required=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    date = fields.Date(string='Transaction Date', required=True, default=fields.Date.today)
    amount = fields.Float(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, 
                                default=lambda self: self.env.company.currency_id)

    # Transaction type
    transaction_type = fields.Selection([
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('budget', 'Budget Allocation'),
        ('payment', 'Payment'),
        ('refund', 'Refund')
    ], string='Transaction Type', required=True)

    # Category
    category_id = fields.Many2one('avf.financial.category', string='Category')
    description = fields.Text(string='Description')

    # Invoice and payment tracking
    invoice_id = fields.Many2one('account.move', string='Related Invoice')
    payment_id = fields.Many2one('account.payment', string='Related Payment')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

    # Approval workflow
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Datetime(string='Approval Date')

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Amount must be greater than zero.'))


class AvfFinancialCategory(models.Model):
    _name = 'avf.financial.category'
    _description = 'Financial Categories'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Category Code', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    # Category type
    category_type = fields.Selection([
        ('revenue', 'Revenue'),
        ('cost', 'Cost'),
        ('expense', 'Expense'),
        ('asset', 'Asset'),
        ('liability', 'Liability')
    ], string='Category Type', required=True)

    # Budget tracking
    budget_limit = fields.Float(string='Budget Limit')
    parent_id = fields.Many2one('avf.financial.category', string='Parent Category')
    child_ids = fields.One2many('avf.financial.category', 'parent_id', string='Sub Categories')