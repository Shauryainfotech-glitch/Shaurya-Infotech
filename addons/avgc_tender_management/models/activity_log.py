from odoo import models, fields, api, _

class ActivityLog(models.Model):
    _name = 'avgc.activity.log'
    _description = 'Activity Log'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char('Title', required=True)
    date = fields.Datetime('Date', default=fields.Datetime.now, required=True)
    user_id = fields.Many2one('res.users', string='User', required=True,
                             default=lambda self: self.env.user)
    
    activity_type = fields.Selection([
        ('tender', 'Tender Activity'),
        ('gem_bid', 'GeM Bid Activity'),
        ('document', 'Document Activity'),
        ('vendor', 'Vendor Activity'),
        ('task', 'Task Activity'),
        ('system', 'System Activity'),
    ], string='Activity Type', required=True)
    
    reference = fields.Reference(selection=[
        ('avgc.tender', 'Tender'),
        ('avgc.gem.bid', 'GeM Bid'),
        ('avgc.tender.document', 'Document'),
        ('avgc.vendor', 'Vendor'),
        ('avgc.task', 'Task'),
    ], string='Reference')
    
    description = fields.Text('Description', required=True)
    details = fields.Text('Additional Details')
    
    # Related Fields for Easy Access
    tender_id = fields.Many2one('avgc.tender', string='Related Tender',
                               compute='_compute_related_records', store=True)
    gem_bid_id = fields.Many2one('avgc.gem.bid', string='Related GeM Bid',
                                compute='_compute_related_records', store=True)
    document_id = fields.Many2one('avgc.tender.document', string='Related Document',
                                 compute='_compute_related_records', store=True)
    vendor_id = fields.Many2one('avgc.vendor', string='Related Vendor',
                               compute='_compute_related_records', store=True)
    task_id = fields.Many2one('avgc.task', string='Related Task',
                             compute='_compute_related_records', store=True)
    
    # Tags for Filtering
    tag_ids = fields.Many2many('avgc.activity.tag', string='Tags')
    
    # Status and Importance
    importance = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Importance', default='medium')
    
    requires_attention = fields.Boolean('Requires Attention')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='completed')

    @api.depends('reference')
    def _compute_related_records(self):
        for record in self:
            record.tender_id = False
            record.gem_bid_id = False
            record.document_id = False
            record.vendor_id = False
            record.task_id = False
            
            if record.reference:
                if record.reference._name == 'avgc.tender':
                    record.tender_id = record.reference.id
                elif record.reference._name == 'avgc.gem.bid':
                    record.gem_bid_id = record.reference.id
                elif record.reference._name == 'avgc.tender.document':
                    record.document_id = record.reference.id
                elif record.reference._name == 'avgc.vendor':
                    record.vendor_id = record.reference.id
                elif record.reference._name == 'avgc.task':
                    record.task_id = record.reference.id

    def action_mark_as_pending(self):
        self.write({'state': 'pending'})

    def action_mark_as_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_mark_as_completed(self):
        self.write({'state': 'completed'})

    def action_mark_as_cancelled(self):
        self.write({'state': 'cancelled'})

    def action_toggle_attention(self):
        self.write({'requires_attention': not self.requires_attention})


class ActivityTag(models.Model):
    _name = 'avgc.activity.tag'
    _description = 'Activity Tag'

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color Index')
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
