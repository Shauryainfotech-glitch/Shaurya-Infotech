from odoo import models, fields, api
import json
from datetime import datetime

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'ai.llm.mixin']
    
    def _get_ai_context(self):
        """Provide partner-specific context for AI"""
        context = super()._get_ai_context()
        context_data = json.loads(context)
        context_data.update({
            'partner_name': self.name,
            'partner_type': 'company' if self.is_company else 'individual',
            'email': self.email or '',
            'phone': self.phone or '',
            'country': self.country_id.name if self.country_id else '',
            'category': [cat.name for cat in self.category_id],
            'is_customer': self.customer_rank > 0,
            'is_vendor': self.supplier_rank > 0,
        })
        return json.dumps(context_data)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'ai.llm.mixin']
    
    ai_generated_description = fields.Text(
        string='AI Generated Description',
        help='Product description generated by AI'
    )
    
    def _get_ai_context(self):
        """Provide sale order specific context for AI"""
        context = super()._get_ai_context()
        context_data = json.loads(context)
        context_data.update({
            'order_name': self.name,
            'partner_name': self.partner_id.name,
            'state': self.state,
            'amount_total': self.amount_total,
            'currency': self.currency_id.name,
            'order_lines': [{
                'product': line.product_id.name,
                'quantity': line.product_uom_qty,
                'price': line.price_unit,
            } for line in self.order_line],
        })
        return json.dumps(context_data)
    
    def action_generate_quotation_content(self):
        """Generate quotation content using AI"""
        self.ensure_one()
        return {
            'name': 'Generate Quotation Content',
            'type': 'ir.actions.act_window',
            'res_model': 'ai.content.generator',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model_name': self._name,
                'default_res_id': self.id,
                'default_prompt_type': 'description',
                'default_context_data': self._get_ai_context(),
            }
        }


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'ai.llm.mixin']
    
    def _get_ai_context(self):
        """Provide task-specific context for AI"""
        context = super()._get_ai_context()
        context_data = json.loads(context)
        context_data.update({
            'task_name': self.name,
            'project_name': self.project_id.name if self.project_id else '',
            'stage': self.stage_id.name if self.stage_id else '',
            'priority': self.priority,
            'assigned_to': self.user_ids.mapped('name'),
            'description': self.description or '',
            'deadline': self.date_deadline.strftime('%Y-%m-%d') if self.date_deadline else '',
        })
        return json.dumps(context_data)


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'ai.llm.mixin']
    
    # Override AI fields with additional security for HR employee context
    ai_conversation_ids = fields.One2many(
        'ai.llm.conversation',
        'res_id',
        compute='_compute_ai_conversations',
        string='AI Conversations',
        groups='mll.group_ai_user,hr.group_hr_user'
    )
    
    ai_suggestions = fields.Text(
        string='AI Suggestions',
        compute='_compute_ai_suggestions',
        groups='mll.group_ai_user,hr.group_hr_user'
    )
    
    def _get_ai_context(self):
        """Provide employee-specific context for AI"""
        context = super()._get_ai_context()
        context_data = json.loads(context)
        context_data.update({
            'employee_name': self.name,
            'job_title': self.job_title or '',
            'department': self.department_id.name if self.department_id else '',
            'manager': self.parent_id.name if self.parent_id else '',
            'work_email': self.work_email or '',
            'work_phone': self.work_phone or '',
        })
        return json.dumps(context_data)
    
    def _compute_ai_conversations(self):
        """Compute related AI conversations with permission check"""
        if not self.user_has_groups('mll.group_ai_user,hr.group_hr_user'):
            for record in self:
                record.ai_conversation_ids = self.env['ai.llm.conversation']
            return
        super()._compute_ai_conversations()
    
    def _compute_ai_suggestions(self):
        """Compute AI suggestions with permission check"""
        if not self.user_has_groups('mll.group_ai_user,hr.group_hr_user'):
            for record in self:
                record.ai_suggestions = False
            return
        super()._compute_ai_suggestions()


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'ai.llm.mixin']
    
    ai_vendor_suggestions = fields.Text(
        string='AI Vendor Suggestions',
        compute='_compute_ai_vendor_suggestions',
        help='AI-generated vendor recommendations based on product requirements'
    )
    
    ai_negotiation_tips = fields.Text(
        string='Negotiation Tips',
        compute='_compute_ai_negotiation_tips',
        help='AI-generated negotiation strategies based on vendor history and market data'
    )
    
    def _get_ai_context(self):
        """Provide purchase-specific context for AI"""
        context = super()._get_ai_context()
        context_data = json.loads(context)
        context_data.update({
            'order_name': self.name,
            'vendor': self.partner_id.name if self.partner_id else '',
            'products': [{
                'name': line.product_id.name,
                'description': line.name,
                'quantity': line.product_qty,
                'uom': line.product_uom.name,
                'price': line.price_unit,
                'category': line.product_id.categ_id.name,
            } for line in self.order_line],
            'currency': self.currency_id.name,
            'company': self.company_id.name,
            'date_planned': self.date_planned.strftime('%Y-%m-%d') if self.date_planned else '',
        })
        return json.dumps(context_data)
    
    def _compute_ai_vendor_suggestions(self):
        """Generate vendor suggestions based on product requirements"""
        for record in self:
            if not record.order_line:
                record.ai_vendor_suggestions = False
                continue
            
            # Get product categories and specifications
            categories = record.order_line.mapped('product_id.categ_id.name')
            products = record.order_line.mapped('product_id.name')
            
            # Find similar vendors from historical data
            similar_orders = self.env['purchase.order'].search([
                ('state', '=', 'purchase'),
                ('order_line.product_id.categ_id.name', 'in', categories),
                ('partner_id', '!=', record.partner_id.id if record.partner_id else False)
            ], limit=5)
            
            vendors = similar_orders.mapped('partner_id')
            
            # Format vendor suggestions
            suggestions = []
            for vendor in vendors:
                vendor_orders = similar_orders.filtered(lambda o: o.partner_id == vendor)
                performance = {
                    'on_time_delivery': sum(1 for o in vendor_orders if o.on_time_delivery) / len(vendor_orders) if vendor_orders else 0,
                    'quality_rating': vendor.quality_rating if hasattr(vendor, 'quality_rating') else None,
                    'avg_delay': sum((o.date_planned - o.date_order).days for o in vendor_orders) / len(vendor_orders) if vendor_orders else 0,
                }
                
                suggestions.append({
                    'name': vendor.name,
                    'categories': vendor.category_id.mapped('name'),
                    'performance': performance,
                    'recent_orders': len(vendor_orders),
                })
            
            record.ai_vendor_suggestions = json.dumps(suggestions, indent=2)
    
    def _compute_ai_negotiation_tips(self):
        """Generate negotiation tips based on vendor history"""
        for record in self:
            if not record.partner_id:
                record.ai_negotiation_tips = False
                continue
            
            # Analyze vendor history
            vendor_orders = self.env['purchase.order'].search([
                ('partner_id', '=', record.partner_id.id),
                ('state', '=', 'purchase')
            ])
            
            # Analyze pricing patterns
            price_history = {}
            for order in vendor_orders:
                for line in order.order_line:
                    product = line.product_id
                    if product not in price_history:
                        price_history[product] = []
                    price_history[product].append({
                        'date': order.date_order,
                        'price': line.price_unit,
                        'quantity': line.product_qty
                    })
            
            # Generate negotiation tips
            tips = []
            
            # Volume discount analysis
            for line in record.order_line:
                product = line.product_id
                if product in price_history:
                    prices = price_history[product]
                    avg_price = sum(p['price'] for p in prices) / len(prices)
                    if line.price_unit > avg_price:
                        tips.append(f"Historical average price for {product.name} is {avg_price:.2f}, "
                                  f"current price {line.price_unit:.2f} seems high")
            
            # Seasonal patterns
            current_month = record.date_order.month if record.date_order else datetime.now().month
            month_orders = vendor_orders.filtered(lambda o: o.date_order.month == current_month)
            if len(month_orders) > 3:
                tips.append("Vendor historically offers better rates during this month")
            
            record.ai_negotiation_tips = "\n".join(tips) if tips else False

    def action_ai_analyze_vendor(self):
        """Open AI assistant for vendor analysis"""
        self.ensure_one()
        return {
            'name': 'AI Vendor Analysis',
            'type': 'ir.actions.act_window',
            'res_model': 'ai.content.generator',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model_name': self._name,
                'default_res_id': self.id,
                'default_prompt_type': 'vendor_analysis',
                'default_context_data': self._get_ai_context(),
            }
        }

class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'ai.llm.mixin']
    
    def _get_ai_context(self):
        """Provide invoice-specific context for AI"""
        context = super()._get_ai_context()
        context_data = json.loads(context)
        context_data.update({
            'invoice_name': self.name,
            'partner_name': self.partner_id.name,
            'invoice_type': self.move_type,
            'state': self.state,
            'amount_total': self.amount_total,
            'currency': self.currency_id.name,
            'invoice_date': self.invoice_date.strftime('%Y-%m-%d') if self.invoice_date else '',
            'due_date': self.invoice_date_due.strftime('%Y-%m-%d') if self.invoice_date_due else '',
        })
        return json.dumps(context_data)
