from odoo import models, fields, api, _


class DocumentRejectWizard(models.TransientModel):
    _name = 'avgc.document.reject.wizard'
    _description = 'Document Rejection Wizard'

    document_id = fields.Many2one('avgc.firm.document', string='Document', required=True)
    reason = fields.Selection([
        ('incomplete', 'Incomplete Information'),
        ('invalid_format', 'Invalid Format'),
        ('expired', 'Expired Document'),
        ('non_compliant', 'Non-Compliant'),
        ('poor_quality', 'Poor Quality'),
        ('other', 'Other'),
    ], string='Rejection Reason', required=True)
    
    comments = fields.Text('Comments', required=True)
    notify_creator = fields.Boolean('Notify Document Creator', default=True)
    
    def action_reject_document(self):
        """Reject the document with reason"""
        self.ensure_one()
        
        self.document_id.write({
            'status': 'rejected',
            'verification_notes': f"Rejected: {dict(self._fields['reason'].selection)[self.reason]}\n\nComments: {self.comments}"
        })
        
        # Post message with rejection details
        self.document_id.message_post(
            body=f"Document rejected. Reason: {dict(self._fields['reason'].selection)[self.reason]}<br/>Comments: {self.comments}",
            message_type='notification'
        )
        
        # Send notification if requested
        if self.notify_creator and self.document_id.created_by:
            self.document_id.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.document_id.created_by.id,
                summary=f'Document Rejected: {self.document_id.document_name}',
                note=f'Your document has been rejected. Reason: {dict(self._fields["reason"].selection)[self.reason]}\n\nComments: {self.comments}'
            )
        
        return {'type': 'ir.actions.act_window_close'}


class VendorBlacklistWizard(models.TransientModel):
    _name = 'avgc.vendor.blacklist.wizard'
    _description = 'Vendor Blacklist Wizard'

    vendor_id = fields.Many2one('avgc.vendor', string='Vendor', required=True)
    reason = fields.Selection([
        ('non_performance', 'Non-Performance'),
        ('fraud', 'Fraudulent Activities'),
        ('quality_issues', 'Quality Issues'),
        ('delivery_delays', 'Consistent Delivery Delays'),
        ('legal_issues', 'Legal Issues'),
        ('financial_instability', 'Financial Instability'),
        ('other', 'Other'),
    ], string='Blacklist Reason', required=True)
    
    blacklist_period = fields.Selection([
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('2_years', '2 Years'),
        ('permanent', 'Permanent'),
    ], string='Blacklist Period', required=True, default='1_year')
    
    comments = fields.Text('Detailed Comments', required=True)
    effective_date = fields.Date('Effective Date', default=fields.Date.today, required=True)
    review_date = fields.Date('Review Date')
    notify_vendor = fields.Boolean('Notify Vendor', default=False)
    
    @api.onchange('blacklist_period', 'effective_date')
    def _onchange_blacklist_period(self):
        """Calculate review date based on blacklist period"""
        if self.effective_date and self.blacklist_period != 'permanent':
            if self.blacklist_period == '6_months':
                self.review_date = self.effective_date + fields.timedelta(days=180)
            elif self.blacklist_period == '1_year':
                self.review_date = self.effective_date + fields.timedelta(days=365)
            elif self.blacklist_period == '2_years':
                self.review_date = self.effective_date + fields.timedelta(days=730)
    
    def action_blacklist_vendor(self):
        """Blacklist the vendor"""
        self.ensure_one()
        
        self.vendor_id.write({
            'status': 'blacklisted',
            'blacklist_reason': f"{dict(self._fields['reason'].selection)[self.reason]}\n\nDetails: {self.comments}"
        })
        
        # Create blacklist record
        self.env['avgc.vendor.blacklist'].create({
            'vendor_id': self.vendor_id.id,
            'reason': self.reason,
            'period': self.blacklist_period,
            'comments': self.comments,
            'effective_date': self.effective_date,
            'review_date': self.review_date,
            'blacklisted_by': self.env.user.id,
        })
        
        # Post message
        self.vendor_id.message_post(
            body=f"Vendor blacklisted. Reason: {dict(self._fields['reason'].selection)[self.reason]}<br/>Period: {dict(self._fields['blacklist_period'].selection)[self.blacklist_period]}<br/>Comments: {self.comments}",
            message_type='notification'
        )
        
        # Notify vendor if requested
        if self.notify_vendor:
            # Send formal notification
            pass
        
        return {'type': 'ir.actions.act_window_close'}


