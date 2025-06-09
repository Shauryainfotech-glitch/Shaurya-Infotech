from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CreateEstimationVersionWizard(models.TransientModel):
    _name = 'create.estimation.version.wizard'
    _description = 'Create New Estimation Version'

    estimation_id = fields.Many2one(
        'mrp.estimation',
        string='Estimation',
        required=True,
        readonly=True
    )

    current_version = fields.Float(
        string='Current Version',
        readonly=True
    )

    new_version = fields.Float(
        string='New Version',
        readonly=True
    )

    version_notes = fields.Text(
        string='Version Notes',
        required=True,
        help="Describe the changes made in this version"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('active_model') == 'mrp.estimation' and \
                self.env.context.get('active_id'):
            estimation = self.env['mrp.estimation'].browse(self.env.context.get('active_id'))

            # Get version increment from settings
            version_increment = float(self.env['ir.config_parameter'].sudo().get_param(
                'mrp_estimation.version_increment', '0.1'
            ))

            res.update({
                'estimation_id': estimation.id,
                'current_version': estimation.version,
                'new_version': estimation.version + version_increment
            })
        return res

    def action_create_version(self):
        self.ensure_one()

        if not self.estimation_id:
            raise UserError(_("No estimation selected."))

        # Create version record
        self.env['mrp.estimation.version'].create({
            'parent_estimation_id': self.estimation_id.id,
            'version_number': self.current_version,
            'version_notes': self.version_notes,
            'created_by': self.env.user.id,
            'creation_date': fields.Datetime.now(),
        })

        # Copy estimation with new version
        new_estimation = self.estimation_id.copy({
            'name': self.estimation_id.name + ' v' + str(self.new_version),
            'version': self.new_version,
            'state': 'draft',
        })

        # Open the new estimation
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Version'),
            'res_model': 'mrp.estimation',
            'res_id': new_estimation.id,
            'view_mode': 'form',
            'target': 'current',
        }