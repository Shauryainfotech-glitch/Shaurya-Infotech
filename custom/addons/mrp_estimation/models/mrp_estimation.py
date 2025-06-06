from odoo import models, fields, api

class MrpEstimation(models.Model):
    _name = 'mrp.estimation'
    _description = 'Manufacturing Estimation'

    # Basic Information Fields
    name = fields.Char(string='Estimation Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    # Approver Field
    approver_id = fields.Many2one('res.users', string='Approver')

    # State Field to track Estimation Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

    # Date Fields
    date_create = fields.Datetime(string='Creation Date', default=fields.Datetime.now, readonly=True)
    date_confirmed = fields.Datetime(string='Confirmed Date')
    date_approved = fields.Datetime(string='Approved Date')

    # Description or Notes
    description = fields.Text(string='Description')

    # Total Estimated Cost (optional)
    estimated_cost = fields.Float(string='Estimated Cost', compute='_compute_estimated_cost', store=True)

    # Related Fields (many2one relationships)
    partner_id = fields.Many2one('res.partner', string='Customer')

    @api.depends('estimated_cost')
    def _compute_estimated_cost(self):
        for record in self:
            # Logic to calculate the estimated cost
            record.estimated_cost = 1000.0  # Replace this with your own cost calculation logic

    def action_confirm(self):
        """ Change the state to 'confirmed' """
        self.write({'state': 'confirmed', 'date_confirmed': fields.Datetime.now()})

    def action_approve(self):
        """ Change the state to 'approved' """
        self.write({'state': 'approved', 'date_approved': fields.Datetime.now()})

    def action_cancel(self):
        """ Change the state to 'cancelled' """
        self.write({'state': 'cancelled'})

    def action_done(self):
        """ Change the state to 'done' """
        self.write({'state': 'done'})
