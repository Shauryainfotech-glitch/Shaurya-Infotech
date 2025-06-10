# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ArchitectDrawing(models.Model):
    _name = 'architect.drawing'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']
    _description = 'Architectural Drawing'
    _order = 'create_date desc'

    name = fields.Char(string='Drawing Title', required=True, tracking=True)
    code = fields.Char(string='Drawing Number', required=True, copy=False, tracking=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    # Drawing Details
    drawing_type = fields.Selection([
        ('concept', 'Concept Drawing'),
        ('preliminary', 'Preliminary Drawing'),
        ('working', 'Working Drawing'),
        ('detail', 'Detail Drawing'),
        ('shop', 'Shop Drawing'),
        ('asbuilt', 'As-Built Drawing')
    ], string='Drawing Type', required=True)
    
    scale = fields.Char(string='Scale')
    revision = fields.Char(string='Revision', default='A')
    sheet_size = fields.Selection([
        ('a0', 'A0'),
        ('a1', 'A1'),
        ('a2', 'A2'),
        ('a3', 'A3'),
        ('a4', 'A4'),
        ('custom', 'Custom')
    ], string='Sheet Size', default='a1')
    custom_size = fields.Char(string='Custom Size')
    
    # Status and Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('revision', 'Needs Revision'),
        ('obsolete', 'Obsolete')
    ], string='Status', default='draft', tracking=True)
    
    # Dates
    create_date = fields.Datetime(string='Created On', readonly=True)
    approval_date = fields.Date(string='Approval Date')
    revision_date = fields.Date(string='Last Revision Date')
    
    # Team
    designer_id = fields.Many2one('res.users', string='Designer', 
                                 default=lambda self: self.env.user)
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    approver_id = fields.Many2one('res.users', string='Approver')
    
    # File Management
    drawing_file = fields.Binary(string='Drawing File', attachment=True)
    file_name = fields.Char(string='File Name')
    file_type = fields.Selection([
        ('dwg', 'AutoCAD DWG'),
        ('dxf', 'AutoCAD DXF'),
        ('pdf', 'PDF'),
        ('rvt', 'Revit RVT'),
        ('skp', 'SketchUp SKP'),
        ('other', 'Other')
    ], string='File Type')
    
    # Version Control
    version = fields.Integer(string='Version', default=1)
    previous_version_id = fields.Many2one('architect.drawing', string='Previous Version')
    is_latest_version = fields.Boolean(string='Latest Version', default=True)
    
    # Drawing Set
    drawing_set_id = fields.Many2one('architect.drawing.set', string='Drawing Set')
    sequence_in_set = fields.Integer(string='Sequence in Set')
    
    # References
    reference_drawings = fields.Many2many('architect.drawing', 
                                        'drawing_reference_rel',
                                        'drawing_id',
                                        'reference_id',
                                        string='Reference Drawings')
    
    # Portal Display
    website_published = fields.Boolean(string='Published', 
                                     help="Make this drawing visible on the portal")
    access_token = fields.Char(string='Access Token')
    
    # Search and Filter
    tags = fields.Many2many('architect.drawing.tag', string='Tags')
    discipline = fields.Selection([
        ('architectural', 'Architectural'),
        ('structural', 'Structural'),
        ('mechanical', 'Mechanical'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('interior', 'Interior'),
        ('landscape', 'Landscape')
    ], string='Discipline')
    
    _sql_constraints = [
        ('unique_code_company', 'unique(code, company_id)', 
         'Drawing number must be unique per company!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'code' not in vals or not vals['code']:
                vals['code'] = self.env['ir.sequence'].next_by_code('architect.drawing')
            if not vals.get('access_token'):
                vals['access_token'] = self._generate_access_token()
        return super().create(vals_list)
    
    def _generate_access_token(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'database.secret', 'secret')[:16]
    
    @api.onchange('sheet_size')
    def _onchange_sheet_size(self):
        if self.sheet_size != 'custom':
            self.custom_size = False
    
    def action_submit_for_review(self):
        self.ensure_one()
        if not self.reviewer_id:
            raise ValidationError(_("Please assign a reviewer before submitting."))
        self.write({
            'state': 'review',
            'revision_date': fields.Date.today()
        })
        self.message_post(body=_("Drawing submitted for review."))
    
    def action_approve(self):
        self.ensure_one()
        self.write({
            'state': 'approved',
            'approval_date': fields.Date.today(),
            'approver_id': self.env.user.id
        })
        self.message_post(body=_("Drawing approved."))
    
    def action_request_revision(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Request Revision'),
            'res_model': 'architect.drawing.revision.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_drawing_id': self.id}
        }
    
    def create_new_version(self):
        self.ensure_one()
        self.is_latest_version = False
        new_version = self.copy({
            'version': self.version + 1,
            'previous_version_id': self.id,
            'state': 'draft',
            'approval_date': False,
            'approver_id': False,
            'is_latest_version': True
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Version'),
            'res_model': 'architect.drawing',
            'res_id': new_version.id,
            'view_mode': 'form',
            'target': 'current'
        }


class ArchitectDrawingSet(models.Model):
    _name = 'architect.drawing.set'
    _description = 'Drawing Set'
    _inherit = ['mail.thread']

    name = fields.Char(string='Set Name', required=True)
    project_id = fields.Many2one('architect.project', string='Project', required=True)
    description = fields.Text(string='Description')
    drawing_ids = fields.One2many('architect.drawing', 'drawing_set_id', string='Drawings')
    drawing_count = fields.Integer(compute='_compute_drawing_count', store=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True
    )

    @api.depends('drawing_ids')
    def _compute_drawing_count(self):
        for record in self:
            record.drawing_count = len(record.drawing_ids)


class ArchitectDrawingTag(models.Model):
    _name = 'architect.drawing.tag'
    _description = 'Drawing Tag'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]
