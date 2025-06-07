from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TenderProcessingWizard(models.TransientModel):
    _name = 'avgc.tender.processing.wizard'
    _description = 'Tender Processing Wizard'

    tender_id = fields.Many2one('avgc.tender', string='Tender', required=True)
    action = fields.Selection([
        ('publish', 'Publish Tender'),
        ('evaluate', 'Start Evaluation'),
        ('award', 'Award Tender'),
        ('close', 'Close Tender'),
        ('cancel', 'Cancel Tender'),
    ], string='Action', required=True)
    
    # Publishing options
    publish_date = fields.Datetime('Publish Date', default=fields.Datetime.now)
    auto_close = fields.Boolean('Auto Close at Deadline', default=True)
    notify_vendors = fields.Boolean('Notify Vendors', default=True)
    selected_vendors = fields.Many2many('avgc.vendor', string='Selected Vendors')
    
    # Evaluation options
    evaluation_team = fields.Many2many('res.users', string='Evaluation Team')
    evaluation_deadline = fields.Date('Evaluation Deadline')
    evaluation_method = fields.Selection([
        ('technical', 'Technical First'),
        ('financial', 'Financial First'),
        ('combined', 'Combined Evaluation'),
    ], string='Evaluation Method', default='technical')
    
    # Award options
    awarded_vendor = fields.Many2one('avgc.vendor', string='Awarded Vendor')
    award_date = fields.Date('Award Date', default=fields.Date.today)
    contract_value = fields.Monetary('Contract Value', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                 default=lambda self: self.env.company.currency_id)
    
    # Closure options
    closure_notes = fields.Text('Closure Notes')
    archive_documents = fields.Boolean('Archive Documents', default=True)
    generate_report = fields.Boolean('Generate Closure Report', default=True)
    
    # Cancellation options
    cancellation_reason = fields.Selection([
        ('insufficient_bids', 'Insufficient Bids'),
        ('budget_constraints', 'Budget Constraints'),
        ('requirement_change', 'Requirement Change'),
        ('compliance_issues', 'Compliance Issues'),
        ('other', 'Other'),
    ], string='Cancellation Reason')
    cancellation_notes = fields.Text('Cancellation Notes')

    @api.model
    def default_get(self, fields_list):
        res = super(TenderProcessingWizard, self).default_get(fields_list)
        if self._context.get('active_model') == 'avgc.tender' and self._context.get('active_id'):
            tender = self.env['avgc.tender'].browse(self._context.get('active_id'))
            res.update({
                'tender_id': tender.id,
                'selected_vendors': [(6, 0, tender.vendor_ids.ids)],
            })
            # Set appropriate action based on tender status
            if tender.status == 'draft':
                res['action'] = 'publish'
            elif tender.status == 'published':
                res['action'] = 'evaluate'
            elif tender.status == 'evaluation':
                res['action'] = 'award'
        return res

    @api.onchange('action')
    def _onchange_action(self):
        if self.action == 'publish':
            self.evaluation_team = False
            self.awarded_vendor = False
        elif self.action == 'evaluate':
            self.publish_date = False
            self.awarded_vendor = False
        elif self.action == 'award':
            self.publish_date = False
            self.cancellation_reason = False

    def action_process(self):
        self.ensure_one()
        if not self.tender_id:
            raise ValidationError(_('No tender selected for processing.'))

        if self.action == 'publish':
            return self._process_publish()
        elif self.action == 'evaluate':
            return self._process_evaluate()
        elif self.action == 'award':
            return self._process_award()
        elif self.action == 'close':
            return self._process_close()
        elif self.action == 'cancel':
            return self._process_cancel()

    def _process_publish(self):
        self.tender_id.write({
            'status': 'published',
            'vendor_ids': [(6, 0, self.selected_vendors.ids)],
        })
        if self.notify_vendors:
            self._notify_vendors()
        return {'type': 'ir.actions.act_window_close'}

    def _process_evaluate(self):
        self.tender_id.write({
            'status': 'evaluation',
            'assigned_to': self.evaluation_team[:1].id,
        })
        self._create_evaluation_tasks()
        return {'type': 'ir.actions.act_window_close'}

    def _process_award(self):
        if not self.awarded_vendor:
            raise ValidationError(_('Please select a vendor to award the tender.'))
        self.tender_id.write({
            'status': 'awarded',
            'award_date': self.award_date,
        })
        self._create_award_documents()
        return {'type': 'ir.actions.act_window_close'}

    def _process_close(self):
        self.tender_id.write({
            'status': 'closed',
        })
        if self.generate_report:
            self._generate_closure_report()
        if self.archive_documents:
            self._archive_documents()
        return {'type': 'ir.actions.act_window_close'}

    def _process_cancel(self):
        if not self.cancellation_reason:
            raise ValidationError(_('Please specify the reason for cancellation.'))
        self.tender_id.write({
            'status': 'cancelled',
        })
        self._notify_cancellation()
        return {'type': 'ir.actions.act_window_close'}

    def _notify_vendors(self):
        """Send notification to selected vendors"""
        template = self.env.ref('avgc_tender_management.email_template_tender_published')
        for vendor in self.selected_vendors:
            template.send_mail(self.tender_id.id, force_send=True,
                            email_values={'email_to': vendor.email})

    def _create_evaluation_tasks(self):
        """Create evaluation tasks for team members"""
        for user in self.evaluation_team:
            self.env['avgc.task'].create({
                'name': f'Evaluate Tender: {self.tender_id.title}',
                'assigned_to': user.id,
                'tender_id': self.tender_id.id,
                'deadline': self.evaluation_deadline,
            })

    def _create_award_documents(self):
        """Create award documents"""
        self.env['avgc.tender.document'].create({
            'name': 'Award Letter',
            'tender_id': self.tender_id.id,
            'document_type': 'legal',
            'is_mandatory': True,
        })

    def _generate_closure_report(self):
        """Generate closure report"""
        return self.env['avgc.task.report'].create({
            'name': f'Closure Report: {self.tender_id.title}',
            'tender_id': self.tender_id.id,
            'notes': self.closure_notes,
        })

    def _archive_documents(self):
        """Archive tender documents"""
        self.tender_id.document_ids.write({'archived': True})

    def _notify_cancellation(self):
        """Notify stakeholders about tender cancellation"""
        self.tender_id.message_post(
            body=f'Tender cancelled. Reason: {self.cancellation_reason}\n{self.cancellation_notes}',
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )
