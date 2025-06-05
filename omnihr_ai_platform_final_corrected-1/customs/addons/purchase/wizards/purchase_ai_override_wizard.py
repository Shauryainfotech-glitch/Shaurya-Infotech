from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseAIOverrideWizard(models.TransientModel):
    _name = 'purchase.ai.override.wizard'
    _description = 'Purchase AI Override Wizard'

    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        required=True
    )
    
    override_type = fields.Selection([
        ('vendor_suggestion', 'Override Vendor Suggestion'),
        ('risk_assessment', 'Override Risk Assessment'),
        ('approval_requirement', 'Override Approval Requirement'),
        ('price_validation', 'Override Price Validation'),
        ('compliance_check', 'Override Compliance Check')
    ], string='Override Type', required=True)
    
    override_reason = fields.Selection([
        ('business_requirement', 'Business Requirement'),
        ('strategic_decision', 'Strategic Decision'),
        ('emergency_purchase', 'Emergency Purchase'),
        ('ai_error', 'AI Analysis Error'),
        ('manual_verification', 'Manual Verification'),
        ('other', 'Other')
    ], string='Override Reason', required=True)
    
    justification = fields.Text(
        string='Justification',
        required=True,
        help="Detailed justification for overriding AI recommendation"
    )
    
    new_vendor_id = fields.Many2one(
        'res.partner',
        string='New Vendor',
        domain=[('is_company', '=', True), ('supplier_rank', '>', 0)],
        help="Select new vendor if overriding vendor suggestion"
    )
    
    new_risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], string='New Risk Level',
       help="Manually set risk level if overriding risk assessment")
    
    requires_approval = fields.Boolean(
        string='Requires Additional Approval',
        default=True,
        help="Whether this override requires additional approval"
    )
    
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        help="User who should approve this override"
    )
    
    notify_ai_team = fields.Boolean(
        string='Notify AI Team',
        default=True,
        help="Notify AI team about this override for system improvement"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'purchase.order':
            res['purchase_order_id'] = self.env.context.get('active_id')
        return res

    @api.onchange('override_type')
    def _onchange_override_type(self):
        """Update form based on override type"""
        if self.override_type == 'vendor_suggestion':
            # Show vendor selection
            pass
        elif self.override_type == 'risk_assessment':
            # Show risk level selection
            pass

    def action_apply_override(self):
        """Apply the AI override"""
        if not self.purchase_order_id:
            raise UserError(_('No purchase order specified.'))
        
        # Create override record
        override_vals = {
            'purchase_order_id': self.purchase_order_id.id,
            'override_type': self.override_type,
            'override_reason': self.override_reason,
            'justification': self.justification,
            'overridden_by': self.env.user.id,
            'override_date': fields.Datetime.now(),
            'new_vendor_id': self.new_vendor_id.id if self.new_vendor_id else False,
            'new_risk_level': self.new_risk_level,
            'requires_approval': self.requires_approval,
            'approver_id': self.approver_id.id if self.approver_id else False,
            'state': 'pending' if self.requires_approval else 'approved'
        }
        
        override = self.env['purchase.ai.override'].create(override_vals)
        
        # Apply the override if no approval required
        if not self.requires_approval:
            self._apply_override_changes(override)
        
        # Send notifications
        if self.notify_ai_team:
            self._notify_ai_team(override)
        
        if self.requires_approval and self.approver_id:
            self._notify_approver(override)
        
        # Log the override
        self.purchase_order_id.message_post(
            body=_('AI override applied. Type: %s, Reason: %s') % (
                dict(self._fields['override_type'].selection)[self.override_type],
                dict(self._fields['override_reason'].selection)[self.override_reason]
            ),
            message_type='notification'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Override Applied'),
                'message': _('AI override has been applied successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _apply_override_changes(self, override):
        """Apply the actual changes from the override"""
        if override.override_type == 'vendor_suggestion' and override.new_vendor_id:
            self.purchase_order_id.write({
                'partner_id': override.new_vendor_id.id
            })
        
        elif override.override_type == 'risk_assessment' and override.new_risk_level:
            # Update risk assessment if exists
            risk_assessment = self.env['risk.assessment'].search([
                ('vendor_id', '=', self.purchase_order_id.partner_id.id),
                ('is_current', '=', True)
            ], limit=1)
            if risk_assessment:
                risk_assessment.write({
                    'risk_level': override.new_risk_level,
                    'manual_override': True,
                    'override_reason': override.justification
                })

    def _notify_ai_team(self, override):
        """Notify AI team about the override"""
        # Create activity for AI team
        ai_team_users = self.env['res.users'].search([
            ('groups_id', 'in', [self.env.ref('purchase_ai.group_purchase_ai_admin').id])
        ])
        
        for user in ai_team_users:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': _('AI Override Notification'),
                'note': _('Purchase order %s has an AI override that may require system review.') % self.purchase_order_id.name,
                'user_id': user.id,
                'res_model': 'purchase.order',
                'res_id': self.purchase_order_id.id
            })

    def _notify_approver(self, override):
        """Notify approver about pending override"""
        if override.approver_id:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': _('AI Override Approval Required'),
                'note': _('Please review and approve the AI override for purchase order %s.') % self.purchase_order_id.name,
                'user_id': override.approver_id.id,
                'res_model': 'purchase.ai.override',
                'res_id': override.id
            })


class PurchaseAIOverride(models.Model):
    _name = 'purchase.ai.override'
    _description = 'Purchase AI Override'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'override_date desc'

    name = fields.Char(string='Override Reference', required=True, default='New')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    override_type = fields.Selection([
        ('vendor_suggestion', 'Override Vendor Suggestion'),
        ('risk_assessment', 'Override Risk Assessment'),
        ('approval_requirement', 'Override Approval Requirement'),
        ('price_validation', 'Override Price Validation'),
        ('compliance_check', 'Override Compliance Check')
    ], string='Override Type', required=True)
    
    override_reason = fields.Selection([
        ('business_requirement', 'Business Requirement'),
        ('strategic_decision', 'Strategic Decision'),
        ('emergency_purchase', 'Emergency Purchase'),
        ('ai_error', 'AI Analysis Error'),
        ('manual_verification', 'Manual Verification'),
        ('other', 'Other')
    ], string='Override Reason', required=True)
    
    justification = fields.Text(string='Justification', required=True)
    overridden_by = fields.Many2one('res.users', string='Overridden By', required=True)
    override_date = fields.Datetime(string='Override Date', required=True)
    
    new_vendor_id = fields.Many2one('res.partner', string='New Vendor')
    new_risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], string='New Risk Level')
    
    requires_approval = fields.Boolean(string='Requires Approval', default=True)
    approver_id = fields.Many2one('res.users', string='Approver')
    approved_by = fields.Many2one('res.users', string='Approved By')
    approval_date = fields.Datetime(string='Approval Date')
    
    state = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='State', default='pending', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.ai.override') or 'New'
        return super().create(vals)

    def action_approve(self):
        """Approve the override"""
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        
        # Apply the override changes
        wizard = self.env['purchase.ai.override.wizard']
        wizard._apply_override_changes(self)

    def action_reject(self):
        """Reject the override"""
        self.write({
            'state': 'rejected',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        }) 