# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ComplianceCheckerWizard(models.TransientModel):
    _name = 'architect.compliance.checker.wizard'
    _description = 'Compliance Checker Wizard'

    project_id = fields.Many2one('architect.project', string='Project', required=True)
    compliance_type = fields.Selection([
        ('building', 'Building Codes'),
        ('environmental', 'Environmental Regulations'),
        ('accessibility', 'Accessibility Standards'),
        ('fire', 'Fire Safety'),
        ('fca', 'Forest Conservation Act'),
        ('ecotourism', 'Ecotourism Guidelines')
    ], string='Compliance Type', required=True)

    def check_compliance(self):
        # This would include actual compliance checking logic
        # For now, we'll create a placeholder compliance record

        vals = {
            'name': f"{self.compliance_type.capitalize()} Compliance Check",
            'project_id': self.project_id.id,
            'compliance_type': self.compliance_type,
            'state': 'draft',
        }

        compliance = self.env['architect.compliance'].create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Compliance Results',
            'res_model': 'architect.compliance',
            'view_mode': 'form',
            'res_id': compliance.id,
            'target': 'current',
        }
