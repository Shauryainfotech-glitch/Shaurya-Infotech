from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VendorSuggestionFeedbackWizard(models.TransientModel):
    _name = 'vendor.suggestion.feedback.wizard'
    _description = 'Vendor Suggestion Feedback Wizard'

    suggestion_id = fields.Many2one(
        'purchase.vendor.suggestion',
        string='Vendor Suggestion',
        required=True
    )
    
    rating = fields.Selection([
        ('1', '1 - Very Poor'),
        ('2', '2 - Poor'),
        ('3', '3 - Average'),
        ('4', '4 - Good'),
        ('5', '5 - Excellent')
    ], string='Rating', required=True)
    
    feedback_text = fields.Text(
        string='Feedback',
        required=True,
        help="Please provide detailed feedback about this vendor suggestion"
    )
    
    accuracy_rating = fields.Selection([
        ('1', '1 - Very Inaccurate'),
        ('2', '2 - Inaccurate'),
        ('3', '3 - Somewhat Accurate'),
        ('4', '4 - Accurate'),
        ('5', '5 - Very Accurate')
    ], string='Accuracy Rating', required=True,
       help="How accurate was the AI suggestion compared to actual vendor performance?")
    
    usefulness_rating = fields.Selection([
        ('1', '1 - Not Useful'),
        ('2', '2 - Slightly Useful'),
        ('3', '3 - Moderately Useful'),
        ('4', '4 - Very Useful'),
        ('5', '5 - Extremely Useful')
    ], string='Usefulness Rating', required=True,
       help="How useful was this suggestion in your decision-making process?")
    
    would_recommend = fields.Boolean(
        string='Would Recommend Vendor',
        help="Would you recommend this vendor to others?"
    )
    
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Related Purchase Order',
        help="Link to the purchase order if one was created"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'purchase.vendor.suggestion':
            res['suggestion_id'] = self.env.context.get('active_id')
        return res

    def action_submit_feedback(self):
        """Submit feedback for the vendor suggestion"""
        if not self.suggestion_id:
            raise UserError(_('No vendor suggestion specified.'))
        
        # Create feedback record
        feedback_vals = {
            'suggestion_id': self.suggestion_id.id,
            'user_id': self.env.user.id,
            'rating': int(self.rating),
            'feedback_text': self.feedback_text,
            'accuracy_rating': int(self.accuracy_rating),
            'usefulness_rating': int(self.usefulness_rating),
            'would_recommend': self.would_recommend,
            'feedback_type': 'user',
            'purchase_order_id': self.purchase_order_id.id if self.purchase_order_id else False
        }
        
        feedback = self.env['vendor.suggestion.feedback'].create(feedback_vals)
        
        # Update suggestion with feedback
        self.suggestion_id.write({
            'user_feedback_count': self.suggestion_id.user_feedback_count + 1,
            'average_user_rating': self._calculate_average_rating()
        })
        
        # Log the feedback
        self.suggestion_id.message_post(
            body=_('User feedback submitted. Rating: %s/5, Accuracy: %s/5, Usefulness: %s/5') % (
                self.rating, self.accuracy_rating, self.usefulness_rating
            ),
            message_type='notification'
        )
        
        # Trigger learning update
        self.suggestion_id._update_learning_data()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Feedback Submitted'),
                'message': _('Thank you for your feedback! This helps improve our AI suggestions.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _calculate_average_rating(self):
        """Calculate average rating for the suggestion"""
        feedbacks = self.env['vendor.suggestion.feedback'].search([
            ('suggestion_id', '=', self.suggestion_id.id),
            ('feedback_type', '=', 'user')
        ])
        
        if not feedbacks:
            return 0.0
        
        total_rating = sum(feedback.rating for feedback in feedbacks)
        return total_rating / len(feedbacks) 