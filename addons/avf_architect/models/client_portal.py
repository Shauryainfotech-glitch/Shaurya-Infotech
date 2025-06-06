# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ClientPortal(models.Model):
    _name = 'avf.client.portal'
    _description = 'Client Portal'
    _rec_name = 'name'

    name = fields.Char(string='Portal Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True)

    access_level = fields.Selection([
        ('view', 'View Only'),
        ('comment', 'View & Comment'),
        ('approve', 'View, Comment & Approve')
    ], string='Access Level', default='view')

    is_active = fields.Boolean(string='Active', default=True)
    last_login = fields.Datetime(string='Last Login')

    allowed_documents = fields.Many2many('avf.document.management', string='Allowed Documents')
    allowed_drawings = fields.Many2many('avf.drawing.management', string='Allowed Drawings')

    portal_url = fields.Char(string='Portal URL', compute='_compute_portal_url')

    @api.depends('project_id')
    def _compute_portal_url(self):
        for record in self:
            if record.project_id:
                record.portal_url = f"/my/project/{record.project_id.id}"
            else:
                record.portal_url = False