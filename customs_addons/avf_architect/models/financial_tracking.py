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
    user_id = fields.Many2one('res.users', string="User")
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
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # Dates
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    due_date = fields.Date(string='Due Date')

    # Categories
    category_id = fields.Many2one('architect.financial.category', string='Category')
    subcategory_id = fields.Many2one('architect.financial.subcategory', string='Subcategory')
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

    # Approval
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Date(string='Approval Date')

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
            record.state = 'approved'

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
    code = fields.Char(string='Category Code')
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
    # Budget Details
    total_budget = fields.Monetary(string='Total Budget', currency_field='currency_id',
                                   required=True, tracking=True)
    allocated_budget = fields.Monetary(string='Allocated Budget',
                                       compute='_compute_budget_analysis', store=True)
    spent_amount = fields.Monetary(string='Spent Amount',
                                   compute='_compute_budget_analysis', store=True)
    remaining_budget = fields.Monetary(string='Remaining Budget',
                                       compute='_compute_budget_analysis', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # Budget Lines
    budget_line_ids = fields.One2many('architect.budget.line', 'budget_id',
                                      string='Budget Lines')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed')
    ], string='Status', default='draft', tracking=True)

    # Dates
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    # Approval
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Date(string='Approval Date')

    # Analysis
    budget_utilization = fields.Float(string='Budget Utilization (%)',
                                      compute='_compute_budget_analysis', store=True)
    variance_amount = fields.Monetary(string='Variance Amount',
                                      compute='_compute_budget_analysis', store=True)
    variance_percentage = fields.Float(string='Variance (%)',
                                       compute='_compute_budget_analysis', store=True)

    @api.depends('budget_line_ids.allocated_amount', 'budget_line_ids.spent_amount')
    def _compute_budget_analysis(self):
        for budget in self:
            budget.allocated_budget = sum(budget.budget_line_ids.mapped('allocated_amount'))
            budget.spent_amount = sum(budget.budget_line_ids.mapped('spent_amount'))
            budget.remaining_budget = budget.total_budget - budget.spent_amount

            if budget.total_budget > 0:
                budget.budget_utilization = (budget.spent_amount / budget.total_budget) * 100
                budget.variance_amount = budget.spent_amount - budget.total_budget
                budget.variance_percentage = (budget.variance_amount / budget.total_budget) * 100
            else:
                budget.budget_utilization = 0.0
                budget.variance_amount = 0.0
                budget.variance_percentage = 0.0

    def action_submit(self):
        for record in self:
            record.state = 'submitted'



    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Date.today()
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
    name = fields.Char(string='Description', required=True)
    category_id = fields.Many2one('architect.financial.category', string='Category')
    subcategory_id = fields.Many2one('architect.financial.subcategory', string='Subcategory')

    # Amounts
    allocated_amount = fields.Monetary(string='Allocated Amount',
                                       currency_field='currency_id', required=True)
    spent_amount = fields.Monetary(string='Spent Amount',
                                   compute='_compute_spent_amount', store=True)
    remaining_amount = fields.Monetary(string='Remaining Amount',
                                       compute='_compute_spent_amount', store=True)

    currency_id = fields.Many2one('res.currency', related='budget_id.currency_id', store=True)

    # Analysis
    utilization_percentage = fields.Float(string='Utilization (%)',
                                          compute='_compute_spent_amount', store=True)

    # Notes
    notes = fields.Text(string='Notes')

    @api.depends('allocated_amount')
    def _compute_spent_amount(self):
        for line in self:
            # Get actual spent amount from financial tracking
            spent = self.env['architect.financial.tracking'].search([
                ('project_id', '=', line.budget_id.project_id.id),
                ('category_id', '=', line.category_id.id),
                ('state', '=', 'confirmed'),
                ('transaction_type', '=', 'expense')
            ])
            line.spent_amount = sum(spent.mapped('amount'))
            line.remaining_amount = line.allocated_amount - line.spent_amount

            if line.allocated_amount > 0:
                line.utilization_percentage = (line.spent_amount / line.allocated_amount) * 100
            else:
                line.utilization_percentage = 0.0


class ArchitectCostEstimate(models.Model):
    _name = 'architect.cost.estimate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cost Estimate'
    _order = 'project_id, version desc'

    name = fields.Char(string='Estimate Name', required=True, tracking=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    version = fields.Integer(string='Version', default=1)

    # Estimate Details
    total_estimate = fields.Monetary(string='Total Estimate',
                                     compute='_compute_totals', store=True,
                                     currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # Estimate Lines
    estimate_line_ids = fields.One2many('architect.cost.estimate.line', 'estimate_id',
                                        string='Estimate Lines')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    # Dates
    estimate_date = fields.Date(string='Estimate Date', default=fields.Date.today)
    validity_date = fields.Date(string='Valid Until')

    # Additional Costs
    contingency_percentage = fields.Float(string='Contingency (%)', default=10.0)
    contingency_amount = fields.Monetary(string='Contingency Amount',
                                         compute='_compute_totals', store=True,
                                         currency_field='currency_id')

    overhead_percentage = fields.Float(string='Overhead (%)', default=15.0)
    overhead_amount = fields.Monetary(string='Overhead Amount',
                                      compute='_compute_totals', store=True,
                                      currency_field='currency_id')

    profit_percentage = fields.Float(string='Profit (%)', default=10.0)
    profit_amount = fields.Monetary(string='Profit Amount',
                                    compute='_compute_totals', store=True,
                                    currency_field='currency_id')

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
    total_amount = fields.Monetary(string='Total Amount',
                                   compute='_compute_total_amount', store=True,
                                   currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='estimate_id.currency_id', store=True)

    # Notes
    notes = fields.Text(string='Notes')

    @api.depends('quantity', 'unit_rate')
    def _compute_total_amount(self):
        for line in self:
            line.total_amount = line.quantity * line.unit_rate