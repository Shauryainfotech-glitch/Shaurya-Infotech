from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TenderSubmission(models.Model):
    _name = 'avgc.tender.submission'
    _description = 'Tender Submission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'submission_date desc'

    name = fields.Char('Reference', required=True, copy=False,
                      default=lambda self: _('New'))
    tender_id = fields.Many2one('avgc.tender', string='Tender', required=True,
                               ondelete='cascade')
    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True)
    submission_date = fields.Datetime('Submission Date', default=fields.Datetime.now)
    
    # Financial Details
    quoted_amount = fields.Monetary('Quoted Amount', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    
    # Evaluation
    evaluator_id = fields.Many2one('res.users', string='Evaluated By')
    evaluation_date = fields.Datetime('Evaluation Date')
    technical_score = fields.Float('Technical Score', digits=(5, 2))
    financial_score = fields.Float('Financial Score', digits=(5, 2))
    total_score = fields.Float('Total Score', compute='_compute_total_score',
                             store=True, digits=(5, 2))
    evaluation_notes = fields.Text('Evaluation Notes')
    
    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('qualified', 'Qualified'),
        ('disqualified', 'Disqualified'),
        ('awarded', 'Awarded'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    
    # Documents
    document_ids = fields.One2many('avgc.tender.submission.document', 
                                 'submission_id', string='Documents')
    document_count = fields.Integer('Document Count', 
                                  compute='_compute_document_count')

    @api.depends('technical_score', 'financial_score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = (record.technical_score * 0.7 + 
                                record.financial_score * 0.3)

    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('avgc.tender.submission')
        return super(TenderSubmission, self).create(vals)

    def action_submit(self):
        self.write({'status': 'submitted'})
        self.message_post(body=_('Submission has been submitted.'))

    def action_start_review(self):
        self.write({
            'status': 'under_review',
            'evaluator_id': self.env.user.id,
        })
        self.message_post(body=_('Review process has started.'))

    def action_qualify(self):
        self.write({'status': 'qualified'})
        self.message_post(body=_('Submission has been qualified.'))

    def action_disqualify(self):
        self.write({'status': 'disqualified'})
        self.message_post(body=_('Submission has been disqualified.'))

    def action_award(self):
        if self.tender_id.status == 'evaluation':
            self.write({'status': 'awarded'})
            self.tender_id.write({
                'status': 'awarded',
                'award_date': fields.Date.today(),
            })
            self.message_post(body=_('Submission has been awarded.'))
        else:
            raise ValidationError(_('Tender must be in evaluation stage to award.'))

    def action_reject(self):
        self.write({'status': 'rejected'})
        self.message_post(body=_('Submission has been rejected.'))


class TenderSubmissionDocument(models.Model):
    _name = 'avgc.tender.submission.document'
    _description = 'Tender Submission Document'
    _inherit = ['mail.thread']

    name = fields.Char('Document Name', required=True)
    submission_id = fields.Many2one('avgc.tender.submission', string='Submission',
                                  required=True, ondelete='cascade')
    document_type = fields.Selection([
        ('technical', 'Technical Document'),
        ('financial', 'Financial Document'),
        ('compliance', 'Compliance Document'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    
    file_data = fields.Binary('File', required=True)
    file_name = fields.Char('File Name')
    file_size = fields.Integer('File Size')
    mime_type = fields.Char('MIME Type')
    
    is_verified = fields.Boolean('Verified', default=False)
    verified_by = fields.Many2one('res.users', string='Verified By')
    verification_date = fields.Datetime('Verification Date')
    verification_notes = fields.Text('Verification Notes')

    def action_verify(self):
        self.write({
            'is_verified': True,
            'verified_by': self.env.user.id,
            'verification_date': fields.Datetime.now(),
        })
        self.message_post(body=_('Document has been verified.'))
