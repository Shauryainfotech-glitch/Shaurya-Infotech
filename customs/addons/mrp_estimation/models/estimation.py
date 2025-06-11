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
    # Removed _check_company_auto since we're not using company_id field

    # ======================
    # HEADER FIELDS
    # ======================

    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )

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

    # company_id = fields.Many2one(
    #     'res.company',
    #     string='Company',
    #     required=True,
    #     default=lambda self: self.env.company
    # )

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

    # New fields for enhanced functionality
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='1', tracking=True)

    tag_ids = fields.Many2many(
        'mrp.estimation.tag',
        string='Tags',
        help="Categorize estimations with tags"
    )

    expected_delivery_date = fields.Date(
        string='Expected Delivery',
        help="Expected delivery date for the manufactured product"
    )

    customer_reference = fields.Char(
        string='Customer Reference',
        help="Customer's internal reference for this estimation"
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

    days_to_expire = fields.Integer(
        string='Days to Expire',
        compute='_compute_days_to_expire',
        help="Number of days until this estimation expires"
    )

    is_expired = fields.Boolean(
        string='Is Expired',
        compute='_compute_days_to_expire',
        help="True if the estimation has expired"
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
        default=lambda self: self._get_default_material_markup(),
        help="Markup value for materials"
    )

    cost_markup_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage')
    ], string='Cost Markup Type', default='percentage')

    cost_markup_value = fields.Float(
        string='Cost Markup Value',
        default=lambda self: self._get_default_cost_markup(),
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

    attachment_count = fields.Integer(
        string='Attachments Count',
        compute='_compute_attachment_count'
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
    # DEFAULT VALUE METHODS
    # ======================

    def _get_default_material_markup(self):
        """Get default material markup from configuration"""
        return float(self.env['ir.config_parameter'].sudo().get_param(
            'mrp_estimation.default_material_markup', '10.0'
        ))

    def _get_default_cost_markup(self):
        """Get default cost markup from configuration"""
        return float(self.env['ir.config_parameter'].sudo().get_param(
            'mrp_estimation.default_cost_markup', '15.0'
        ))

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

    @api.constrains('material_markup_value', 'cost_markup_value')
    def _check_markup_values(self):
        for record in self:
            if record.material_markup_value < 0:
                raise ValidationError(_("Material markup value cannot be negative."))
            if record.cost_markup_value < 0:
                raise ValidationError(_("Cost markup value cannot be negative."))

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

    @api.depends('validity_date')
    def _compute_days_to_expire(self):
        today = fields.Date.today()
        for record in self:
            if record.validity_date:
                delta = record.validity_date - today
                record.days_to_expire = delta.days
                record.is_expired = delta.days < 0
            else:
                record.days_to_expire = 0
                record.is_expired = False

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

    def _compute_attachment_count(self):
        for record in self:
            record.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', self._name),
                ('res_id', '=', record.id)
            ])

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

    @api.onchange('material_markup_type')
    def _onchange_material_markup_type(self):
        if self.material_markup_type == 'percentage':
            self.material_markup_value = self._get_default_material_markup()
        else:
            self.material_markup_value = 0.0

    @api.onchange('cost_markup_type')
    def _onchange_cost_markup_type(self):
        if self.cost_markup_type == 'percentage':
            self.cost_markup_value = self._get_default_cost_markup()
        else:
            self.cost_markup_value = 0.0

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

    def unlink(self):
        for record in self:
            if record.state not in ['draft', 'cancel']:
                raise UserError(_("You cannot delete an estimation that is not in draft or cancelled state."))
        return super().unlink()

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

    def action_view_attachments(self):
        """View estimation attachments"""
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
        }

    def action_view_boms(self):
        """View related BOMs"""
        self.ensure_one()
        boms = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)
        ])
        return {
            'name': _('Bills of Materials'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'view_mode': 'list,form',
            'domain': [('id', 'in', boms.ids)],
            'context': {'default_product_tmpl_id': self.product_id.product_tmpl_id.id},
        }

    def action_view_manufacturing_orders(self):
        """View related manufacturing orders"""
        self.ensure_one()
        mos = self.env['mrp.production'].search([
            ('product_id', '=', self.product_id.id),
            ('origin', 'ilike', self.name)
        ])
        return {
            'name': _('Manufacturing Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'list,form',
            'domain': [('id', 'in', mos.ids)],
        }

    def action_view_sale_orders(self):
        """View related sale orders"""
        self.ensure_one()
        sales = self.env['sale.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('origin', 'ilike', self.name)
        ])
        return {
            'name': _('Sales Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', sales.ids)],
        }

    def action_view_versions(self):
        """View estimation versions"""
        self.ensure_one()
        return {
            'name': _('Estimation Versions'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.estimation.version',
            'view_mode': 'list,form',
            'domain': [('parent_estimation_id', '=', self.id)],
        }

    def action_create_version(self):
        """Create new version of estimation"""
        self.ensure_one()
        return {
            'name': _('Create New Version'),
            'type': 'ir.actions.act_window',
            'res_model': 'create.estimation.version.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_estimation_id': self.id,
                'active_id': self.id,
                'active_model': self._name,
            }
        }

    def action_create_bom(self):
        """Create BOM from estimation"""
        self.ensure_one()
        if not self.estimation_line_ids:
            raise UserError(_("Cannot create BOM without material lines."))

        bom_lines = []
        for line in self.estimation_line_ids:
            bom_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty / self.product_qty,  # Calculate per unit
                'product_uom_id': line.product_uom_id.id,
            }))

        bom = self.env['mrp.bom'].create({
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'product_qty': 1.0,
            'product_uom_id': self.product_uom_id.id,
            'bom_line_ids': bom_lines,
            'type': 'normal',
        })

        return {
            'name': _('Bill of Materials'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'res_id': bom.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_sale_order(self):
        """Create sale order from estimation"""
        self.ensure_one()

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'product_uom_qty': self.product_qty,
                'product_uom': self.product_uom_id.id,
                'price_unit': self.estimation_total / self.product_qty,
            })]
        })

        return {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_manufacturing_order(self):
        """Create manufacturing order from estimation"""
        self.ensure_one()

        # Check if BOM exists
        bom = self.env['mrp.bom']._bom_find(
            product=self.product_id,
            bom_type='normal'
        )

        if not bom:
            raise UserError(
                _("No Bill of Materials found for product %s. Please create a BOM first.") % self.product_id.name)

        mo = self.env['mrp.production'].create({
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.product_uom_id.id,
            'bom_id': bom.id,
            'origin': self.name,
        })

        return {
            'name': _('Manufacturing Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'res_id': mo.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # ======================
    # BUSINESS LOGIC METHODS
    # ======================

    def _auto_populate_from_bom(self):
        """Auto-populate estimation lines from existing BOM"""
        if not self.product_id:
            return

        bom = self.env['mrp.bom']._bom_find(
            product=self.product_id,
            bom_type='normal'
        )

        if bom:
            # Clear existing lines
            self.estimation_line_ids.unlink()

            # Create new lines from BOM
            lines = []
            for bom_line in bom.bom_line_ids:
                qty_needed = bom_line.product_qty * self.product_qty / bom.product_qty

                lines.append((0, 0, {
                    'product_id': bom_line.product_id.id,
                    'product_qty': qty_needed,
                    'product_uom_id': bom_line.product_uom_id.id,
                    'product_cost': bom_line.product_id.standard_price,
                }))

            self.estimation_line_ids = lines

    def _notify_approvers(self):
        """Notify approvers about pending estimation"""
        approvers = self.env['res.users'].search([
            ('groups_id', 'in', self.env.ref('mrp_estimation.group_estimation_manager').id)
        ])

        for approver in approvers:
            self.activity_schedule(
                'mrp_estimation.mail_activity_estimation_approval',
                user_id=approver.id,
                summary=_('Estimation Approval Required'),
                note=_('Please review and approve estimation %s') % self.name
            )

    # ======================
    # CRON METHODS
    # ======================

    @api.model
    def _check_expired_estimations(self):
        """Cron method to check and notify about expired estimations"""
        expired_estimations = self.search([
            ('validity_date', '<', fields.Date.today()),
            ('state', 'in', ['draft', 'waiting_approval', 'approved', 'sent'])
        ])

        for estimation in expired_estimations:
            estimation.message_post(
                body=_("This estimation has expired on %s") % estimation.validity_date,
                subtype_xmlid='mail.mt_note'
            )


class MrpEstimationTag(models.Model):
    """Tags for categorizing estimations"""
    _name = 'mrp.estimation.tag'
    _description = 'Estimation Tag'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color', default=10)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tag name must be unique!')
    ]