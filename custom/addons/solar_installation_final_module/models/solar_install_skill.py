# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SolarInstallSkill(models.Model):
    _name = "solar.install.skill"
    _description = "Installation Skill / Certification"

    name = fields.Char(
        string="Skill Name",
        required=True
    )
    code = fields.Char(
        string="Skill Code",
        required=True,
    )
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The Skill Code must be unique.'),
    ]

    @api.constrains('code')
    def _check_code_unique(self):
        for record in self:
            existing = self.search([
                ('code', '=', record.code),
                ('id', '!=', record.id),
            ])
            if existing:
                raise ValidationError("Skill Code must be unique.")