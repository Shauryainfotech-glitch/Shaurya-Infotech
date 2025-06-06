# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import hashlib
import mimetypes

class DocumentAttachment(models.Model):
    _name = 'architect.document.attachment'
    _description = 'Document Attachment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Name', required=True)
    file = fields.Binary(string='File', attachment=True, required=True)
    file_name = fields.Char(string='File Name')
    file_size = fields.Integer(string='File Size (bytes)', compute='_compute_file_info', store=True)
    file_type = fields.Char(string='File Type', compute='_compute_file_info', store=True)
    mime_type = fields.Char(string='MIME Type', compute='_compute_file_info', store=True)
    res_model = fields.Char('Resource Model', help='The database object this attachment will be attached to')
    res_id = fields.Integer('Resource ID', help='The record id this attachment will be attached to')
    checksum = fields.Char(string='File Checksum', compute='_compute_checksum', store=True)
    description = fields.Text('Description')
    create_date = fields.Datetime('Created on', readonly=True)
    create_uid = fields.Many2one('res.users', string='Created by', readonly=True)

    @api.depends('file', 'file_name')
    def _compute_file_info(self):
        for attachment in self:
            if attachment.file and attachment.file_name:
                # Get file size (approximate from base64)
                attachment.file_size = len(attachment.file) * 3 / 4 if attachment.file else 0

                # Get file type and MIME type
                file_ext = attachment.file_name.split('.')[-1].lower() if '.' in attachment.file_name else ''
                attachment.file_type = file_ext
                attachment.mime_type = mimetypes.guess_type(attachment.file_name)[0] or 'application/octet-stream'
            else:
                attachment.file_size = 0
                attachment.file_type = ''
                attachment.mime_type = ''

    @api.depends('file')
    def _compute_checksum(self):
        for attachment in self:
            if attachment.file:
                attachment.checksum = hashlib.md5(attachment.file).hexdigest()
            else:
                attachment.checksum = ''
