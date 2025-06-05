# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging
import base64
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class DocumentAnalysis(models.Model):
    _name = 'document.analysis'
    _description = 'AI Document Analysis'
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(string='Analysis Name', required=True)
    sequence = fields.Char(string='Sequence', default=lambda self: self.env['ir.sequence'].next_by_code('document.analysis'))
    
    # Document Information
    document_id = fields.Many2one('ir.attachment', string='Document', required=True)
    document_name = fields.Char(string='Document Name', related='document_id.name', store=True)
    document_type = fields.Char(string='Document Type', related='document_id.mimetype', store=True)
    document_size = fields.Integer(string='Document Size', related='document_id.file_size', store=True)
    
    # Related Records
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('is_company', '=', True)])
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    
    # Analysis Type
    analysis_type = fields.Selection([
        ('contract', 'Contract Analysis'),
        ('certificate', 'Certificate Verification'),
        ('financial', 'Financial Document'),
        ('compliance', 'Compliance Document'),
        ('quality', 'Quality Document'),
        ('general', 'General Analysis'),
    ], string='Analysis Type', default='general', required=True)
    
    # Analysis Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('analyzing', 'Analyzing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], string='State', default='draft', required=True)
    
    # Progress Tracking
    progress = fields.Float(string='Progress (%)', default=0.0)
    progress_message = fields.Char(string='Progress Message')
    
    # AI Analysis Results
    ai_summary = fields.Text(string='AI Summary')
    key_information = fields.Text(string='Key Information (JSON)')
    risk_indicators = fields.Text(string='Risk Indicators (JSON)')
    compliance_status = fields.Text(string='Compliance Status (JSON)')
    recommendations = fields.Text(string='AI Recommendations')
    
    # Analysis Scores
    confidence_score = fields.Float(string='Confidence Score', default=0.0)
    risk_score = fields.Float(string='Risk Score', default=0.0)
    compliance_score = fields.Float(string='Compliance Score', default=0.0)
    
    # Extracted Data
    extracted_text = fields.Text(string='Extracted Text')
    extracted_data = fields.Text(string='Extracted Data (JSON)')
    
    # Contract-specific fields
    contract_value = fields.Float(string='Contract Value')
    contract_start_date = fields.Date(string='Contract Start Date')
    contract_end_date = fields.Date(string='Contract End Date')
    payment_terms = fields.Char(string='Payment Terms')
    
    # Certificate-specific fields
    certificate_type = fields.Char(string='Certificate Type')
    issuing_authority = fields.Char(string='Issuing Authority')
    certificate_valid_from = fields.Date(string='Valid From')
    certificate_valid_until = fields.Date(string='Valid Until')
    certificate_status = fields.Selection([
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('expiring_soon', 'Expiring Soon'),
        ('invalid', 'Invalid'),
    ], string='Certificate Status')
    
    # Timing
    started_date = fields.Datetime(string='Started Date')
    completed_date = fields.Datetime(string='Completed Date')
    processing_time = fields.Float(string='Processing Time (seconds)', compute='_compute_processing_time', store=True)
    
    # User Context
    analyzed_by = fields.Many2one('res.users', string='Analyzed By', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('started_date', 'completed_date')
    def _compute_processing_time(self):
        for record in self:
            if record.started_date and record.completed_date:
                delta = record.completed_date - record.started_date
                record.processing_time = delta.total_seconds()
            else:
                record.processing_time = 0.0

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            document = self.env['ir.attachment'].browse(vals.get('document_id'))
            vals['name'] = f"Analysis: {document.name}"
        return super().create(vals)

    def action_start_analysis(self):
        """Start the document analysis process"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Only draft analyses can be started'))
        
        self.write({
            'state': 'analyzing',
            'started_date': fields.Datetime.now(),
            'progress': 0.0,
            'progress_message': 'Starting document analysis...'
        })
        
        # Queue the analysis process
        self.env['ai.processing.queue'].create({
            'name': f'Document Analysis: {self.document_name}',
            'request_type': 'document_analysis',
            'priority': 'medium',
            'input_data': json.dumps({'document_id': self.document_id.id}),
            'model_name': 'document.analysis',
            'record_id': self.id,
            'method_name': 'process_analysis',
        })

    def process_analysis(self):
        """Process the document analysis"""
        self.ensure_one()
        
        try:
            # Step 1: Extract text from document
            self.update_progress(20, 'Extracting text from document...')
            self._extract_text()
            
            # Step 2: Analyze document structure
            self.update_progress(40, 'Analyzing document structure...')
            self._analyze_structure()
            
            # Step 3: Run AI analysis
            self.update_progress(60, 'Running AI analysis...')
            self._run_ai_analysis()
            
            # Step 4: Extract specific information based on type
            self.update_progress(80, 'Extracting specific information...')
            self._extract_specific_information()
            
            # Step 5: Generate recommendations
            self.update_progress(95, 'Generating recommendations...')
            self._generate_recommendations()
            
            # Complete
            self.write({
                'state': 'completed',
                'completed_date': fields.Datetime.now(),
                'progress': 100.0,
                'progress_message': 'Analysis completed successfully'
            })
            
        except Exception as e:
            _logger.error(f"Error in document analysis: {str(e)}")
            self.write({
                'state': 'failed',
                'completed_date': fields.Datetime.now(),
                'progress_message': f'Analysis failed: {str(e)}'
            })
            raise

    def _extract_text(self):
        """Extract text from document"""
        document = self.document_id
        
        if not document.datas:
            raise UserError(_('Document has no content'))
        
        # Decode document content
        document_content = base64.b64decode(document.datas)
        
        # Extract text based on document type
        if document.mimetype == 'application/pdf':
            extracted_text = self._extract_text_from_pdf(document_content)
        elif document.mimetype in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            extracted_text = self._extract_text_from_word(document_content)
        elif document.mimetype.startswith('text/'):
            extracted_text = document_content.decode('utf-8', errors='ignore')
        elif document.mimetype.startswith('image/'):
            extracted_text = self._extract_text_from_image(document_content)
        else:
            extracted_text = "Text extraction not supported for this file type"
        
        self.extracted_text = extracted_text

    def _extract_text_from_pdf(self, content):
        """Extract text from PDF document"""
        try:
            import PyPDF2
            import io
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except ImportError:
            _logger.warning("PyPDF2 not installed, cannot extract PDF text")
            return "PDF text extraction requires PyPDF2 library"
        except Exception as e:
            _logger.error(f"Error extracting PDF text: {str(e)}")
            return f"Error extracting PDF text: {str(e)}"

    def _extract_text_from_word(self, content):
        """Extract text from Word document"""
        try:
            import docx
            import io
            
            doc = docx.Document(io.BytesIO(content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except ImportError:
            _logger.warning("python-docx not installed, cannot extract Word text")
            return "Word text extraction requires python-docx library"
        except Exception as e:
            _logger.error(f"Error extracting Word text: {str(e)}")
            return f"Error extracting Word text: {str(e)}"

    def _extract_text_from_image(self, content):
        """Extract text from image using OCR"""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(content))
            text = pytesseract.image_to_string(image)
            
            return text
        except ImportError:
            _logger.warning("pytesseract not installed, cannot extract image text")
            return "Image text extraction requires pytesseract library"
        except Exception as e:
            _logger.error(f"Error extracting image text: {str(e)}")
            return f"Error extracting image text: {str(e)}"

    def _analyze_structure(self):
        """Analyze document structure"""
        if not self.extracted_text:
            return
        
        # Basic structure analysis
        lines = self.extracted_text.split('\n')
        word_count = len(self.extracted_text.split())
        
        structure_data = {
            'line_count': len(lines),
            'word_count': word_count,
            'character_count': len(self.extracted_text),
            'has_tables': 'table' in self.extracted_text.lower() or '|' in self.extracted_text,
            'has_signatures': any(keyword in self.extracted_text.lower() for keyword in ['signature', 'signed', 'authorized']),
            'has_dates': self._detect_dates_in_text(self.extracted_text),
            'has_amounts': self._detect_amounts_in_text(self.extracted_text),
        }
        
        # Store structure data
        if not self.extracted_data:
            self.extracted_data = json.dumps(structure_data)
        else:
            existing_data = json.loads(self.extracted_data)
            existing_data.update(structure_data)
            self.extracted_data = json.dumps(existing_data)

    def _run_ai_analysis(self):
        """Run AI analysis on the document"""
        # Get AI service for document analysis
        ai_service = self.env['purchase.ai.service'].get_service_for_usage('document_analysis')
        if not ai_service:
            _logger.warning("No AI service available for document analysis")
            return
        
        # Prepare AI prompt based on analysis type
        prompt = self._prepare_analysis_prompt()
        
        try:
            response = ai_service.call_ai_service(
                prompt=prompt,
                context={'document_id': self.document_id.id, 'analysis_id': self.id}
            )
            
            if response.get('success'):
                self._process_ai_response(response.get('response', {}))
            
        except Exception as e:
            _logger.error(f"AI analysis failed: {str(e)}")

    def _prepare_analysis_prompt(self):
        """Prepare AI prompt based on analysis type"""
        base_prompt = f"""
        Analyze the following document:
        
        Document Name: {self.document_name}
        Document Type: {self.analysis_type}
        
        Document Content:
        {self.extracted_text[:4000]}  # Limit to first 4000 characters
        
        """
        
        if self.analysis_type == 'contract':
            prompt = base_prompt + """
            This is a contract document. Please analyze and extract:
            1. Contract parties and their roles
            2. Contract value and payment terms
            3. Contract duration (start and end dates)
            4. Key obligations and responsibilities
            5. Risk factors and concerning clauses
            6. Compliance with standard terms
            7. Recommendations for negotiation or approval
            
            Format your response as JSON with keys: parties, value, duration, obligations, risks, compliance, recommendations, confidence_score
            """
        elif self.analysis_type == 'certificate':
            prompt = base_prompt + """
            This is a certificate document. Please analyze and extract:
            1. Certificate type and purpose
            2. Issuing authority
            3. Validity period (from and to dates)
            4. Certificate holder information
            5. Scope of certification
            6. Certificate status (valid/expired/expiring)
            7. Compliance implications
            
            Format your response as JSON with keys: type, authority, validity, holder, scope, status, compliance, confidence_score
            """
        elif self.analysis_type == 'financial':
            prompt = base_prompt + """
            This is a financial document. Please analyze and extract:
            1. Financial figures and key metrics
            2. Revenue and profitability indicators
            3. Financial health indicators
            4. Risk factors
            5. Compliance with financial requirements
            6. Recommendations for financial assessment
            
            Format your response as JSON with keys: metrics, revenue, health, risks, compliance, recommendations, confidence_score
            """
        else:
            prompt = base_prompt + """
            Please provide a general analysis of this document including:
            1. Document summary and purpose
            2. Key information and data points
            3. Risk indicators or concerns
            4. Compliance considerations
            5. Recommendations for action
            
            Format your response as JSON with keys: summary, key_info, risks, compliance, recommendations, confidence_score
            """
        
        return prompt

    def _process_ai_response(self, ai_response):
        """Process AI analysis response"""
        try:
            # Store general analysis results
            self.ai_summary = ai_response.get('summary', '')
            self.confidence_score = ai_response.get('confidence_score', 0.0)
            self.recommendations = ai_response.get('recommendations', '')
            
            # Store structured data
            self.key_information = json.dumps(ai_response.get('key_info', {}))
            self.risk_indicators = json.dumps(ai_response.get('risks', []))
            self.compliance_status = json.dumps(ai_response.get('compliance', {}))
            
            # Extract type-specific information
            if self.analysis_type == 'contract':
                self._extract_contract_info(ai_response)
            elif self.analysis_type == 'certificate':
                self._extract_certificate_info(ai_response)
            
        except Exception as e:
            _logger.error(f"Error processing AI response: {str(e)}")

    def _extract_contract_info(self, ai_response):
        """Extract contract-specific information"""
        try:
            duration = ai_response.get('duration', {})
            if isinstance(duration, dict):
                if 'start_date' in duration:
                    self.contract_start_date = duration['start_date']
                if 'end_date' in duration:
                    self.contract_end_date = duration['end_date']
            
            value = ai_response.get('value', {})
            if isinstance(value, dict) and 'amount' in value:
                self.contract_value = value['amount']
            elif isinstance(value, (int, float)):
                self.contract_value = value
            
            if 'payment_terms' in ai_response:
                self.payment_terms = ai_response['payment_terms']
                
        except Exception as e:
            _logger.error(f"Error extracting contract info: {str(e)}")

    def _extract_certificate_info(self, ai_response):
        """Extract certificate-specific information"""
        try:
            self.certificate_type = ai_response.get('type', '')
            self.issuing_authority = ai_response.get('authority', '')
            
            validity = ai_response.get('validity', {})
            if isinstance(validity, dict):
                if 'from' in validity:
                    self.certificate_valid_from = validity['from']
                if 'to' in validity:
                    self.certificate_valid_until = validity['to']
            
            status = ai_response.get('status', '').lower()
            if 'valid' in status:
                self.certificate_status = 'valid'
            elif 'expired' in status:
                self.certificate_status = 'expired'
            elif 'expiring' in status:
                self.certificate_status = 'expiring_soon'
            else:
                self.certificate_status = 'invalid'
                
        except Exception as e:
            _logger.error(f"Error extracting certificate info: {str(e)}")

    def _extract_specific_information(self):
        """Extract specific information based on analysis type"""
        # This method can be extended for more specific extraction logic
        pass

    def _generate_recommendations(self):
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Risk-based recommendations
        if self.risk_score > 0.7:
            recommendations.append("High risk detected - requires management review")
        
        # Certificate-specific recommendations
        if self.analysis_type == 'certificate':
            if self.certificate_status == 'expired':
                recommendations.append("Certificate has expired - request updated certificate")
            elif self.certificate_status == 'expiring_soon':
                recommendations.append("Certificate expiring soon - follow up for renewal")
        
        # Contract-specific recommendations
        if self.analysis_type == 'contract':
            if self.contract_end_date and self.contract_end_date < fields.Date.today():
                recommendations.append("Contract has expired - review renewal requirements")
        
        if recommendations:
            existing_recommendations = self.recommendations or ""
            self.recommendations = existing_recommendations + "\n\nSystem Recommendations:\n" + "\n".join(recommendations)

    def update_progress(self, progress, message=None):
        """Update analysis progress"""
        self.ensure_one()
        values = {'progress': min(100.0, max(0.0, progress))}
        if message:
            values['progress_message'] = message
        self.write(values)

    def _detect_dates_in_text(self, text):
        """Detect if text contains dates"""
        import re
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _detect_amounts_in_text(self, text):
        """Detect if text contains monetary amounts"""
        import re
        amount_patterns = [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|dollars?|euros?)',
        ]
        
        for pattern in amount_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @api.model
    def analyze_document(self, document_id, analysis_type='general'):
        """Public method to analyze a document"""
        document = self.env['ir.attachment'].browse(document_id)
        if not document.exists():
            raise UserError(_('Document not found'))
        
        analysis = self.create({
            'document_id': document_id,
            'analysis_type': analysis_type,
        })
        
        analysis.action_start_analysis()
        return analysis

    def action_view_document(self):
        """View the analyzed document"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self.document_id.id}?download=true',
            'target': 'new',
        } 