class TaskCreateWizard(models.TransientModel):
    _name = 'avgc.task.create.wizard'
    _description = 'Task Creation Wizard'

    # Template or Manual
    use_template = fields.Boolean('Use Template', default=False)
    template_id = fields.Many2one('avgc.task.template', string='Task Template')
    
    # Basic Information
    name = fields.Char('Task Title', required=True)
    description = fields.Html('Description')
    
    # Context
    tender_id = fields.Many2one('avgc.tender', string='Related Tender')
    gem_bid_id = fields.Many2one('avgc.gem.bid', string='Related GeM Bid')
    project_id = fields.Many2one('project.project', string='Project')
    
    # Assignment
    assigned_to = fields.Many2one('res.users', string='Assigned To', required=True)
    team_id = fields.Many2one('hr.department', string='Team')
    
    # Classification
    task_type = fields.Selection([
        ('tender_preparation', 'Tender Preparation'),
        ('document_review', 'Document Review'),
        ('compliance_check', 'Compliance Check'),
        ('vendor_evaluation', 'Vendor Evaluation'),
        ('technical_review', 'Technical Review'),
        ('financial_analysis', 'Financial Analysis'),
        ('approval_workflow', 'Approval Workflow'),
        ('follow_up', 'Follow-up'),
        ('other', 'Other'),
    ], string='Task Type', required=True)
    
    category = fields.Selection([
        ('administrative', 'Administrative'),
        ('technical', 'Technical'),
        ('financial', 'Financial'),
        ('legal', 'Legal'),
        ('compliance', 'Compliance'),
    ], string='Category', required=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Priority', default='medium', required=True)
    
    # Timeline
    start_date = fields.Date('Start Date', default=fields.Date.today)
    due_date = fields.Date('Due Date', required=True)
    estimated_hours = fields.Float('Estimated Hours', digits=(16, 2))
    
    # Options
    create_subtasks = fields.Boolean('Create Subtasks from Template', default=False)
    create_checklist = fields.Boolean('Create Checklist Items', default=True)
    
    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Populate fields from template"""
        if self.template_id:
            self.name = self.template_id.name
            self.description = self.template_id.description
            self.task_type = self.template_id.task_type
            self.category = self.template_id.category
            self.priority = self.template_id.priority
            self.estimated_hours = self.template_id.estimated_hours
            
            if self.template_id.duration_days:
                self.due_date = self.start_date + fields.timedelta(days=self.template_id.duration_days)
    
    def action_create_task(self):
        """Create the task"""
        self.ensure_one()
        
        task_vals = {
            'name': self.name,
            'description': self.description,
            'tender_id': self.tender_id.id,
            'gem_bid_id': self.gem_bid_id.id,
            'project_id': self.project_id.id,
            'assigned_to': self.assigned_to.id,
            'team_id': self.team_id.id,
            'task_type': self.task_type,
            'category': self.category,
            'priority': self.priority,
            'start_date': self.start_date,
            'due_date': self.due_date,
            'estimated_hours': self.estimated_hours,
        }
        
        task = self.env['avgc.task'].create(task_vals)
        
        # Create checklist items from template
        if self.create_checklist and self.template_id:
            for checklist_template in self.template_id.checklist_template_ids:
                due_date = None
                if checklist_template.days_offset:
                    due_date = self.start_date + fields.timedelta(days=checklist_template.days_offset)
                
                self.env['avgc.task.checklist'].create({
                    'task_id': task.id,
                    'name': checklist_template.name,
                    'description': checklist_template.description,
                    'is_mandatory': checklist_template.is_mandatory,
                    'due_date': due_date,
                    'sequence': checklist_template.sequence,
                })
        
        # Update template usage count
        if self.template_id:
            self.template_id.usage_count += 1
        
        return {
            'name': _('Task Created'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'avgc.task',
            'res_id': task.id,
            'target': 'current',
        }