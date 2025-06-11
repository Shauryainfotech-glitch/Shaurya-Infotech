from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging
import base64
import secrets

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

    # Portal access token for sharing
    access_token = fields.Char(
        string='Access Token',
        default=lambda self: self._generate_access_token(),
        copy=False
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

    # ======================
    # SMART BUTTON FIELDS
    # ======================

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
        string='Versions Count',
        compute='_compute_version_count'
    )

    # ======================
    # NOTES & DESCRIPTION
    # ======================

    notes = fields.Html(
        string='Internal Notes',
        help="Internal notes for this estimation"
    )

    customer_notes = fields.Html(
        string='Customer Notes',
        help="Notes visible to customer"
    )

    # ======================
    # PORTAL METHODS
    # ======================

    def _generate_access_token(self):
        """Generate a unique access token for portal sharing"""
        return secrets.token_urlsafe(32)

    def _get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """Get portal URL for this estimation"""
        self.ensure_one()
        url = f'/my/estimation/{self.id}'
        if suffix:
            url += f'/{suffix}'
        if download:
            url += '/download'
        if query_string:
            url += f'?{query_string}'
        if anchor:
            url += f'#{anchor}'
        return url

    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        """Public method to get portal URL"""
        return self._get_portal_url(suffix, report_type, download, query_string, anchor)

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
    # ONCHANGE METHODS
    # ======================

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
            # Auto-populate estimation lines from existing BOM if available
            self._auto_populate_from_bom()

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.property_product_pricelist:
            self.currency_id = self.partner_id.property_product_pricelist.currency_id

    # ======================
    # CRUD METHODS
    # ======================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('mrp.estimation') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        # Track state changes
        if 'state' in vals:
            for record in self:
                record.message_post(
                    body=_("State changed from %s to %s") % (
                        dict(record._fields['state'].selection)[record.state],
                        dict(record._fields['state'].selection)[vals['state']]
                    )
                )
        return super().write(vals)

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': _('Copy of %s') % self.name,
            'state': 'draft',
            'version': 1.0,
            'access_token': self._generate_access_token(),
        })
        return super().copy(default)

    # ======================
    # ACTION METHODS
    # ======================

    def action_submit_for_approval(self):
        """Submit estimation for approval"""
        if not self.estimation_line_ids:
            raise UserError(_("Cannot submit estimation without material lines."))

        self.state = 'waiting_approval'
        self.message_post(body=_("Estimation submitted for approval"))

        # Send notification to approvers
        self._notify_approvers()

    def action_approve(self):
        """Approve estimation"""
        if not self.env.user.has_group('mrp_estimation.group_estimation_manager'):
            raise UserError(_("Only estimation managers can approve estimations."))

        self.state = 'approved'
        self.message_post(body=_("Estimation approved by %s") % self.env.user.name)

    def action_reject(self):
        """Reject estimation back to draft"""
        self.state = 'draft'
        self.message_post(body=_("Estimation rejected back to draft"))

    def action_send_estimation(self):
        """Send estimation to customer"""
        self.ensure_one()

        # Generate PDF report
        report = self.env.ref('mrp_estimation.action_report_estimation')
        pdf_content = report._render_qweb_pdf([self.id])[0]

        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'Estimation_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        # Send email
        template = self.env.ref('mrp_estimation.email_template_estimation', raise_if_not_found=False)
        if template:
            template.attachment_ids = [(6, 0, [attachment.id])]
            template.send_mail(self.id, force_send=True)

        self.state = 'sent'
        self.message_post(body=_("Estimation sent to customer"))

    def action_confirm(self):
        """Confirm estimation"""
        self.state = 'confirmed'
        self.message_post(body=_("Estimation confirmed"))

    def action_cancel(self):
        """Cancel estimation"""
        self.state = 'cancel'
        self.message_post(body=_("Estimation cancelled"))

    def action_done(self):
        """Mark estimation as done"""
        self.state = 'done'
        self.message_post(body=_("Estimation completed"))

    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.state = 'draft'
        self.message_post(body=_("Estimation reset to draft"))

    def action_view_boms(self):
        """View related BOMs"""
        self.ensure_one()
        boms = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
        ])
        action = {
            'name': _('Bills of Materials'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', boms.ids)],
        }
        if len(boms) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': boms.id,
            })
        return action

    def action_view_manufacturing_orders(self):
        """View related manufacturing orders"""
        self.ensure_one()
        manufacturing_orders = self.env['mrp.production'].search([
            ('product_id', '=', self.product_id.id),
            ('origin', 'ilike', self.name)
        ])
        action = {
            'name': _('Manufacturing Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', manufacturing_orders.ids)],
        }
        if len(manufacturing_orders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': manufacturing_orders.id,
            })
        return action

    def action_view_sale_orders(self):
        """View related sale orders"""
        self.ensure_one()
        sale_orders = self.env['sale.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('origin', 'ilike', self.name)
        ])
        action = {
            'name': _('Sales Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', sale_orders.ids)],
        }
        if len(sale_orders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': sale_orders.id,
            })
        return action

    def action_view_versions(self):
        """View estimation versions"""
        self.ensure_one()
        action = {
            'name': _('Estimation Versions'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.estimation.version',
            'view_mode': 'tree,form',
            'domain': [('parent_estimation_id', '=', self.id)],
        }
        return action

    def action_create_version(self):
        """Create a new version of this estimation"""
        self.ensure_one()

        # Create version record for current estimation
        self.env['mrp.estimation.version'].create({
            'parent_estimation_id': self.id,
            'version_number': self.version,
            'version_notes': _('Version created automatically'),
            'created_by': self.env.user.id,
            'creation_date': fields.Datetime.now(),
        })

        # Get version increment from settings
        version_increment = float(self.env['ir.config_parameter'].sudo().get_param(
            'mrp_estimation.version_increment', '0.1'
        ))

        # Copy estimation with new version
        new_estimation = self.copy({
            'name': self.name + f' v{self.version + version_increment}',
            'version': self.version + version_increment,
            'state': 'draft',
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('New Version'),
            'res_model': 'mrp.estimation',
            'res_id': new_estimation.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_bom(self):
        """Create Bill of Materials from estimation."""
        self.ensure_one()

        if not self.product_id:
            raise UserError(_("Please select a product to manufacture before creating BOM."))

        # Check if BOM already exists
        existing_bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
            ('product_id', '=', self.product_id.id)
        ], limit=1)

        if existing_bom:
            raise UserError(_("A Bill of Materials already exists for this product."))

        # Create BOM
        bom_vals = {
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'product_id': self.product_id.id,
            'product_qty': 1.0,
            'type': 'normal',
            'code': self.name,
        }

        # Create BOM lines from estimation lines
        bom_line_vals = []
        for line in self.estimation_line_ids:
            bom_line_vals.append((0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom_id.id,
            }))

        bom_vals['bom_line_ids'] = bom_line_vals

        # Create the BOM
        bom = self.env['mrp.bom'].create(bom_vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Bill of Materials has been created successfully.'),
                'sticky': False,
                'type': 'success',
            }
        }

    def action_create_sale_order(self):
        """Create Sales Order from estimation."""
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_("Please select a customer before creating a sales order."))

        # Create sales order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'client_order_ref': self.name,
            'date_order': fields.Datetime.now(),
            'user_id': self.user_id.id,
            'company_id'