# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import hashlib
import mimetypes

class DocumentManagement(models.Model):
    _name = 'avf.document.management'
    _description = 'Document Management'
    _rec_name = 'name'

    name = fields.Char(string='Document Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)

    document_type = fields.Selection([
        ('contract', 'Contract'),
        ('drawing', 'Drawing'),
        ('specification', 'Specification'),
        ('report', 'Report'),
        ('permit', 'Permit'),
        ('certificate', 'Certificate')
    ], string='Document Type', required=True)

    document_file = fields.Binary(string='Document File')
    filename = fields.Char(string='Filename')
    file_size = fields.Integer(string='File Size')
    mime_type = fields.Char(string='MIME Type')

    version = fields.Char(string='Version', default='1.0')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('archived', 'Archived')
    ], string='Status', default='draft')

    upload_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now)
    expiry_date = fields.Date(string='Expiry Date')

    tags = fields.Many2many('avf.document.tag', string='Tags')
    description = fields.Text(string='Description')

class DocumentTag(models.Model):
    _name = 'avf.document.tag'
    _description = 'Document Tag'
    _rec_name = 'name'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color')

class ArchitectDocumentCategory(models.Model):
    _name = 'architect.document.category'
    _description = 'Document Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Category Code')
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    parent_id = fields.Many2one('architect.document.category', string='Parent Category')
    child_ids = fields.One2many('architect.document.category', 'parent_id', 
                               string='Child Categories')

    # Configuration
    allowed_file_types = fields.Char(string='Allowed File Types',
                                   help="Comma-separated list of allowed file extensions")
    max_file_size = fields.Integer(string='Max File Size (MB)', default=50)

    active = fields.Boolean(default=True)


class ArchitectDocumentSubcategory(models.Model):
    _name = 'architect.document.subcategory'
    _description = 'Document Subcategory'
    _order = 'category_id, sequence, name'

    name = fields.Char(string='Subcategory Name', required=True)
    category_id = fields.Many2one('architect.document.category', string='Category', 
                                 required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)

    active = fields.Boolean(default=True)


class ArchitectDocumentTag(models.Model):
    _name = 'architect.document.tag'
    _description = 'Document Tag'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class ArchitectDocumentTemplate(models.Model):
    _name = 'architect.document.template'
    _description = 'Document Template'

    name = fields.Char(string='Template Name', required=True)
    document_type = fields.Selection([
        ('drawing', 'Drawing'),
        ('specification', 'Specification'),
        ('report', 'Report'),
        ('contract', 'Contract'),
        ('other', 'Other')
    ], string='Document Type', required=True)

    # Template File
    template_file = fields.Binary(string='Template File', attachment=True)
    template_filename = fields.Char(string='Template Filename')

    # Configuration
    description = fields.Text(string='Description')
    instructions = fields.Html(string='Usage Instructions')

    # Metadata Template
    default_category_id = fields.Many2one('architect.document.category', 
                                        string='Default Category')
    default_tags = fields.Many2many('architect.document.tag', string='Default Tags')

    active = fields.Boolean(default=True)
    usage_count = fields.Integer(string='Usage Count', default=0)

    def use_template(self):
        """Create a new document from this template"""
        self.usage_count += 1
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Document from Template'),
            'res_model': 'architect.document',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': f"New {self.name}",
                'default_document_type': self.document_type,
                'default_category_id': self.default_category_id.id,
                'default_tag_ids': [(6, 0, self.default_tags.ids)],
                'template_file': self.template_file,
                'template_filename': self.template_filename
            }
        }

class ArchitectDocument(models.Model):
    _name = 'architect.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Document'
    _order = 'project_id, category_id, name'

    name = fields.Char(string='Document Name', required=True, tracking=True)
    project_id = fields.Many2one('project.project', string='Project', required=True, tracking=True)
    category_id = fields.Many2one('architect.document.category', string='Category', tracking=True)
    subcategory_id = fields.Many2one('architect.document.subcategory', string='Subcategory', tracking=True)

    # Document file handling
    attachment_id = fields.Many2one('ir.attachment', string='Document File', ondelete='cascade')
    file_name = fields.Char(string='File Name', related='attachment_id.name', readonly=True)
    file_size = fields.Integer(string='File Size', related='attachment_id.file_size', readonly=True)
    file_type = fields.Char(string='File Type', related='attachment_id.mimetype', readonly=True)

    # Document details
    version = fields.Char(string='Version', default='1.0', tracking=True)
    description = fields.Text(string='Description')
    tags = fields.Char(string='Tags', help="Comma-separated tags for easy searching")

    # Status and workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived')
    ], string='Status', default='draft', tracking=True)

    # Dates
    submission_date = fields.Date(string='Submission Date', tracking=True)
    approval_date = fields.Date(string='Approval Date', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)

    # Responsible persons
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By', tracking=True)

    # Compliance and certification
    is_compliance_doc = fields.Boolean(string='Compliance Document')
    compliance_type = fields.Selection([
        ('fca', 'Forest Conservation Act'),
        ('environmental', 'Environmental Clearance'),
        ('fire_safety', 'Fire Safety'),
        ('building_code', 'Building Code'),
        ('accessibility', 'Accessibility Standards')
    ], string='Compliance Type')

    # Additional fields
    confidential = fields.Boolean(string='Confidential')
    shared_with_client = fields.Boolean(string='Shared with Client')
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if 'submission_date' not in vals and vals.get('state') == 'submitted':
            vals['submission_date'] = fields.Date.today()
        return super().create(vals)

    def action_submit(self):
        self.write({
            'state': 'submitted',
            'submission_date': fields.Date.today()
        })

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approval_date': fields.Date.today(),
            'approved_by': self.env.user.id
        })

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_archive(self):
        self.write({'state': 'archived'})

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            return {'domain': {'subcategory_id': [('category_id', '=', self.category_id.id)]}}
        else:
            return {'domain': {'subcategory_id': []}}