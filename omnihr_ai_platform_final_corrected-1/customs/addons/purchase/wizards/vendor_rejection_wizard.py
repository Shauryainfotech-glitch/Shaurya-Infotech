from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VendorRejectionWizard(models.TransientModel):
    _name = 'vendor.rejection.wizard'
    _description = 'Vendor Rejection Wizard'

    vendor_request_id = fields.Many2one(
        'vendor.creation.request',
        string='Vendor Request',
        required=True
    )
    rejection_reason = fields.Selection([
        ('insufficient_info', 'Insufficient Information'),
        ('high_risk', 'High Risk Assessment'),
        ('compliance_issues', 'Compliance Issues'),
        ('financial_concerns', 'Financial Concerns'),
        ('duplicate_vendor', 'Duplicate Vendor'),
        ('other', 'Other')
    ], string='Rejection Reason', required=True)
    
    rejection_notes = fields.Text(
        string='Rejection Notes',
        required=True,
        help="Detailed explanation for the rejection"
    )
    
    notify_requester = fields.Boolean(
        string='Notify Requester',
        default=True,
        help="Send notification email to the person who requested vendor creation"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'vendor.creation.request':
            res['vendor_request_id'] = self.env.context.get('active_id')
        return res

    def action_reject_vendor(self):
        """Reject the vendor creation request with specified reason"""
        if not self.vendor_request_id:
            raise UserError(_('No vendor request specified.'))
        
        # Update the vendor request
        self.vendor_request_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason,
            'rejection_notes': self.rejection_notes,
            'rejected_by': self.env.user.id,
            'rejection_date': fields.Datetime.now()
        })
        
        # Send notification if requested
        if self.notify_requester and self.vendor_request_id.user_id:
            self._send_rejection_notification()
        
        # Log the rejection
        self.vendor_request_id.message_post(
            body=_('Vendor request rejected. Reason: %s. Notes: %s') % (
                dict(self._fields['rejection_reason'].selection)[self.rejection_reason],
                self.rejection_notes
            ),
            message_type='notification'
        )
        
        return {'type': 'ir.actions.act_window_close'}

    def _send_rejection_notification(self):
        """Send email notification about vendor rejection"""
        template = self.env.ref('purchase_ai.vendor_rejection_email_template', raise_if_not_found=False)
        if template:
            template.send_mail(self.vendor_request_id.id, force_send=True)
        else:
            # Fallback notification
            self.vendor_request_id.user_id.notify_info(
                message=_('Your vendor creation request for %s has been rejected.') % self.vendor_request_id.company_name
            ) 