# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DprGeneratorWizard(models.TransientModel):
    _name = 'architect.dpr.generator.wizard'
    _description = 'DPR Generator Wizard'

    project_id = fields.Many2one('architect.project', string='Project', required=True)
    dpr_type = fields.Selection([
        ('preliminary', 'Preliminary DPR'),
        ('detailed', 'Detailed DPR'),
        ('final', 'Final DPR')
    ], string='DPR Type', required=True)
    include_financials = fields.Boolean(string='Include Financial Analysis', default=True)
    include_drawings = fields.Boolean(string='Include Drawings', default=True)
    include_compliance = fields.Boolean(string='Include Compliance Reports', default=True)

    def generate_dpr(self):
        # Logic to generate DPR would go here
        vals = {
            'name': f"{self.dpr_type.capitalize()} DPR - {self.project_id.name}",
            'project_id': self.project_id.id,
            'dpr_type': self.dpr_type,
            'state': 'draft',
        }

        dpr = self.env['architect.dpr'].create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Generated DPR',
            'res_model': 'architect.dpr',
            'view_mode': 'form',
            'res_id': dpr.id,
            'target': 'current',
        }
