# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ArchitectFinancialTracking(models.Model):
    _name = 'architect.financial.tracking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Financial Tracking'
    _order = 'project_id, date desc'

    name = fields.Char(string='Reference', required=True, tracking=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)

    # Financial Details
    transaction_type = fields.Selection([
        ('budget', 'Budget Allocation'),
        ('expense', 'Expense'),
        ('income', 'Income'),
        ('invoice', 'Invoice'),
        ('payment', 'Payment'),
        ('adjustment', 'Adjustment')
    ], string='Transaction Type', required=True)

    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.ref('base.₹')  # Ensure 'base.INR' is the XML ID for INR currency
    )
    # Dates
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    due_date = fields.Date(string='Due Date')

    # Categories
    category_id = fields.Many2one('architect.financial.category', string='Category')
    subcategory_id = fields.Many2one('architect.financial.subcategory', string='Subcategory')

    # Approval fields (removed duplicate)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    approval_notes = fields.Text(string='Approval Notes')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # Related Records
    invoice_id = fields.Many2one('account.move', string='Related Invoice')
    payment_id = fields.Many2one('account.payment', string='Related Payment')

    # Description
    description = fields.Text(string='Description')
    notes = fields.Text(string='Internal Notes')

    # Mail thread fields
    message_follower_ids = fields.One2many('mail.followers', 'res_id', string="Followers")
    activity_ids = fields.One2many('mail.activity', 'res_id', string="Activities")
    message_ids = fields.One2many('mail.message', 'res_id', string="Messages")

    def action_pay(self):
        for record in self:
            record.state = 'paid'

    def action_receive(self):
        for record in self:
            record.state = 'paid'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('architect.financial.tracking')
        return super().create(vals_list)

    def action_submit(self):
        for record in self:
            record.state = 'submitted'

    def action_approve(self):
        for record in self:
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now()
            })

    def action_reject(self):
        for record in self:
            record.state = 'rejected'

    def action_confirm(self):
        self.state = 'confirmed'
        self.message_post(body=_("Financial transaction confirmed."))

    def action_mark_paid(self):
        self.state = 'paid'
        self.message_post(body=_("Transaction marked as paid."))

    def action_cancel(self):
        self.state = 'cancelled'
        self.message_post(body=_("Transaction cancelled."))


class ArchitectFinancialCategory(models.Model):
    _name = 'architect.financial.category'
    _description = 'Financial Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category Name', required=True)
    #code = fields.Char(string='Category Code')
    code = fields.Char(
        string='Category Code',
        required=True,
        copy=False,
        readonly=True,
        tracking=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('architect.financial.category') or 'new'
    )
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)

    # Category Type
    category_type = fields.Selection([
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('both', 'Both')
    ], string='Category Type', default='both')

    # Accounting Integration
    account_id = fields.Many2one('account.account', string='Default Account')

    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')


class ArchitectFinancialSubcategory(models.Model):
    _name = 'architect.financial.subcategory'
    _description = 'Financial Subcategory'
    _order = 'category_id, sequence, name'

    name = fields.Char(string='Subcategory Name', required=True)
    category_id = fields.Many2one('architect.financial.category', string='Category',
                                  required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)

    active = fields.Boolean(default=True)


