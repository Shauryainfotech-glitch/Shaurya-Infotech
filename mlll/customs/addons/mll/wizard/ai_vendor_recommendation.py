from odoo import models, fields

class AiVendorRecommendation(models.TransientModel):
    _name = 'ai.vendor.recommendation'
    _description = 'AI Vendor Recommendation'
    
    assistant_id = fields.Many2one(
        'ai.purchase.assistant',
        string='Assistant',
        required=True,
        ondelete='cascade'
    )
    
    vendor_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        required=True
    )
    
    score = fields.Float(
        string='AI Score',
        help='AI-calculated vendor score (0-100)'
    )
    
    analysis = fields.Text(
        string='Analysis',
        help='Detailed vendor analysis'
    )
    
    products_count = fields.Integer(
        string='Available Products',
        help='Number of relevant products this vendor can supply'
    )
    
    def action_contact_vendor(self):
        """Open vendor contact form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.vendor_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_create_rfq(self):
        """Create RFQ with this vendor"""
        purchase_order = self.assistant_id.purchase_order_id
        
        # Create new purchase order with same lines but different vendor
        new_order = purchase_order.copy({
            'partner_id': self.vendor_id.id,
            'name': self.env['ir.sequence'].next_by_code('purchase.order'),
            'state': 'draft',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': new_order.id,
            'view_mode': 'form',
            'target': 'current',
        }
