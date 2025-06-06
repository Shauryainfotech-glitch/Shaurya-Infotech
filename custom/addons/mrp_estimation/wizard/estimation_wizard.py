from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CreateEstimationFromBomWizard(models.TransientModel):
    _name = 'create.estimation.from.bom.wizard'
    _description = 'Create Estimation from BOM'

    bom_id = fields.Many2one('mrp.bom', string='Bill of Materials', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity', required=True, default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        if self.bom_id:
            self.product_id = self.bom_id.product_id
            self.product_uom_id = self.bom_id.product_uom_id

    def action_create_estimation(self):
        self.ensure_one()
        Estimation = self.env['mrp.estimation']
        
        # Create estimation
        estimation = Estimation.create({
            'name': self.env['ir.sequence'].next_by_code('mrp.estimation'),
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.product_uom_id.id,
            'partner_id': self.partner_id.id,
            'bom_id': self.bom_id.id,
        })

        # Create material lines
        for line in self.bom_id.bom_line_ids:
            self.env['mrp.estimation.material'].create({
                'estimation_id': estimation.id,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty * self.product_qty,
                'product_uom_id': line.product_uom_id.id,
                'cost_price': line.product_id.standard_price,
            })

        # Create operation lines
        for operation in self.bom_id.operation_ids:
            self.env['mrp.estimation.operation'].create({
                'estimation_id': estimation.id,
                'workcenter_id': operation.workcenter_id.id,
                'name': operation.name,
                'time_cycle': operation.time_cycle,
                'sequence': operation.sequence,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.estimation',
            'view_mode': 'form',
            'res_id': estimation.id,
        }

class CreateMoFromEstimationWizard(models.TransientModel):
    _name = 'create.mo.from.estimation.wizard'
    _description = 'Create Manufacturing Order from Estimation'

    estimation_id = fields.Many2one('mrp.estimation', string='Estimation', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_qty = fields.Float(string='Quantity', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    date_planned_start = fields.Datetime(string='Scheduled Date', required=True)
    date_planned_finished = fields.Datetime(string='Scheduled End Date', required=True)

    @api.onchange('estimation_id')
    def _onchange_estimation_id(self):
        if self.estimation_id:
            self.product_id = self.estimation_id.product_id
            self.product_qty = self.estimation_id.product_qty
            self.product_uom_id = self.estimation_id.product_uom_id

    def action_create_mo(self):
        self.ensure_one()
        if not self.estimation_id.bom_id:
            raise UserError(_('No Bill of Materials found on the estimation.'))

        # Create manufacturing order
        mo = self.env['mrp.production'].create({
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.product_uom_id.id,
            'bom_id': self.estimation_id.bom_id.id,
            'date_planned_start': self.date_planned_start,
            'date_planned_finished': self.date_planned_finished,
            'estimation_id': self.estimation_id.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'res_id': mo.id,
        }

class CreateSoFromEstimationWizard(models.TransientModel):
    _name = 'create.so.from.estimation.wizard'
    _description = 'Create Sale Order from Estimation'

    estimation_id = fields.Many2one('mrp.estimation', string='Estimation', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    date_order = fields.Datetime(string='Order Date', required=True, default=fields.Datetime.now)

    @api.onchange('estimation_id')
    def _onchange_estimation_id(self):
        if self.estimation_id:
            self.partner_id = self.estimation_id.partner_id

    def action_create_so(self):
        self.ensure_one()
        
        # Create sale order
        so = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'payment_term_id': self.payment_term_id.id,
            'date_order': self.date_order,
            'estimation_id': self.estimation_id.id,
        })

        # Create sale order line
        self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': self.estimation_id.product_id.id,
            'product_uom_qty': self.estimation_id.product_qty,
            'product_uom': self.estimation_id.product_uom_id.id,
            'price_unit': self.estimation_id.total_cost,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': so.id,
        } 