class ArchitectBudget(models.Model):
    _name = 'architect.budget'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Budget'
    _order = 'project_id, version desc'

    name = fields.Char(string='Budget Name', required=True, tracking=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    version = fields.Integer(string='Version', default=1)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True
    )
    manager_id = fields.Many2one(
        'res.users',
        string='Manager',
        default=lambda self: self.env.user
    )

    budget_type = fields.Selection([
        ('capital', 'Capital'),
        ('operational', 'Operational'),
    ], string='Budget Type')

    # Budget amounts
    total_amount = fields.Monetary(
        string="Total Amount",
        compute="_compute_total_amount",
        store=True,
        currency_field='currency_id'
    )
    spent_amount = fields.Monetary(
        string='Spent Amount',
        compute='_compute_budget_analysis',
        store=True,
        currency_field='currency_id'
    )
    remaining_amount = fields.Monetary(
        string='Remaining Amount',
        compute='_compute_budget_analysis',
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # Status and flags
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed')
    ], string='Status', default='draft', tracking=True)

    is_over_budget = fields.Boolean(
        string='Over Budget',
        compute='_compute_budget_analysis',
        store=True
    )

    # Dates
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    # Relations
    line_ids = fields.One2many('architect.budget.line', 'budget_id', string='Budget Lines')
    cost_estimate_ids = fields.One2many('architect.cost.estimate', 'budget_id', string='Cost Estimates')

    # Approval
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approved_date = fields.Date(string='Approved Date', readonly=True)

    # Analysis fields
    utilization_percentage = fields.Float(
        string='Utilization %',
        compute='_compute_budget_analysis',
        store=True
    )
    variance_amount = fields.Monetary(
        string='Variance Amount',
        compute='_compute_budget_analysis',
        store=True,
        currency_field='currency_id'
    )
    variance_percentage = fields.Float(
        string='Variance %',
        compute='_compute_budget_analysis',
        store=True
    )

    @api.depends('line_ids.budgeted_amount')
    def _compute_total_amount(self):
        for budget in self:
            budget.total_amount = sum(budget.line_ids.mapped('budgeted_amount'))

    @api.depends('line_ids.budgeted_amount', 'line_ids.actual_amount')
    def _compute_budget_analysis(self):
        for budget in self:
            total_budgeted = sum(budget.line_ids.mapped('budgeted_amount'))
            total_actual = sum(budget.line_ids.mapped('actual_amount'))

            budget.spent_amount = total_actual
            budget.remaining_amount = total_budgeted - total_actual
            budget.is_over_budget = total_actual > total_budgeted

            if total_budgeted > 0:
                budget.utilization_percentage = (total_actual / total_budgeted) * 100
                budget.variance_amount = total_actual - total_budgeted
                budget.variance_percentage = (budget.variance_amount / total_budgeted) * 100
            else:
                budget.utilization_percentage = 0.0
                budget.variance_amount = 0.0
                budget.variance_percentage = 0.0

    def action_submit(self):
        for record in self:
            record.state = 'submitted'

    def action_revise(self):
        for record in self:
            record.state = 'draft'

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Date.today()
        })
        self.message_post(body=_("Budget approved."))

    def action_activate(self):
        self.state = 'active'
        self.message_post(body=_("Budget activated."))

    def action_close(self):
        self.state = 'closed'
        self.message_post(body=_("Budget closed."))


