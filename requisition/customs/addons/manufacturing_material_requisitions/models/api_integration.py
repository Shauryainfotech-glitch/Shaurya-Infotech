from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
import hmac
import hashlib
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

# Handle requests import gracefully
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    _logger.warning("requests library not available. API integration features will be limited.")


class RequisitionAPIIntegration(models.Model):
    _name = 'manufacturing.requisition.api.integration'
    _description = 'API Integration for Requisitions'
    _rec_name = 'name'

    name = fields.Char(string='Integration Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    # Integration Type
    integration_type = fields.Selection([
        ('erp', 'ERP System'),
        ('supplier', 'Supplier Portal'),
        ('inventory', 'Inventory Management'),
        ('procurement', 'Procurement System'),
        ('wms', 'Warehouse Management'),
        ('mes', 'Manufacturing Execution'),
        ('custom', 'Custom Integration')
    ], string='Integration Type', required=True, default='custom')
    
    # Connection Configuration
    api_url = fields.Char(string='API Base URL', required=True)
    api_version = fields.Char(string='API Version', default='v1')
    authentication_type = fields.Selection([
        ('none', 'No Authentication'),
        ('basic', 'Basic Authentication'),
        ('bearer', 'Bearer Token'),
        ('api_key', 'API Key'),
        ('oauth', 'OAuth 2.0'),
        ('custom', 'Custom Headers')
    ], string='Authentication Type', default='bearer')
    
    username = fields.Char(string='Username')
    password = fields.Char(string='Password')
    api_key = fields.Char(string='API Key')
    bearer_token = fields.Text(string='Bearer Token')
    custom_headers = fields.Text(string='Custom Headers (JSON)')
    
    # Synchronization Settings
    sync_direction = fields.Selection([
        ('push', 'Push Only (Outbound)'),
        ('pull', 'Pull Only (Inbound)'),
        ('bidirectional', 'Bidirectional')
    ], string='Sync Direction', default='push')
    
    auto_sync = fields.Boolean(string='Auto Synchronization', default=True)
    sync_frequency = fields.Selection([
        ('realtime', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('manual', 'Manual Only')
    ], string='Sync Frequency', default='realtime')
    
    # Data Mapping
    field_mapping_ids = fields.One2many('manufacturing.requisition.api.field.mapping', 'integration_id', 
                                       string='Field Mappings')
    
    # Webhook Configuration
    webhook_enabled = fields.Boolean(string='Enable Webhooks')
    webhook_url = fields.Char(string='Webhook URL')
    webhook_secret = fields.Char(string='Webhook Secret')
    webhook_events = fields.Selection([
        ('create', 'Create Events'),
        ('update', 'Update Events'),
        ('delete', 'Delete Events'),
        ('all', 'All Events')
    ], string='Webhook Events', default='all')
    
    # Statistics and Monitoring
    last_sync = fields.Datetime(string='Last Synchronization', readonly=True)
    sync_count = fields.Integer(string='Sync Count', readonly=True)
    error_count = fields.Integer(string='Error Count', readonly=True)
    last_error = fields.Text(string='Last Error', readonly=True)
    
    # Logs
    log_ids = fields.One2many('manufacturing.requisition.api.log', 'integration_id', string='API Logs')
    
    @api.model
    def create(self, vals):
        """Override create to check if requests is available"""
        if not REQUESTS_AVAILABLE:
            raise UserError('The requests library is not installed. Please install it to use API integration features.')
        return super().create(vals)
    
    @api.model
    def test_connection(self):
        """Test the API connection"""
        if not REQUESTS_AVAILABLE:
            return {'success': False, 'message': 'requests library not available. Please install it to use API features.'}
            
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.api_url}/health", headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Connection successful'}
            else:
                return {'success': False, 'message': f'HTTP {response.status_code}: {response.text}'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def _get_headers(self):
        """Build authentication headers"""
        headers = {'Content-Type': 'application/json'}
        
        if self.authentication_type == 'basic' and self.username and self.password:
            import base64
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'
            
        elif self.authentication_type == 'bearer' and self.bearer_token:
            headers['Authorization'] = f'Bearer {self.bearer_token}'
            
        elif self.authentication_type == 'api_key' and self.api_key:
            headers['X-API-Key'] = self.api_key
            
        elif self.authentication_type == 'custom' and self.custom_headers:
            try:
                custom = json.loads(self.custom_headers)
                headers.update(custom)
            except json.JSONDecodeError:
                _logger.warning("Invalid custom headers JSON format")
        
        return headers
    
    def sync_requisitions(self, requisition_ids=None):
        """Synchronize requisitions with external system"""
        if not REQUESTS_AVAILABLE:
            self._create_log('error', 'Cannot sync: requests library not available')
            return False
            
        try:
            if not self.active:
                return False
            
            if self.sync_direction in ['push', 'bidirectional']:
                result = self._push_requisitions(requisition_ids)
                
            if self.sync_direction in ['pull', 'bidirectional']:
                result = self._pull_requisitions()
            
            self.last_sync = fields.Datetime.now()
            self.sync_count += 1
            
            return True
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            self._create_log('error', f'Sync failed: {str(e)}')
            _logger.error(f"API sync error for {self.name}: {str(e)}")
            return False
    
    def _push_requisitions(self, requisition_ids=None):
        """Push requisitions to external system"""
        if not REQUESTS_AVAILABLE:
            return False
            
        if not requisition_ids:
            # Get all requisitions that need syncing
            domain = [('state', 'in', ['submitted', 'approved', 'in_progress'])]
            if hasattr(self.env['manufacturing.material.requisition'], 'last_api_sync'):
                domain.append(('write_date', '>', self.last_sync or '1900-01-01'))
            
            requisitions = self.env['manufacturing.material.requisition'].search(domain)
        else:
            requisitions = self.env['manufacturing.material.requisition'].browse(requisition_ids)
        
        for requisition in requisitions:
            data = self._map_requisition_to_external(requisition)
            
            try:
                headers = self._get_headers()
                response = requests.post(
                    f"{self.api_url}/requisitions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    self._create_log('success', f'Pushed requisition {requisition.name}')
                    # Update external reference if available
                    if 'id' in response.json():
                        requisition.external_reference = response.json()['id']
                else:
                    self._create_log('error', f'Failed to push {requisition.name}: {response.text}')
                    
            except Exception as e:
                self._create_log('error', f'Exception pushing {requisition.name}: {str(e)}')
    
    def _pull_requisitions(self):
        """Pull requisitions from external system"""
        if not REQUESTS_AVAILABLE:
            return False
            
        try:
            headers = self._get_headers()
            # Add timestamp filter if available
            params = {}
            if self.last_sync:
                params['modified_since'] = self.last_sync.isoformat()
            
            response = requests.get(
                f"{self.api_url}/requisitions",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                external_requisitions = response.json()
                for ext_req in external_requisitions.get('data', []):
                    self._create_or_update_requisition(ext_req)
                    
                self._create_log('success', f'Pulled {len(external_requisitions.get("data", []))} requisitions')
            else:
                self._create_log('error', f'Failed to pull requisitions: {response.text}')
                
        except Exception as e:
            self._create_log('error', f'Exception pulling requisitions: {str(e)}')
    
    def _map_requisition_to_external(self, requisition):
        """Map Odoo requisition to external system format"""
        # Base mapping
        data = {
            'external_id': requisition.external_reference or requisition.id,
            'name': requisition.name,
            'department': requisition.department_id.name if requisition.department_id else None,
            'priority': requisition.priority,
            'state': requisition.state,
            'requisition_date': requisition.requisition_date.isoformat() if requisition.requisition_date else None,
            'required_date': requisition.required_date.isoformat() if requisition.required_date else None,
            'notes': requisition.notes,
            'lines': []
        }
        
        # Map lines
        for line in requisition.line_ids:
            line_data = {
                'product_code': line.product_id.default_code,
                'product_name': line.product_id.name,
                'quantity': line.quantity,
                'uom': line.uom_id.name,
                'estimated_cost': line.estimated_cost,
                'required_date': line.required_date.isoformat() if line.required_date else None,
                'notes': line.notes
            }
            data['lines'].append(line_data)
        
        # Apply custom field mappings
        for mapping in self.field_mapping_ids:
            if mapping.odoo_field and mapping.external_field:
                value = getattr(requisition, mapping.odoo_field, None)
                if value is not None:
                    data[mapping.external_field] = mapping.transform_value(value)
        
        return data
    
    def _create_or_update_requisition(self, external_data):
        """Create or update requisition from external data"""
        external_id = external_data.get('external_id')
        
        # Check if requisition exists
        existing = self.env['manufacturing.material.requisition'].search([
            ('external_reference', '=', external_id)
        ], limit=1)
        
        # Map external data to Odoo format
        vals = self._map_external_to_requisition(external_data)
        
        if existing:
            existing.write(vals)
            self._create_log('success', f'Updated requisition {existing.name} from external system')
        else:
            new_req = self.env['manufacturing.material.requisition'].create(vals)
            self._create_log('success', f'Created requisition {new_req.name} from external system')
    
    def _map_external_to_requisition(self, external_data):
        """Map external data to Odoo requisition format"""
        vals = {
            'external_reference': external_data.get('external_id'),
            'name': external_data.get('name', 'Imported Requisition'),
            'priority': external_data.get('priority', '1'),
            'notes': external_data.get('notes', ''),
        }
        
        # Handle dates
        if external_data.get('requisition_date'):
            vals['requisition_date'] = external_data['requisition_date']
        if external_data.get('required_date'):
            vals['required_date'] = external_data['required_date']
        
        # Handle department
        if external_data.get('department'):
            dept = self.env['hr.department'].search([('name', '=', external_data['department'])], limit=1)
            if dept:
                vals['department_id'] = dept.id
        
        # Handle lines
        line_vals = []
        for line_data in external_data.get('lines', []):
            product = self.env['product.product'].search([
                '|', ('default_code', '=', line_data.get('product_code')),
                     ('name', '=', line_data.get('product_name'))
            ], limit=1)
            
            if product:
                line_vals.append((0, 0, {
                    'product_id': product.id,
                    'quantity': line_data.get('quantity', 1),
                    'uom_id': product.uom_id.id,
                    'estimated_cost': line_data.get('estimated_cost', 0),
                    'notes': line_data.get('notes', ''),
                }))
        
        if line_vals:
            vals['line_ids'] = line_vals
        
        return vals
    
    def _create_log(self, log_type, message):
        """Create API log entry"""
        self.env['manufacturing.requisition.api.log'].create({
            'integration_id': self.id,
            'log_type': log_type,
            'message': message,
            'timestamp': fields.Datetime.now()
        })
    
    def send_webhook(self, event_type, requisition_id):
        """Send webhook notification"""
        if not REQUESTS_AVAILABLE:
            self._create_log('warning', 'Cannot send webhook: requests library not available')
            return
            
        if not self.webhook_enabled or not self.webhook_url:
            return
        
        if self.webhook_events != 'all' and self.webhook_events != event_type:
            return
        
        try:
            requisition = self.env['manufacturing.material.requisition'].browse(requisition_id)
            data = {
                'event': event_type,
                'timestamp': fields.Datetime.now().isoformat(),
                'requisition': self._map_requisition_to_external(requisition)
            }
            
            headers = {'Content-Type': 'application/json'}
            
            # Add signature if secret is configured
            if self.webhook_secret:
                payload = json.dumps(data, sort_keys=True)
                signature = hmac.new(
                    self.webhook_secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Webhook-Signature'] = f'sha256={signature}'
            
            response = requests.post(self.webhook_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                self._create_log('webhook', f'Webhook sent for {event_type} on {requisition.name}')
            else:
                self._create_log('error', f'Webhook failed for {event_type}: {response.text}')
                
        except Exception as e:
            self._create_log('error', f'Webhook exception: {str(e)}')
    
    @api.onchange('active')
    def _onchange_active(self):
        """Warn user if requests is not available"""
        if self.active and not REQUESTS_AVAILABLE:
            return {
                'warning': {
                    'title': 'API Integration Limited',
                    'message': 'The requests library is not installed. API features will not work until it is installed.'
                }
            }


class RequisitionAPIFieldMapping(models.Model):
    _name = 'manufacturing.requisition.api.field.mapping'
    _description = 'API Field Mapping'
    _rec_name = 'odoo_field'

    integration_id = fields.Many2one('manufacturing.requisition.api.integration', 
                                    string='Integration', required=True, ondelete='cascade')
    odoo_field = fields.Char(string='Odoo Field', required=True)
    external_field = fields.Char(string='External Field', required=True)
    field_type = fields.Selection([
        ('char', 'Text'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('selection', 'Selection'),
        ('many2one', 'Many2one'),
        ('one2many', 'One2many'),
        ('many2many', 'Many2many')
    ], string='Field Type', default='char')
    
    # Transformation rules
    transformation_type = fields.Selection([
        ('none', 'No Transformation'),
        ('format', 'Format String'),
        ('calculation', 'Python Calculation'),
        ('mapping', 'Value Mapping')
    ], string='Transformation', default='none')
    
    format_string = fields.Char(string='Format String')
    calculation_code = fields.Text(string='Python Code')
    value_mapping = fields.Text(string='Value Mapping (JSON)')
    
    def transform_value(self, value):
        """Transform value according to mapping rules"""
        if self.transformation_type == 'none':
            return value
        elif self.transformation_type == 'format' and self.format_string:
            try:
                return self.format_string.format(value=value)
            except:
                return str(value)
        elif self.transformation_type == 'calculation' and self.calculation_code:
            try:
                # Safe evaluation context
                context = {'value': value, 'datetime': datetime, 'timedelta': timedelta}
                return eval(self.calculation_code, {"__builtins__": {}}, context)
            except:
                return value
        elif self.transformation_type == 'mapping' and self.value_mapping:
            try:
                mapping = json.loads(self.value_mapping)
                return mapping.get(str(value), value)
            except:
                return value
        
        return value


class RequisitionAPILog(models.Model):
    _name = 'manufacturing.requisition.api.log'
    _description = 'API Integration Log'
    _order = 'timestamp desc'
    _rec_name = 'message'

    integration_id = fields.Many2one('manufacturing.requisition.api.integration', 
                                    string='Integration', required=True, ondelete='cascade')
    timestamp = fields.Datetime(string='Timestamp', required=True, default=fields.Datetime.now)
    log_type = fields.Selection([
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('webhook', 'Webhook')
    ], string='Type', required=True, default='info')
    
    message = fields.Text(string='Message', required=True)
    details = fields.Text(string='Details')
    
    # Auto-cleanup old logs
    @api.model
    def _cleanup_old_logs(self):
        """Remove logs older than 30 days"""
        cutoff_date = fields.Datetime.now() - timedelta(days=30)
        old_logs = self.search([('timestamp', '<', cutoff_date)])
        old_logs.unlink()


# Extend the main requisition model to support API integration
class ManufacturingRequisition(models.Model):
    _inherit = 'manufacturing.material.requisition'

    external_reference = fields.Char(string='External Reference', readonly=True)
    api_sync_enabled = fields.Boolean(string='API Sync Enabled', default=True)
    last_api_sync = fields.Datetime(string='Last API Sync', readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to trigger API sync"""
        records = super().create(vals_list)
        for record in records:
            if record.api_sync_enabled:
                self._trigger_api_sync('create', record.id)
        return records
    
    def write(self, vals):
        """Override write to trigger API sync"""
        result = super().write(vals)
        if self.api_sync_enabled and any(key in vals for key in ['state', 'priority', 'line_ids']):
            for record in self:
                self._trigger_api_sync('update', record.id)
        return result
    
    def unlink(self):
        """Override unlink to trigger API sync"""
        for record in self:
            if record.api_sync_enabled:
                self._trigger_api_sync('delete', record.id)
        return super().unlink()
    
    def _trigger_api_sync(self, event_type, requisition_id):
        """Trigger API synchronization"""
        # Only trigger if requests is available
        if not REQUESTS_AVAILABLE:
            return
            
        # Find active integrations
        integrations = self.env['manufacturing.requisition.api.integration'].search([
            ('active', '=', True),
            ('auto_sync', '=', True)
        ])
        
        for integration in integrations:
            if integration.sync_frequency == 'realtime':
                # Immediate sync
                integration.sync_requisitions([requisition_id])
            
            # Send webhook notification
            integration.send_webhook(event_type, requisition_id) 