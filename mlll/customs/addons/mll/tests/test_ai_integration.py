from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestAiIntegration(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Create test provider
        self.provider = self.env['ai.llm.provider'].create({
            'name': 'Test Provider',
            'code': 'openai',
            'api_endpoint': 'https://api.openai.com/v1/chat/completions',
            'model_name': 'gpt-3.5-turbo',
            'auth_type': 'api_key',
        })
        
        # Create test account
        self.account = self.env['ai.llm.account'].create({
            'name': 'Test Account',
            'provider_id': self.provider.id,
            'api_key': 'test-key-123',
            'company_id': self.env.company.id,
        })
        
        # Create test user
        self.test_user = self.env['res.users'].create({
            'name': 'Test AI User',
            'login': 'test_ai_user',
            'groups_id': [(4, self.env.ref('ai_llm_integration.group_ai_user').id)]
        })
    
    def test_account_activation(self):
        """Test account activation process"""
        self.assertEqual(self.account.state, 'draft')
        
        # Mock the connection test
        self.account._test_connection = lambda: True
        self.account.action_activate()
        
        self.assertEqual(self.account.state, 'active')
    
    def test_conversation_creation(self):
        """Test conversation creation and message handling"""
        conversation = self.env['ai.llm.conversation'].create({
            'account_id': self.account.id,
            'user_id': self.env.user.id,
            'model_name': 'res.partner',
            'res_id': 1,
        })
        
        self.assertTrue(conversation.exists())
        self.assertEqual(conversation.user_id, self.env.user)
        
        # Add test messages
        message1 = self.env['ai.llm.message'].create({
            'conversation_id': conversation.id,
            'role': 'user',
            'content': 'Test question',
        })
        
        message2 = self.env['ai.llm.message'].create({
            'conversation_id': conversation.id,
            'role': 'assistant',
            'content': 'Test response',
            'token_count': 10,
        })
        
        self.assertEqual(len(conversation.message_ids), 2)
        self.assertEqual(conversation.total_tokens, 10)
    
    def test_mixin_integration(self):
        """Test AI mixin integration with res.partner"""
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
            'phone': '+1234567890',
        })
        
        # Test context generation
        context = partner._get_ai_context()
        self.assertIn('partner_name', context)
        self.assertIn('email', context)
        self.assertIn('phone', context)
        
        # Test AI assistant action
        action = partner.action_open_ai_assistant()
        self.assertEqual(action['res_model'], 'ai.content.generator')
        self.assertEqual(action['context']['default_model_name'], 'res.partner')
        self.assertEqual(action['context']['default_res_id'], partner.id)
    
    def test_content_generator(self):
        """Test AI content generator wizard"""
        wizard = self.env['ai.content.generator'].create({
            'prompt_type': 'custom',
            'custom_prompt': 'Test prompt',
            'model_name': 'res.partner',
            'res_id': 1,
            'max_tokens': 100,
        })
        
        # Mock AI client response
        def mock_send_request(*args, **kwargs):
            return {
                'content': 'Test AI response',
                'usage': {'total_tokens': 10},
                'success': True
            }
        
        self.env['ai.llm.client'].send_request = mock_send_request
        
        # Test generation
        result = wizard.action_generate()
        self.assertEqual(wizard.ai_response, 'Test AI response')
        self.assertTrue(result['res_id'])
    
    def test_security_rules(self):
        """Test security rules and access rights"""
        Conversation = self.env['ai.llm.conversation']
        
        # Create conversation as admin
        conv_admin = Conversation.create({
            'account_id': self.account.id,
            'user_id': self.env.user.id,
        })
        
        # Switch to test user
        Conversation = Conversation.with_user(self.test_user)
        
        # Create conversation as test user
        conv_user = Conversation.create({
            'account_id': self.account.id,
            'user_id': self.test_user.id,
        })
        
        # Test user should only see their own conversations
        conversations = Conversation.search([])
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0], conv_user)
    
    def test_api_client(self):
        """Test AI client API handling"""
        client = self.env['ai.llm.client']
        
        # Test with inactive account
        with self.assertRaises(UserError):
            client.send_request(self.account.id, [{'role': 'user', 'content': 'test'}])
        
        # Activate account and test
        self.account._test_connection = lambda: True
        self.account.action_activate()
        
        # Test with unsupported provider
        self.provider.code = 'unsupported'
        with self.assertRaises(UserError):
            client.send_request(self.account.id, [{'role': 'user', 'content': 'test'}])
