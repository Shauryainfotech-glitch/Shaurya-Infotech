# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64

class ArchitectDrawing(models.Model):
    _name = 'avf.drawing.management'
    _description = 'Drawing Management'
    _rec_name = 'name'
    _order = 'sequence, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Drawing Name', required=True)
    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    drawing_number = fields.Char(string='Drawing Number', required=True)
    drawing_type = fields.Selection([
        ('plan', 'Floor Plan'),
        ('elevation', 'Elevation'),
        ('section', 'Section'),
        ('detail', 'Detail'),
        ('site_plan', 'Site Plan'),
        ('3d_view', '3D View'),
        ('working', 'Working Drawing'),
        ('presentation', 'Presentation Drawing')
    ], string='Drawing Type', required=True)

    # File management
    drawing_file = fields.Binary(string='Drawing File', attachment=True)
    drawing_filename = fields.Char(string='Filename')
    drawing_url = fields.Char(string='External URL')

    # Drawing properties
    scale = fields.Char(string='Scale', default='1:100')
    sheet_size = fields.Selection([
        ('A0', 'A0 (841 × 1189 mm)'),
        ('A1', 'A1 (594 × 841 mm)'),
        ('A2', 'A2 (420 × 594 mm)'),
        ('A3', 'A3 (297 × 420 mm)'),
        ('A4', 'A4 (210 × 297 mm)')
    ], string='Sheet Size', default='A3')

    # Status and versioning
    version = fields.Char(string='Version', default='1.0')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('superseded', 'Superseded')
    ], string='Status', default='draft', tracking=True)

    # Metadata
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    reviewed_by = fields.Many2one('res.users', string='Reviewed By')
    approved_by = fields.Many2one('res.users', string='Approved By')

    # Dates
    creation_date = fields.Date(string='Creation Date', default=fields.Date.today)
    review_date = fields.Date(string='Review Date')
    approval_date = fields.Date(string='Approval Date')

    # Computed fields
    file_size = fields.Float(string='File Size (MB)', compute='_compute_file_size')
    is_latest_version = fields.Boolean(string='Latest Version', compute='_compute_latest_version')

    @api.depends('drawing_file')
    def _compute_file_size(self):
        for drawing in self:
            if drawing.drawing_file:
                # Convert bytes to MB
                file_data = base64.b64decode(drawing.drawing_file)
                drawing.file_size = len(file_data) / (1024 * 1024)
            else:
                drawing.file_size = 0.0

    @api.depends('drawing_number', 'project_id')
    def _compute_latest_version(self):
        for drawing in self:
            if drawing.drawing_number and drawing.project_id:
                latest = self.search([
                    ('drawing_number', '=', drawing.drawing_number),
                    ('project_id', '=', drawing.project_id.id)
                ], order='version desc', limit=1)
                drawing.is_latest_version = (drawing.id == latest.id) if latest else True
            else:
                drawing.is_latest_version = True

    @api.constrains('drawing_number', 'project_id')
    def _check_unique_drawing_number(self):
        for drawing in self:
            if drawing.drawing_number and drawing.project_id:
                existing = self.search([
                    ('drawing_number', '=', drawing.drawing_number),
                    ('project_id', '=', drawing.project_id.id),
                    ('version', '=', drawing.version),
                    ('id', '!=', drawing.id)
                ])
                if existing:
                    raise ValidationError(_("Drawing number %s with version %s already exists for this project.") % (drawing.drawing_number, drawing.version))

    def action_submit_for_review(self):
        """Submit drawing for review"""
        self.ensure_one()
        if self.status != 'draft':
            raise ValidationError(_("Only draft drawings can be submitted for review."))
        self.status = 'review'
        self.review_date = fields.Date.today()
        self.message_post(body=_("Drawing submitted for review."))

    def action_approve(self):
        """Approve the drawing"""
        self.ensure_one()
        if self.status != 'review':
            raise ValidationError(_("Only drawings under review can be approved."))
        self.status = 'approved'
        self.approval_date = fields.Date.today()
        self.approved_by = self.env.user
        self.message_post(body=_("Drawing approved."))

    def action_create_revision(self):
        """Create a new revision of the drawing"""
        self.ensure_one()
        # Mark current as superseded
        self.status = 'superseded'

        # Create new version
        new_version = self.copy({
            'version': self._get_next_version(),
            'status': 'draft',
            'review_date': False,
            'approval_date': False,
            'reviewed_by': False,
            'approved_by': False,
        })

        return {
            'name': _('Drawing Revision'),
            'type': 'ir.actions.act_window',
            'res_model': 'avf.drawing.management',
            'res_id': new_version.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_next_version(self):
        """Generate next version number"""
        if not self.version:
            return "1.0"

        try:
            parts = self.version.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            return f"{major}.{minor + 1}"
        except:
            return "1.0"

class ArchitectDrawingRevision(models.Model):
    _name = 'avf.drawing.revision'
    _description = 'Drawing Revision History'
    _order = 'revision_number desc'

    drawing_id = fields.Many2one('avf.drawing.management', string='Drawing', required=True, ondelete='cascade')
    revision_number = fields.Integer(string='Revision Number', required=True)
    revision_date = fields.Date(string='Revision Date', default=fields.Date.today)
    revised_by = fields.Many2one('res.users', string='Revised By', default=lambda self: self.env.user)
    revision_notes = fields.Text(string='Revision Notes')

    # Previous file for comparison
    previous_file = fields.Binary(string='Previous File', attachment=True)
    previous_filename = fields.Char(string='Previous Filename')

class ArchitectDrawingComment(models.Model):
    _name = 'avf.drawing.comment'
    _description = 'Drawing Comments'
    _order = 'create_date desc'

    drawing_id = fields.Many2one('avf.drawing.management', string='Drawing', required=True, ondelete='cascade')
    comment = fields.Text(string='Comment', required=True)
    comment_type = fields.Selection([
        ('general', 'General Comment'),
        ('correction', 'Correction Required'),
        ('suggestion', 'Suggestion'),
        ('approval', 'Approval Comment')
    ], string='Comment Type', default='general')

    author_id = fields.Many2one('res.users', string='Author', default=lambda self: self.env.user)
    is_resolved = fields.Boolean(string='Resolved', default=False)
    resolution_notes = fields.Text(string='Resolution Notes')