class ArchitectBudgetLine(models.Model):
    _name = 'architect.budget.line'
    _description = 'Budget Line'
    _order = 'sequence, id'

    budget_id = fields.Many2one('architect.budget', string='Budget',
                                required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    # Line Details
    description = fields.Text(string="Description")
    category_id = fields.Many2one('architect.financial.category', string='Category')
    subcategory_id = fields.Many2one('architect.financial.subcategory', string='Subcategory')

    # Amounts
    budgeted_amount = fields.Monetary(
        string='Budgeted Amount',
        currency_field='currency_id',
        required=True
    )
    actual_amount = fields.Monetary(
        string='Actual Amount',
        currency_field='currency_id',
        compute='_compute_actual_amount',
        store=True
    )

    # Variance calculations
    variance_amount = fields.Monetary(
        string='Variance Amount',
        currency_field='currency_id',
        compute='_compute_variance',
        store=True
    )
    variance_percentage = fields.Float(
        string='Variance %',
        compute='_compute_variance',
        store=True
    )

    currency_id = fields.Many2one('res.currency', related='budget_id.currency_id', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('budget_id.project_id', 'category_id', 'subcategory_id')
    def _compute_actual_amount(self):
        for line in self:
            domain = [
                ('project_id', '=', line.budget_id.project_id.id),
                ('category_id', '=', line.category_id.id),
                ('state', 'in', ['approved', 'paid']),
                ('transaction_type', '=', 'expense')
            ]
            if line.subcategory_id:
                domain.append(('subcategory_id', '=', line.subcategory_id.id))

            transactions = self.env['architect.financial.tracking'].search(domain)
            line.actual_amount = sum(transactions.mapped('amount'))

    @api.depends('budgeted_amount', 'actual_amount')
    def _compute_variance(self):
        for line in self:
            line.variance_amount = line.actual_amount - line.budgeted_amount
            if line.budgeted_amount > 0:
                line.variance_percentage = (line.variance_amount / line.budgeted_amount) * 100
            else:
                line.variance_percentage = 0.0


class ArchitectCostEstimate(models.Model):
    _name = 'architect.cost.estimate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cost Estimate'
    _order = 'project_id, version desc'

    name = fields.Char(string='Estimate Name', required=True, tracking=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    version = fields.Integer(string='Version', default=1)

    # Added missing fields from XML
    category_id = fields.Many2one('architect.financial.category', string='Category')
    subcategory_id = fields.Many2one('architect.financial.subcategory', string='Subcategory')
    estimator_id = fields.Many2one('res.users', string='Estimator', default=lambda self: self.env.user)

    # Estimate Details
    estimated_amount = fields.Monetary(
        string='Estimated Amount',
        currency_field='currency_id',
        required=True
    )
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # Confidence and approval
    confidence_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string='Confidence Level', default='medium')

    is_approved = fields.Boolean(
        string='Approved',
        compute='_compute_is_approved',
        store=True
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    # Dates (renamed from estimate_date to date for XML compatibility)
    date = fields.Date(string='Estimate Date', default=fields.Date.today)
    validity_date = fields.Date(string='Valid Until')

    # Description fields
    description = fields.Text(string='Description')
    assumptions = fields.Text(string='Assumptions')
    notes = fields.Text(string='Notes')

    # Relations
    budget_id = fields.Many2one('architect.budget', string='Related Budget')
    estimate_line_ids = fields.One2many('architect.cost.estimate.line', 'estimate_id',
                                        string='Estimate Lines')

    # Additional cost calculations
    total_estimate = fields.Monetary(
        string='Total Estimate',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    contingency_percentage = fields.Float(string='Contingency (%)', default=10.0)
    contingency_amount = fields.Monetary(
        string='Contingency Amount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    overhead_percentage = fields.Float(string='Overhead (%)', default=15.0)
    overhead_amount = fields.Monetary(
        string='Overhead Amount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    profit_percentage = fields.Float(string='Profit (%)', default=10.0)
    profit_amount = fields.Monetary(
        string='Profit Amount',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )

    @api.depends('state')
    def _compute_is_approved(self):
        for estimate in self:
            estimate.is_approved = estimate.state == 'approved'

    @api.depends('estimate_line_ids.total_amount', 'contingency_percentage',
                 'overhead_percentage', 'profit_percentage')

    def _compute_totals(self):
        for estimate in self:
            subtotal = sum(estimate.estimate_line_ids.mapped('total_amount'))
            estimate.contingency_amount = subtotal * (estimate.contingency_percentage / 100)
            estimate.overhead_amount = subtotal * (estimate.overhead_percentage / 100)
            estimate.profit_amount = subtotal * (estimate.profit_percentage / 100)
            estimate.total_estimate = (subtotal + estimate.contingency_amount +
                                       estimate.overhead_amount + estimate.profit_amount)

    def action_submit(self):
        self.state = 'submitted'
        self.message_post(body=_("Cost estimate submitted for approval."))

    def action_approve(self):
        self.state = 'approved'
        self.message_post(body=_("Cost estimate approved."))

    def action_reject(self):
        self.state = 'rejected'
        self.message_post(body=_("Cost estimate rejected."))


class ArchitectCostEstimateLine(models.Model):
    _name = 'architect.cost.estimate.line'
    _description = 'Cost Estimate Line'
    _order = 'sequence, id'

    estimate_id = fields.Many2one('architect.cost.estimate', string='Estimate',
                                  required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    # Line Details
    name = fields.Char(string='Description', required=True)
    category_id = fields.Many2one('architect.financial.category', string='Category')

    # Quantities and Rates
    quantity = fields.Float(string='Quantity', default=1.0)
    unit = fields.Char(string='Unit')
    unit_rate = fields.Monetary(string='Unit Rate', currency_field='currency_id')
    total_amount = fields.Monetary(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one('res.currency', related='estimate_id.currency_id', store=True)
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'unit_rate')
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = line.quantity * line.unit_rate