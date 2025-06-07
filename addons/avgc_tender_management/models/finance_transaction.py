from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class FinanceTransaction(models.Model):
    _name = 'avgc.finance.transaction'
    _description = 'Finance Transaction Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'transaction_date desc'
    
    # Basic Information
    name = fields.Char('Transaction Reference', required=True, copy=False,
                      default=lambda self: _('New'), tracking=True)
    description = fields.Text('Description')
    
    # Related Records
    tender_id = fields.Many2one('avgc.tender', string='Related Tender', ondelete='cascade')
    gem_bid_id = fields.Many2one('avgc.gem.bid', string='Related GeM Bid', ondelete='cascade')
    vendor_id = fields.Many2one('avgc.vendor', string='Vendor')
    
    # Transaction Details
    transaction_type = fields.Selection([
        ('emd', 'Earnest Money Deposit'),
        ('document_fee', 'Document Fee'),
        ('security_deposit', 'Security Deposit'),
        ('advance_payment', 'Advance Payment'),
        ('milestone_payment', 'Milestone Payment'),
        ('final_payment', 'Final Payment'),
        ('penalty', 'Penalty'),
        ('refund', 'Refund'),
        ('retention', 'Retention Money'),
        ('other', 'Other'),
    ], string='Transaction Type', required=True, tracking=True)
    
    # Financial Information
    amount = fields.Monetary('Amount', currency_field='currency_id', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    
    # Transaction Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Dates
    transaction_date = fields.Date('Transaction Date', required=True, default=fields.Date.today)
    due_date = fields.Date('Due Date')
    completion_date = fields.Date('Completion Date')
    
    # Payment Details
    payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('dd', 'Demand Draft'),
        ('online', 'Online Payment'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ], string='Payment Method', tracking=True)
    
    payment_reference = fields.Char('Payment Reference', tracking=True)
    bank_reference = fields.Char('Bank Reference')
    utr_number = fields.Char('UTR Number')
    
    # Account Information
    account_id = fields.Many2one('account.account', string='Account')
    journal_id = fields.Many2one('account.journal', string='Journal')
    
    # Direction
    direction = fields.Selection([
        ('inbound', 'Inbound (Received)'),
        ('outbound', 'Outbound (Paid)'),
    ], string='Direction', required=True, default='outbound')
    
    # Approval Workflow
    requires_approval = fields.Boolean('Requires Approval', default=True)
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Datetime('Approval Date')
    approval_notes = fields.Text('Approval Notes')
    
    # Document Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    # Compliance and Audit
    compliance_status = fields.Selection([
        ('pending', 'Pending Review'),
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('requires_action', 'Requires Action'),
    ], string='Compliance Status', default='pending')
    
    audit_notes = fields.Text('Audit Notes')
    
    # Related Transactions
    parent_transaction_id = fields.Many2one('avgc.finance.transaction', string='Parent Transaction')
    child_transaction_ids = fields.One2many('avgc.finance.transaction', 'parent_transaction_id', 
                                           string='Child Transactions')
    
    # Computed Fields
    is_overdue = fields.Boolean('Is Overdue', compute='_compute_is_overdue')
    days_overdue = fields.Integer('Days Overdue', compute='_compute_days_overdue')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('avgc.finance.transaction') or _('New')
        return super(FinanceTransaction, self).create(vals)
    
    @api.depends('due_date', 'status')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (
                record.due_date and 
                record.due_date < today and 
                record.status not in ['completed', 'cancelled', 'refunded']
            )
    
    @api.depends('due_date', 'status')
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.due_date and record.status not in ['completed', 'cancelled', 'refunded']:
                delta = today - record.due_date
                record.days_overdue = max(0, delta.days)
            else:
                record.days_overdue = 0
    
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('Transaction amount must be greater than zero.'))
    
    def action_submit_for_approval(self):
        """Submit transaction for approval"""
        for record in self:
            if record.status == 'draft':
                record.status = 'pending'
                record.message_post(body=_('Transaction submitted for approval.'))
    
    def action_approve(self):
        """Approve transaction"""
        for record in self:
            if record.status == 'pending':
                record.status = 'processing'
                record.approved_by = self.env.user
                record.approval_date = fields.Datetime.now()
                record.message_post(body=_('Transaction approved.'))
    
    def action_complete(self):
        """Mark transaction as completed"""
        for record in self:
            if record.status == 'processing':
                record.status = 'completed'
                record.completion_date = fields.Date.today()
                record.message_post(body=_('Transaction completed.'))
    
    def action_cancel(self):
        """Cancel transaction"""
        for record in self:
            if record.status in ['draft', 'pending', 'processing']:
                record.status = 'cancelled'
                record.message_post(body=_('Transaction cancelled.'))
    
    def action_create_refund(self):
        """Create refund transaction"""
        for record in self:
            if record.status == 'completed':
                refund = record.copy({
                    'name': f"REFUND-{record.name}",
                    'amount': -record.amount,
                    'direction': 'inbound' if record.direction == 'outbound' else 'outbound',
                    'transaction_type': 'refund',
                    'parent_transaction_id': record.id,
                    'status': 'draft',
                })
                
                return {
                    'name': _('Refund Transaction'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'avgc.finance.transaction',
                    'res_id': refund.id,
                    'target': 'current',
                }


class Budget(models.Model):
    _name = 'avgc.budget'
    _description = 'Budget Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fiscal_year desc, name'
    
    # Basic Information
    name = fields.Char('Budget Name', required=True, tracking=True)
    code = fields.Char('Budget Code', required=True)
    description = fields.Text('Description')
    
    # Period
    fiscal_year = fields.Char('Fiscal Year', required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    
    # Budget Categories
    category = fields.Selection([
        ('operational', 'Operational'),
        ('capital', 'Capital'),
        ('project', 'Project-based'),
        ('department', 'Department-wise'),
    ], string='Budget Category', required=True)
    
    # Financial Information
    total_budget = fields.Monetary('Total Budget', currency_field='currency_id', required=True)
    allocated_amount = fields.Monetary('Allocated Amount', currency_field='currency_id')
    spent_amount = fields.Monetary('Spent Amount', compute='_compute_spent_amount', store=True)
    remaining_amount = fields.Monetary('Remaining Amount', compute='_compute_remaining_amount')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Ownership
    department_id = fields.Many2one('hr.department', string='Department')
    responsible_user_id = fields.Many2one('res.users', string='Budget Owner', 
                                         default=lambda self: self.env.user)
    
    # Budget Lines
    line_ids = fields.One2many('avgc.budget.line', 'budget_id', string='Budget Lines')
    
    # Related Transactions
    transaction_ids = fields.One2many('avgc.finance.transaction', 'budget_id', string='Transactions')
    
    # Computed Fields
    utilization_percentage = fields.Float('Budget Utilization (%)', 
                                        compute='_compute_utilization_percentage', digits=(5, 2))
    is_over_budget = fields.Boolean('Over Budget', compute='_compute_is_over_budget')
    
    @api.depends('transaction_ids.amount', 'transaction_ids.status')
    def _compute_spent_amount(self):
        for record in self:
            completed_transactions = record.transaction_ids.filtered(
                lambda t: t.status == 'completed' and t.direction == 'outbound'
            )
            record.spent_amount = sum(completed_transactions.mapped('amount'))
    
    @api.depends('total_budget', 'spent_amount')
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.total_budget - record.spent_amount
    
    @api.depends('total_budget', 'spent_amount')
    def _compute_utilization_percentage(self):
        for record in self:
            if record.total_budget > 0:
                record.utilization_percentage = (record.spent_amount / record.total_budget) * 100
            else:
                record.utilization_percentage = 0
    
    @api.depends('spent_amount', 'total_budget')
    def _compute_is_over_budget(self):
        for record in self:
            record.is_over_budget = record.spent_amount > record.total_budget
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date >= record.end_date:
                raise ValidationError(_('End date must be after start date.'))
    
    def action_approve(self):
        """Approve budget"""
        for record in self:
            if record.status == 'draft':
                record.status = 'approved'
                record.message_post(body=_('Budget approved.'))
    
    def action_activate(self):
        """Activate budget"""
        for record in self:
            if record.status == 'approved':
                record.status = 'active'
                record.message_post(body=_('Budget activated.'))


class BudgetLine(models.Model):
    _name = 'avgc.budget.line'
    _description = 'Budget Line Item'
    _order = 'sequence, name'
    
    budget_id = fields.Many2one('avgc.budget', string='Budget', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    
    # Line Details
    name = fields.Char('Line Item', required=True)
    code = fields.Char('Code')
    description = fields.Text('Description')
    
    # Category
    category = fields.Selection([
        ('personnel', 'Personnel'),
        ('equipment', 'Equipment'),
        ('services', 'Services'),
        ('travel', 'Travel'),
        ('training', 'Training'),
        ('miscellaneous', 'Miscellaneous'),
    ], string='Category', required=True)
    
    # Budget Allocation
    budgeted_amount = fields.Monetary('Budgeted Amount', currency_field='currency_id', required=True)
    spent_amount = fields.Monetary('Spent Amount', compute='_compute_spent_amount', store=True)
    remaining_amount = fields.Monetary('Remaining Amount', compute='_compute_remaining_amount')
    currency_id = fields.Related('budget_id.currency_id', store=True)
    
    # Tracking
    account_id = fields.Many2one('account.account', string='Account')
    
    # Related Transactions
    transaction_ids = fields.One2many('avgc.finance.transaction', 'budget_line_id', 
                                     string='Transactions')
    
    @api.depends('transaction_ids.amount', 'transaction_ids.status')
    def _compute_spent_amount(self):
        for record in self:
            completed_transactions = record.transaction_ids.filtered(
                lambda t: t.status == 'completed' and t.direction == 'outbound'
            )
            record.spent_amount = sum(completed_transactions.mapped('amount'))
    
    @api.depends('budgeted_amount', 'spent_amount')
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.budgeted_amount - record.spent_amount


class PaymentSchedule(models.Model):
    _name = 'avgc.payment.schedule'
    _description = 'Payment Schedule'
    _order = 'due_date'
    
    # Related Records
    tender_id = fields.Many2one('avgc.tender', string='Tender', ondelete='cascade')
    gem_bid_id = fields.Many2one('avgc.gem.bid', string='GeM Bid', ondelete='cascade')
    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True)
    
    # Schedule Details
    name = fields.Char('Milestone/Description', required=True)
    sequence = fields.Integer('Sequence', default=10)
    
    # Financial Information
    amount = fields.Monetary('Amount', currency_field='currency_id', required=True)
    percentage = fields.Float('Percentage of Total', digits=(5, 2))
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    
    # Dates
    due_date = fields.Date('Due Date', required=True)
    payment_date = fields.Date('Actual Payment Date')
    
    # Status
    status = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready for Payment'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', compute='_compute_status', store=True)
    
    # Conditions
    milestone_description = fields.Text('Milestone Description')
    completion_criteria = fields.Text('Completion Criteria')
    is_milestone_completed = fields.Boolean('Milestone Completed', default=False)
    
    # Related Transaction
    transaction_id = fields.Many2one('avgc.finance.transaction', string='Payment Transaction')
    
    # Computed Fields
    days_overdue = fields.Integer('Days Overdue', compute='_compute_days_overdue')
    
    @api.depends('due_date', 'payment_date', 'is_milestone_completed')
    def _compute_status(self):
        today = fields.Date.today()
        for record in self:
            if record.payment_date:
                record.status = 'paid'
            elif record.transaction_id and record.transaction_id.status == 'processing':
                record.status = 'processing'
            elif record.is_milestone_completed:
                record.status = 'ready'
            elif record.due_date < today:
                record.status = 'overdue'
            else:
                record.status = 'pending'
    
    @api.depends('due_date', 'status')
    def _compute_days_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.status == 'overdue':
                delta = today - record.due_date
                record.days_overdue = delta.days
            else:
                record.days_overdue = 0
    
    def action_mark_milestone_completed(self):
        """Mark milestone as completed"""
        for record in self:
            record.is_milestone_completed = True
            record.message_post(body=_('Milestone marked as completed.'))
    
    def action_create_payment(self):
        """Create payment transaction"""
        for record in self:
            if record.status == 'ready':
                transaction = self.env['avgc.finance.transaction'].create({
                    'name': f"Payment for {record.name}",
                    'tender_id': record.tender_id.id,
                    'gem_bid_id': record.gem_bid_id.id,
                    'vendor_id': record.vendor_id.id,
                    'transaction_type': 'milestone_payment',
                    'amount': record.amount,
                    'currency_id': record.currency_id.id,
                    'due_date': record.due_date,
                    'direction': 'outbound',
                    'description': f"Payment for milestone: {record.name}",
                })
                
                record.transaction_id = transaction.id
                
                return {
                    'name': _('Payment Transaction'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'avgc.finance.transaction',
                    'res_id': transaction.id,
                    'target': 'current',
                }