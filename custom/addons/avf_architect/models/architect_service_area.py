# -*- coding: utf-8 -*-
from odoo import models, fields

class ArchitectServiceArea(models.Model):
    _name = 'architect.service.area'
    _description = 'Architect Service Area'

    name = fields.Char(string='Service Area', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
