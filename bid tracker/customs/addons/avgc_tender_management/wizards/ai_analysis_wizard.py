from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AIAnalysisWizard(models.TransientModel):
    _name = 'avgc.ai.analysis.wizard'
    _description = 'AI Document Analysis Wizard'

    # Target Records
    tender_id = fields.Many2one('avgc.tender', string='Tender')
    gem_bid_id = fields.Many2one('avgc.gem.bid', string='GeM Bid')
    document_ids = fields.Many2many('avgc.tender.document', string='Documents to Analyze')
    
    # Analysis Configuration
    ai_provider = fields.Selection([
        ('claude', 'Claude (Anthropic)'),
        ('gpt', 'GPT (OpenAI)'),
        ('gemini', 'Gemini (Google)'),
    ], string='AI Provider', required=True, default='claude')
    
    analysis_type = fields.Selection([
        ('document_summary', 'Document Summary'),
        ('compliance_check', 'Compliance Check'),
        ('risk_assessment', 'Risk Assessment'),
        ('bid_optimization', 'Bid Optimization'),
        ('tender_response', 'Tender Response Generation'),
        ('ocr_extraction', 'OCR Text Extraction'),
        ('gem_bid_analysis', 'GeM Bid Analysis'),
    ], string='Analysis Type', required=True, default='document_summary')
    
    # Input Options
    use_uploaded_file = fields.Boolean('Upload Custom File', default=False)
    uploaded_file = fields.Binary('Custom File')
    uploaded_filename = fields.Char('Custom Filename')
    custom_prompt = fields.Text('Custom Analysis Prompt')
    
    # Processing Options
    batch_process = fields.Boolean('Batch Process Multiple Documents', default=False)
    include_ocr = fields.Boolean('Include OCR Processing', default=True)
    generate_summary = fields.Boolean('Generate Executive Summary', default=True)
    
    # Results Preview
    estimated_cost = fields.Float('Estimated Cost', digits=(10, 4), readonly=True)
    estimated_time = fields.Integer('Estimated Time (minutes)', readonly=True)
    
    @api.onchange('analysis_type', 'document_ids', 'ai_provider')
    def _onchange_analysis_config(self):
        """Update cost and time estimates"""
        doc_count = len(self.document_ids) if self.batch_process else 1
        
        # Base cost per document by provider
        provider_costs = {
            'claude': 0.05,
            'gpt': 0.03,
            'gemini': 0.02,
        }
        
        # Analysis type multipliers
        type_multipliers = {
            'document_summary': 1.0,
            'compliance_check': 1.5,
            'risk_assessment': 2.0,
            'bid_optimization': 2.5,
            'tender_response': 3.0,
            'ocr_extraction': 0.8,
            'gem_bid_analysis': 2.2,
        }
        
        base_cost = provider_costs.get(self.ai_provider, 0.05)
        multiplier = type_multipliers.get(self.analysis_type, 1.0)
        
        self.estimated_cost = base_cost * multiplier * doc_count
        self.estimated_time = min(2 + (doc_count * 1.5), 30)  # 2-30 minutes
    
    def action_start_analysis(self):
        """Start the AI analysis process"""
        self.ensure_one()
        
        if not self.document_ids and not self.use_uploaded_file:
            raise UserError(_('Please select documents to analyze or upload a custom file.'))
        
        analyses = []
        
        if self.batch_process and self.document_ids:
            # Process multiple documents
            for document in self.document_ids:
                analysis = self._create_analysis(document)
                analyses.append(analysis)
        elif self.document_ids:
            # Process single document
            analysis = self._create_analysis(self.document_ids[0])
            analyses.append(analysis)
        elif self.use_uploaded_file:
            # Process uploaded file
            analysis = self._create_analysis_from_file()
            analyses.append(analysis)
        
        # Start processing
        for analysis in analyses:
            analysis.action_process()
        
        if len(analyses) == 1:
            return {
                'name': _('AI Analysis Result'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'avgc.ai.analysis',
                'res_id': analyses[0].id,
                'target': 'current',
            }
        else:
            return {
                'name': _('AI Analysis Results'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'avgc.ai.analysis',
                'domain': [('id', 'in', [a.id for a in analyses])],
                'target': 'current',
            }
    
    def _create_analysis(self, document):
        """Create AI analysis record for a document"""
        analysis_name = f"{self.analysis_type.replace('_', ' ').title()} - {document.name}"
        
        return self.env['avgc.ai.analysis'].create({
            'name': analysis_name,
            'tender_id': self.tender_id.id,
            'gem_bid_id': self.gem_bid_id.id,
            'document_id': document.id,
            'ai_provider': self.ai_provider,
            'analysis_type': self.analysis_type,
            'input_text': self.custom_prompt or self._get_default_prompt(document),
            'input_file': document.file_data,
            'input_filename': document.file_name,
        })
    
    def _create_analysis_from_file(self):
        """Create AI analysis record from uploaded file"""
        analysis_name = f"{self.analysis_type.replace('_', ' ').title()} - {self.uploaded_filename}"
        
        return self.env['avgc.ai.analysis'].create({
            'name': analysis_name,
            'tender_id': self.tender_id.id,
            'gem_bid_id': self.gem_bid_id.id,
            'ai_provider': self.ai_provider,
            'analysis_type': self.analysis_type,
            'input_text': self.custom_prompt or self._get_default_prompt(),
            'input_file': self.uploaded_file,
            'input_filename': self.uploaded_filename,
        })
    
    def _get_default_prompt(self, document=None):
        """Generate default prompt based on context"""
        if self.tender_id:
            return f"Analyze this document in context of tender: {self.tender_id.title}"
        elif self.gem_bid_id:
            return f"Analyze this document for GeM bid: {self.gem_bid_id.title}"
        elif document:
            return f"Perform {self.analysis_type.replace('_', ' ')} on document: {document.name}"
        else:
            return f"Perform {self.analysis_type.replace('_', ' ')} on the uploaded document"


class TenderProcessingWizard(models.TransientModel):
    _name = 'avgc.tender.processing.wizard'
    _description = 'Automated Tender Processing Wizard'

    # Source Configuration
    tender_id = fields.Many2one('avgc.tender', string='Tender', required=True)
    processing_mode = fields.Selection([
        ('full_automation', 'Full Automation'),
        ('assisted', 'AI-Assisted Processing'),
        ('manual_review', 'Manual Review with AI Insights'),
    ], string='Processing Mode', required=True, default='assisted')
    
    # AI Configuration
    enable_ocr = fields.Boolean('Enable OCR Processing', default=True)
    enable_ai_analysis = fields.Boolean('Enable AI Analysis', default=True)
    ai_providers = fields.Selection([
        ('claude_only', 'Claude Only'),
        ('multi_ai', 'Multi-AI Analysis'),
        ('best_available', 'Best Available'),
    ], string='AI Configuration', default='multi_ai')
    
    # Processing Options
    analyze_documents = fields.Boolean('Analyze All Documents', default=True)
    check_compliance = fields.Boolean('Check Compliance', default=True)
    assess_risks = fields.Boolean('Assess Risks', default=True)
    generate_insights = fields.Boolean('Generate Strategic Insights', default=True)
    create_recommendations = fields.Boolean('Create Recommendations', default=True)
    
    # Output Options
    generate_report = fields.Boolean('Generate Processing Report', default=True)
    notify_stakeholders = fields.Boolean('Notify Stakeholders', default=False)
    create_tasks = fields.Boolean('Create Follow-up Tasks', default=True)
    
    # Status
    processing_status = fields.Selection([
        ('ready', 'Ready to Process'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='Status', default='ready', readonly=True)
    
    progress_percentage = fields.Float('Progress (%)', digits=(5, 2), readonly=True)
    current_step = fields.Char('Current Step', readonly=True)
    
    def action_start_processing(self):
        """Start automated tender processing"""
        self.ensure_one()
        
        self.processing_status = 'processing'
        self.progress_percentage = 0
        
        try:
            # Step 1: Document Analysis
            if self.analyze_documents:
                self._process_documents()
                self.progress_percentage = 20
            
            # Step 2: Compliance Check
            if self.check_compliance:
                self._check_compliance()
                self.progress_percentage = 40
            
            # Step 3: Risk Assessment
            if self.assess_risks:
                self._assess_risks()
                self.progress_percentage = 60
            
            # Step 4: Generate Insights
            if self.generate_insights:
                self._generate_insights()
                self.progress_percentage = 80
            
            # Step 5: Create Recommendations
            if self.create_recommendations:
                self._create_recommendations()
                self.progress_percentage = 90
            
            # Step 6: Finalization
            if self.generate_report:
                self._generate_report()
            
            if self.create_tasks:
                self._create_follow_up_tasks()
            
            self.processing_status = 'completed'
            self.progress_percentage = 100
            self.current_step = 'Processing Complete'
            
            return self._show_results()
            
        except Exception as e:
            self.processing_status = 'failed'
            self.current_step = f'Error: {str(e)}'
            raise UserError(_('Processing failed: %s') % str(e))
    
    def _process_documents(self):
        """Process tender documents with AI"""
        self.current_step = 'Processing Documents'
        
        for document in self.tender_id.document_ids:
            if self.enable_ai_analysis:
                analysis = self.env['avgc.ai.analysis'].create({
                    'name': f'Auto Analysis - {document.name}',
                    'tender_id': self.tender_id.id,
                    'document_id': document.id,
                    'ai_provider': 'claude',
                    'analysis_type': 'document_summary',
                    'input_file': document.file_data,
                    'input_filename': document.file_name,
                })
                analysis.action_process()
    
    def _check_compliance(self):
        """Check tender compliance"""
        self.current_step = 'Checking Compliance'
        
        if self.enable_ai_analysis:
            analysis = self.env['avgc.ai.analysis'].create({
                'name': f'Compliance Check - {self.tender_id.title}',
                'tender_id': self.tender_id.id,
                'ai_provider': 'claude',
                'analysis_type': 'compliance_check',
                'input_text': f'Tender: {self.tender_id.title}\nDescription: {self.tender_id.description}',
            })
            analysis.action_process()
    
    def _assess_risks(self):
        """Assess tender risks"""
        self.current_step = 'Assessing Risks'
        
        if self.enable_ai_analysis:
            analysis = self.env['avgc.ai.analysis'].create({
                'name': f'Risk Assessment - {self.tender_id.title}',
                'tender_id': self.tender_id.id,
                'ai_provider': 'claude',
                'analysis_type': 'risk_assessment',
                'input_text': f'Tender: {self.tender_id.title}\nCategory: {self.tender_id.category}\nValue: {self.tender_id.estimated_value}',
            })
            analysis.action_process()
    
    def _generate_insights(self):
        """Generate strategic insights"""
        self.current_step = 'Generating Insights'
        # Implementation for insight generation
        pass
    
    def _create_recommendations(self):
        """Create recommendations"""
        self.current_step = 'Creating Recommendations'
        # Implementation for recommendation creation
        pass
    
    def _generate_report(self):
        """Generate processing report"""
        self.current_step = 'Generating Report'
        # Implementation for report generation
        pass
    
    def _create_follow_up_tasks(self):
        """Create follow-up tasks"""
        self.current_step = 'Creating Tasks'
        
        # Create standard follow-up tasks
        task_templates = [
            ('Review AI Analysis Results', 'administrative', 1),
            ('Vendor Communication', 'administrative', 3),
            ('Technical Evaluation', 'technical', 7),
            ('Financial Analysis', 'financial', 5),
        ]
        
        for task_name, category, days_offset in task_templates:
            due_date = fields.Date.today() + fields.timedelta(days=days_offset)
            self.env['avgc.task'].create({
                'name': f'{task_name} - {self.tender_id.title}',
                'tender_id': self.tender_id.id,
                'task_type': 'follow_up',
                'category': category,
                'due_date': due_date,
                'assigned_to': self.tender_id.assigned_to.id or self.env.user.id,
                'description': f'Automated task created from tender processing for {self.tender_id.title}',
            })
    
    def _show_results(self):
        """Show processing results"""
        return {
            'name': _('Processing Results'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'avgc.ai.analysis',
            'domain': [('tender_id', '=', self.tender_id.id)],
            'target': 'current',
            'context': {
                'group_by': 'analysis_type',
            },
        }