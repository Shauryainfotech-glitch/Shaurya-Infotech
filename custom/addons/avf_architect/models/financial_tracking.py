# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AVFFinancialTracking(models.Model):
    _name = 'avf.financial.tracking'
    _description = 'Financial Tracking for Projects'
    _rec_name = 'name'
    _order = 'date desc'

    name = fields.Char(string='Description', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)

    # Transaction Details
    transaction_type = fields.Selection([
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('advance', 'Advance Payment'),
        ('milestone', 'Milestone Payment'),
        ('retention', 'Retention Release'),
        ('adjustment', 'Adjustment')
    ], string='Transaction Type', required=True)

    category = fields.Selection([
        ('material', 'Material Cost'),
        ('labor', 'Labor Cost'),
        ('equipment', 'Equipment Cost'),
        ('subcontractor', 'Subcontractor Payment'),
        ('overhead', 'Overhead'),
        ('professional_fee', 'Professional Fee'),
        ('permit_fee', 'Permit & License Fee'),
        ('other', 'Other')
    ], string='Category')

    # Financial Information
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)

    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    reference = fields.Char(string='Reference/Invoice No.')

    # Payment Information
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('card', 'Card Payment')
    ], string='Payment Method')

    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], string='Payment Status', default='pending')

    # Vendor/Client Information
    partner_id = fields.Many2one('res.partner', string='Vendor/Client')

    # Additional Information
    notes = fields.Text(string='Notes')
    tax_amount = fields.Monetary(string='Tax Amount', currency_field='currency_id')
    net_amount = fields.Monetary(string='Net Amount', compute='_compute_net_amount', 
                                store=True, currency_field='currency_id')

    # Approval
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Date(string='Approval Date')

    # Files
    document_ids = fields.Many2many('ir.attachment', string='Supporting Documents')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

    @api.depends('amount', 'tax_amount')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.amount + record.tax_amount

    def action_submit(self):
        """Submit for approval"""
        self.ensure_one()
        self.state = 'submitted'

    def action_approve(self):
        """Approve transaction"""
        self.ensure_one()
        self.state = 'approved'
        self.approved_by = self.env.user
        self.approval_date = fields.Date.today()

    def action_mark_paid(self):
        """Mark as paid"""
        self.ensure_one()
        self.state = 'paid'
        self.payment_status = 'paid'

    def action_cancel(self):
        """Cancel transaction"""
        self.ensure_one()
        self.state = 'cancelled'
        self.payment_status = 'cancelled'

class FinancialCategory(models.Model):
    _name = 'avf.financial.category'
    _description = 'Financial Category'

    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Category Code')
    parent_id = fields.Many2one('avf.financial.category', string='Parent Category')
    child_ids = fields.One2many('avf.financial.category', 'parent_id', string='Child Categories')

    category_type = fields.Selection([
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('both', 'Both')
    ], string='Category Type', default='both')

    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

class ProjectBudget(models.Model):
    _name = 'avf.project.budget'
    _description = 'Project Budget'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    budget_category_id = fields.Many2one('avf.financial.category', string='Budget Category', required=True)

    budgeted_amount = fields.Monetary(string='Budgeted Amount', currency_field='currency_id')
    actual_amount = fields.Monetary(string='Actual Amount', compute='_compute_actual_amount', 
                                   store=True, currency_field='currency_id')
    variance = fields.Monetary(string='Variance', compute='_compute_variance', 
                              store=True, currency_field='currency_id')
    variance_percentage = fields.Float(string='Variance %', compute='_compute_variance_percentage', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 default=lambda self: self.env.company.currency_id)

    notes = fields.Text(string='Notes')

    @api.depends('project_id', 'budget_category_id')
    def _compute_actual_amount(self):
        for budget in self:
            financial_records = self.env['avf.financial.tracking'].search([
                ('project_id', '=', budget.project_id.id),
                ('category', '=', budget.budget_category_id.name.lower()),
                ('state', '=', 'approved')
            ])
            budget.actual_amount = sum(financial_records.mapped('amount'))

    @api.depends('budgeted_amount', 'actual_amount')
    def _compute_variance(self):
        for budget in self:
            budget.variance = budget.budgeted_amount - budget.actual_amount

    @api.depends('budgeted_amount', 'variance')
    def _compute_variance_percentage(self):
        for budget in self:
            if budget.budgeted_amount:
                budget.variance_percentage = (budget.variance / budget.budgeted_amount) * 100
            else:
                budget.variance_percentage = 0.0