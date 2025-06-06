# -*- coding: utf-8 -*-
from odoo import models, fields

class ArchitectSpecialization(models.Model):
    _name = 'architect.specialization'
    _description = 'Architect Specialization'

    name = fields.Char(string='Specialization', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
