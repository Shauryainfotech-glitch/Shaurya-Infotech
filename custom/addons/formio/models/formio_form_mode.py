# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class FormioFormMode(models.Model):
    _name = 'formio.form.mode'
    _description = 'Form.io Form Mode'

    name = fields.Char(string='Mode', required=True)
    action_id = fields.Many2one('ir.actions.act_window.view', string='Action View')