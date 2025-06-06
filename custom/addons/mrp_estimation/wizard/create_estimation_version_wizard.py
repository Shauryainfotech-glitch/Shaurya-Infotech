from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CreateEstimationVersionWizard(models.TransientModel):
    _name = 'create.estimation.version.wizard'
    _description = 'Create Estimation Version'

    estimation_id = fields.Many2one('mrp.estimation', string='Estimation', required=True)
    version_number = fields.Char(string='Version Number', required=True)
    notes = fields.Text(string='Version Notes')
    copy_materials = fields.Boolean(string='Copy Materials', default=True)
    copy_operations = fields.Boolean(string='Copy Operations', default=True)
    copy_overhead = fields.Boolean(string='Copy Overhead', default=True)

    @api.onchange('estimation_id')
    def _onchange_estimation_id(self):
        if self.estimation_id:
            # Get the next version number
            last_version = self.env['mrp.estimation.version'].search([
                ('estimation_id', '=', self.estimation_id.id)
            ], order='version_number desc', limit=1)
            
            if last_version:
                try:
                    current_version = float(last_version.version_number)
                    self.version_number = str(current_version + 0.1)
                except ValueError:
                    self.version_number = '1.0'
            else:
                self.version_number = '1.0'

    def action_create_version(self):
        self.ensure_one()
        
        # Create new version
        version = self.env['mrp.estimation.version'].create({
            'estimation_id': self.estimation_id.id,
            'version_number': self.version_number,
            'notes': self.notes,
            'created_by': self.env.user.id,
        })

        # Copy materials if requested
        if self.copy_materials:
            for material in self.estimation_id.material_ids:
                self.env['mrp.estimation.material'].create({
                    'estimation_id': self.estimation_id.id,
                    'version_id': version.id,
                    'product_id': material.product_id.id,
                    'product_qty': material.product_qty,
                    'product_uom_id': material.product_uom_id.id,
                    'cost_price': material.cost_price,
                })

        # Copy operations if requested
        if self.copy_operations:
            for operation in self.estimation_id.operation_ids:
                self.env['mrp.estimation.operation'].create({
                    'estimation_id': self.estimation_id.id,
                    'version_id': version.id,
                    'workcenter_id': operation.workcenter_id.id,
                    'name': operation.name,
                    'time_cycle': operation.time_cycle,
                    'sequence': operation.sequence,
                })

        # Copy overhead if requested
        if self.copy_overhead:
            for overhead in self.estimation_id.overhead_ids:
                self.env['mrp.estimation.overhead'].create({
                    'estimation_id': self.estimation_id.id,
                    'version_id': version.id,
                    'name': overhead.name,
                    'amount': overhead.amount,
                    'type': overhead.type,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.estimation.version',
            'view_mode': 'form',
            'res_id': version.id,
        }
