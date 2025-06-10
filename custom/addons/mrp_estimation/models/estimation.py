from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging
import base64

_logger = logging.getLogger(__name__)


class MrpEstimation(models.Model):
    _name = 'mrp.estimation'
    _description = 'Manufacturing Estimation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'name desc'
    _rec_name = 'name'

    # ======================
    # HEADER FIELDS
    # ======================

    name = fields.Char(
        string='Estimation Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        domain=[('is_company', '=', True)]
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product to Manufacture',
        required=True,
        tracking=True,
        domain=[('type', 'in', ['product', 'consu'])]
    )

    product_qty = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        tracking=True,
        digits='Product Unit of Measure'
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
        tracking=True
    )

    estimation_date = fields.Date(
        string='Estimation Date',
        required=True,
        default=fields.Date.today,
        tracking=True
    )

    validity_date = fields.Date(
        string='Valid Until',
        tracking=True,
        help="Date until this estimation is valid"
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('sent', 'Sent to Customer'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    version = fields.Float(
        string='Version',
        default=1.0,
        tracking=True,
        help="Version number of this estimation"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True
    )

    # ======================
    # ONE2MANY RELATIONS
    # ======================

    estimation_line_ids = fields.One2many(
        'mrp.estimation.line',
        'estimation_id',
        string='Material Lines'
    )

    estimation_cost_ids = fields.One2many(
        'mrp.estimation.cost',
        'estimation_id',
        string='Cost Breakdown'
    )

    version_ids = fields.One2many(
        'mrp.estimation.version',
        'parent_estimation_id',
        string='Versions'
    )

    # ======================
    # COMPUTED FIELDS
    # ======================

    material_total = fields.Monetary(
        string='Material Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )

    cost_total = fields.Monetary(
        string='Cost Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )

    markup_total = fields.Monetary(
        string='Markup Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )

    estimation_total = fields.Monetary(
        string='Estimation Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )

    # MISSING COMPUTED FIELDS - ADDED
    bom_count = fields.Integer(
        string='BOM Count',
        compute='_compute_bom_count'
    )

    mo_count = fields.Integer(
        string='Manufacturing Orders Count',
        compute='_compute_mo_count'
    )

    so_count = fields.Integer(
        string='Sales Orders Count',
        compute='_compute_so_count'
    )

    version_count = fields.Integer(
        string='Version Count',
        compute='_compute_version_count'
    )

    # ======================
    # MARKUP FIELDS
    # ======================

    material_markup_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Material Markup Type', default='percentage')

    material_markup_value = fields.Float(
        string='Material Markup Value',
        default=0.0,
        help="Markup value for materials"
    )

    cost_markup_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Cost Markup Type', default='percentage')

    cost_markup_value = fields.Float(
        string='Cost Markup Value',
        default=0.0,
        help="Markup value for costs"
    )

    # MISSING FIELDS - ADDED
    notes = fields.Text(string='Internal Notes')
    customer_notes = fields.Text(string='Customer Notes')

    # ======================
    # CREATE METHOD - ADDED SEQUENCE GENERATION
    # ======================

    @api.model_create_multi
    def create(self, vals_list):
        """Create method that supports batch creation (Odoo 18 standard)"""
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        # Process each vals dict for sequence generation
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('mrp.estimation') or _('New')

        return super().create(vals_list)
    # ======================
    # COMPUTED METHODS
    # ======================

    @api.depends('estimation_line_ids.subtotal', 'estimation_cost_ids.total_cost',
                 'material_markup_type', 'material_markup_value',
                 'cost_markup_type', 'cost_markup_value')
    def _compute_totals(self):
        for record in self:
            # Material total
            record.material_total = sum(record.estimation_line_ids.mapped('subtotal'))

            # Cost total
            record.cost_total = sum(record.estimation_cost_ids.mapped('total_cost'))

            # Markup calculation
            material_markup = 0.0
            if record.material_markup_type == 'percentage':
                material_markup = record.material_total * (record.material_markup_value / 100)
            else:
                material_markup = record.material_markup_value

            cost_markup = 0.0
            if record.cost_markup_type == 'percentage':
                cost_markup = record.cost_total * (record.cost_markup_value / 100)
            else:
                cost_markup = record.cost_markup_value

            record.markup_total = material_markup + cost_markup
            record.estimation_total = record.material_total + record.cost_total + record.markup_total

    @api.depends('product_id')
    def _compute_bom_count(self):
        for record in self:
            if record.product_id:
                record.bom_count = self.env['mrp.bom'].search_count([
                    ('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)
                ])
            else:
                record.bom_count = 0

    @api.depends('product_id')
    def _compute_mo_count(self):
        for record in self:
            if record.product_id:
                record.mo_count = self.env['mrp.production'].search_count([
                    ('product_id', '=', record.product_id.id),
                    ('origin', 'ilike', record.name)
                ])
            else:
                record.mo_count = 0

    @api.depends('partner_id')
    def _compute_so_count(self):
        for record in self:
            if record.partner_id:
                record.so_count = self.env['sale.order'].search_count([
                    ('partner_id', '=', record.partner_id.id),
                    ('origin', 'ilike', record.name)
                ])
            else:
                record.so_count = 0

    def _compute_version_count(self):
        for record in self:
            record.version_count = len(record.version_ids)

    # ======================
    # CONSTRAINTS & VALIDATION
    # ======================

    @api.constrains('product_qty')
    def _check_product_qty(self):
        for record in self:
            if record.product_qty <= 0:
                raise ValidationError(_("Product quantity must be greater than zero."))

    @api.constrains('validity_date')
    def _check_validity_date(self):
        for record in self:
            if record.validity_date and record.validity_date < record.estimation_date:
                raise ValidationError(_("Validity date cannot be earlier than estimation date."))

    @api.constrains('material_markup_value')
    def _check_material_markup_value(self):
        for record in self:
            if record.material_markup_type == 'percentage' and record.material_markup_value < -100:
                raise ValidationError(_("Material markup percentage cannot be less than -100%."))
            elif record.material_markup_type == 'fixed' and record.material_markup_value < 0:
                raise ValidationError(_("Fixed material markup cannot be negative."))

    @api.constrains('cost_markup_value')
    def _check_cost_markup_value(self):
        for record in self:
            if record.cost_markup_type == 'percentage' and record.cost_markup_value < -100:
                raise ValidationError(_("Cost markup percentage cannot be less than -100%."))
            elif record.cost_markup_type == 'fixed' and record.cost_markup_value < 0:
                raise ValidationError(_("Fixed cost markup cannot be negative."))

    @api.constrains('version')
    def _check_version(self):
        for record in self:
            if record.version <= 0:
                raise ValidationError(_("Version number must be greater than zero."))

    # ======================
    # ACTION METHODS
    # ======================

    def action_submit_for_approval(self):
        """Submit estimation for approval"""
        for record in self:
            if not record.estimation_line_ids:
                raise UserError(_("Cannot submit estimation without material lines."))

            record.state = 'waiting_approval'
            record.message_post(body=_("Estimation submitted for approval"))

            # Send notification to approvers
            record._notify_approvers()
        return True

    def action_approve(self):
        """Approve estimation"""
        for record in self:
            if not self.env.user.has_group('mrp_estimation.group_estimation_manager'):
                raise UserError(_("Only estimation managers can approve estimations."))

            record.state = 'approved'
            record.message_post(body=_("Estimation approved by %s") % self.env.user.name)
        return True

    def action_send_estimation(self):
        """Send estimation to customer"""
        for record in self:
            try:
                # Generate PDF report
                report = self.env.ref('mrp_estimation.action_report_estimation', raise_if_not_found=False)
                if report:
                    pdf_content, content_type = report._render_qweb_pdf([record.id])

                    # Create attachment
                    attachment = self.env['ir.attachment'].create({
                        'name': f'Estimation_{record.name}.pdf',
                        'type': 'binary',
                        'datas': base64.b64encode(pdf_content),
                        'res_model': record._name,
                        'res_id': record.id,
                        'mimetype': 'application/pdf'
                    })

                    # Send email
                    template = self.env.ref('mrp_estimation.email_template_estimation', raise_if_not_found=False)
                    if template:
                        template.attachment_ids = [(6, 0, [attachment.id])]
                        template.send_mail(record.id, force_send=True)

            except Exception as e:
                _logger.warning(f"Could not send estimation PDF: {e}")

            record.state = 'sent'
            record.message_post(body=_("Estimation sent to customer"))
        return True

    # MISSING METHODS - ADDED
    def action_confirm(self):
        """Confirm estimation"""
        for record in self:
            record.state = 'confirmed'
            record.message_post(body=_("Estimation confirmed"))
        return True

    def action_done(self):
        """Mark estimation as done"""
        for record in self:
            record.state = 'done'
            record.message_post(body=_("Estimation completed"))
        return True

    def action_cancel(self):
        """Cancel estimation"""
        for record in self:
            record.state = 'cancel'
            record.message_post(body=_("Estimation cancelled"))
        return True

    def action_reset_to_draft(self):
        """Reset estimation to draft"""
        for record in self:
            record.state = 'draft'
            record.message_post(body=_("Estimation reset to draft"))
        return True

    def action_view_versions(self):
        """View estimation versions"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Estimation Versions',
            'res_model': 'mrp.estimation.version',
            'view_mode': 'list,form',
            'domain': [('parent_estimation_id', '=', self.id)],
            'context': {'default_parent_estimation_id': self.id}
        }

    def action_view_boms(self):
        """View related BOMs"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bills of Materials',
            'res_model': 'mrp.bom',
            'view_mode': 'list,form',
            'domain': [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)],
        }

    def action_view_manufacturing_orders(self):
        """View related Manufacturing Orders"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing Orders',
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'domain': [('product_id', '=', self.product_id.id), ('origin', 'ilike', self.name)],
        }

    def action_view_sale_orders(self):
        """View related Sales Orders"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id), ('origin', 'ilike', self.name)],
        }

    # ======================
    # HELPER METHODS
    # ======================

    def _notify_approvers(self):
        """Send notification to approvers"""
        try:
            approver_group = self.env.ref('mrp_estimation.group_estimation_manager', raise_if_not_found=False)
            if approver_group:
                approvers = approver_group.users
                for approver in approvers:
                    self.activity_schedule(
                        'mrp_estimation.mail_activity_estimation_approval',
                        user_id=approver.id,
                        summary=f'Estimation {self.name} needs approval'
                    )
        except Exception as e:
            _logger.warning(f"Could not notify approvers: {e}")

    # ======================
    # ONCHANGE METHODS
    # ======================

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.currency_id = self.partner_id.property_product_pricelist.currency_id or self.env.company.currency_id