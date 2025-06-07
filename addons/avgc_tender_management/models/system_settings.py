from odoo import models, fields, api, _

class SystemSettings(models.Model):
    _name = 'avgc.system.settings'
    _description = 'System Settings'
    _inherit = ['mail.thread']

    name = fields.Char('Setting Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
    
    # General Settings
    enable_blockchain = fields.Boolean('Enable Blockchain Integration', default=False)
    enable_ai_analysis = fields.Boolean('Enable AI Analysis', default=True)
    enable_ocr = fields.Boolean('Enable OCR Processing', default=True)
    
    # Document Settings
    max_file_size = fields.Integer('Maximum File Size (MB)', default=25)
    allowed_file_types = fields.Char('Allowed File Types', 
                                   default='pdf,doc,docx,xls,xlsx,ppt,pptx,jpg,png')
    enable_version_control = fields.Boolean('Enable Version Control', default=True)
    
    # Email Settings
    enable_email_notifications = fields.Boolean('Enable Email Notifications', default=True)
    notification_email = fields.Char('Notification Email')
    
    # Security Settings
    min_password_length = fields.Integer('Minimum Password Length', default=8)
    password_expiry_days = fields.Integer('Password Expiry Days', default=90)
    session_timeout = fields.Integer('Session Timeout (minutes)', default=60)
    
    # API Integration
    api_key = fields.Char('API Key', groups='base.group_system')
    api_secret = fields.Char('API Secret', groups='base.group_system')
    api_endpoint = fields.Char('API Endpoint')
    
    # AI Configuration
    ai_provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('azure', 'Azure AI'),
        ('google', 'Google AI'),
    ], string='AI Provider', default='openai')
    ai_api_key = fields.Char('AI API Key', groups='base.group_system')
    ai_model = fields.Char('AI Model Name')
    
    # OCR Configuration
    ocr_provider = fields.Selection([
        ('tesseract', 'Tesseract'),
        ('azure', 'Azure OCR'),
        ('google', 'Google Cloud Vision'),
    ], string='OCR Provider', default='tesseract')
    ocr_api_key = fields.Char('OCR API Key', groups='base.group_system')
    
    # Blockchain Configuration
    blockchain_network = fields.Selection([
        ('ethereum', 'Ethereum'),
        ('polygon', 'Polygon'),
        ('hyperledger', 'Hyperledger'),
    ], string='Blockchain Network', default='ethereum')
    blockchain_node_url = fields.Char('Blockchain Node URL')
    smart_contract_address = fields.Char('Smart Contract Address')
    
    # Workflow Settings
    auto_stage_progression = fields.Boolean('Automatic Stage Progression', default=False)
    require_double_validation = fields.Boolean('Require Double Validation', default=True)
    
    # Audit Settings
    enable_audit_trail = fields.Boolean('Enable Audit Trail', default=True)
    audit_retention_days = fields.Integer('Audit Log Retention (days)', default=365)
    
    @api.model
    def get_settings(self):
        """Get system settings, create default if not exists"""
        settings = self.search([], limit=1)
        if not settings:
            settings = self.create({
                'name': 'Default System Settings'
            })
        return settings
    
    def write(self, vals):
        """Override write to track changes"""
        if vals.get('api_key') or vals.get('api_secret') or vals.get('ai_api_key') or vals.get('ocr_api_key'):
            self.message_post(body=_('Security settings have been updated'))
        return super(SystemSettings, self).write(vals)
