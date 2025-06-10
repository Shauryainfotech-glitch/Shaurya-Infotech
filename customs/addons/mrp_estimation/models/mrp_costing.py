from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpCosting(models.Model):
    _name = 'mrp.costing'
    _description = 'Manufacturing Cost Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char('Reference', required=True, readonly=True, default='New')
    mo_id = fields.Many2one('mrp.production', 'Manufacturing Order', required=True)
    product_id = fields.Many2one('product.product', related='mo_id.product_id', store=True)
    estimation_id = fields.Many2one('mrp.estimation', 'Estimation Reference')

    # Costs
    planned_cost = fields.Monetary('Planned Cost', tracking=True)
    actual_cost = fields.Monetary('Actual Cost', tracking=True)
    cost_variance = fields.Monetary('Cost Variance', compute='_compute_variance', store=True)
    cost_variance_percentage = fields.Float('Variance %', compute='_compute_variance', store=True)

    # Cost Breakdown
    raw_material_cost = fields.Monetary('Raw Material Cost', tracking=True)
    labor_cost_actual = fields.Monetary('Labor Cost', tracking=True)
    overhead_cost = fields.Monetary('Overhead Cost', tracking=True)
    machine_cost = fields.Monetary('Machine Cost', tracking=True)
    quality_cost = fields.Monetary('Quality Cost', tracking=True)

    # Other Fields
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.depends('planned_cost', 'actual_cost')
    def _compute_variance(self):
        for record in self:
            record.cost_variance = record.actual_cost - record.planned_cost
            record.cost_variance_percentage = (
                (record.cost_variance / record.planned_cost * 100)
                if record.planned_cost else 0
            )

    def action_start_costing(self):
        """Start the costing analysis"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Costing can only be started from draft state."))
        self.state = 'in_progress'
        return True

    def action_complete_costing(self):
        """Complete the costing analysis"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_("Only in-progress costings can be completed."))
        self.state = 'done'
        return True

    def action_cancel_costing(self):
        """Cancel the costing analysis"""
        self.ensure_one()
        if self.state in ['done', 'cancelled']:
            raise UserError(_("Cannot cancel completed or already cancelled costings."))
        self.state = 'cancelled'
        return True

    def action_reset_to_draft(self):
        """Reset costing to draft state"""
        self.ensure_one()
        if self.state not in ['cancelled', 'done']:
            raise UserError(_("Only cancelled or completed costings can be reset to draft."))
        self.state = 'draft'
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('mrp.costing') or 'New'
        return super().create(vals_list)