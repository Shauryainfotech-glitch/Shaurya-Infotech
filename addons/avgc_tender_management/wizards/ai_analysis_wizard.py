from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AIAnalysisWizard(models.TransientModel):
    _name = 'avgc.ai.analysis.wizard'
    _description = 'AI Analysis Wizard'

    tender_id = fields.Many2one('avgc.tender', string='Tender', required=True)
    document_ids = fields.Many2many('avgc.tender.document', string='Documents to Analyze')
    analysis_type = fields.Selection([
        ('technical', 'Technical Analysis'),
        ('financial', 'Financial Analysis'),
        ('compliance', 'Compliance Check'),
        ('risk', 'Risk Assessment'),
        ('all', 'Full Analysis'),
    ], string='Analysis Type', default='all', required=True)
    
    ai_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('azure', 'Azure AI'),
        ('google', 'Google AI'),
    ], string='AI Provider')
    
    language = fields.Selection([
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
    ], string='Language', default='en', required=True)
    
    include_ocr = fields.Boolean('Include OCR Processing', default=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Priority', default='medium')

    @api.model
    def default_get(self, fields_list):
        res = super(AIAnalysisWizard, self).default_get(fields_list)
        if self._context.get('active_model') == 'avgc.tender' and self._context.get('active_id'):
            tender = self.env['avgc.tender'].browse(self._context.get('active_id'))
            res.update({
                'tender_id': tender.id,
                'document_ids': [(6, 0, tender.document_ids.ids)],
            })
        # Get AI provider from system settings
        settings = self.env['avgc.system.settings'].get_settings()
        res['ai_provider'] = settings.ai_provider
        return res

    def action_start_analysis(self):
        self.ensure_one()
        if not self.document_ids:
            raise ValidationError(_('Please select at least one document to analyze.'))

        # Create AI analysis record
        analysis_vals = {
            'tender_id': self.tender_id.id,
            'analysis_type': self.analysis_type,
            'status': 'in_progress',
            'ai_provider': self.ai_provider,
            'language': self.language,
            'priority': self.priority,
        }
        analysis = self.env['avgc.ai.analysis'].create(analysis_vals)

        # Update tender status
        self.tender_id.write({
            'ai_analysis_status': 'in_progress',
            'ai_analysis_ids': [(4, analysis.id)],
        })

        # Process documents
        for doc in self.document_ids:
            if self.include_ocr and not doc.ocr_text:
                # Trigger OCR processing
                doc._process_ocr()
            
            # Create document analysis tasks
            analysis._create_document_analysis_task(doc)

        return {
            'type': 'ir.actions.act_window',
            'name': _('AI Analysis'),
            'res_model': 'avgc.ai.analysis',
            'res_id': analysis.id,
            'view_mode': 'form',
            'target': 'current',
        }
