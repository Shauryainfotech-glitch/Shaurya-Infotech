# AI LLM Integration for Odoo 18

A comprehensive AI Large Language Model integration module for Odoo 18 that provides intelligent assistance, automation, and insights across all Odoo modules.

## Features

- **Universal AI Assistant**: Accessible from any Odoo module with context-aware responses
- **Multi-Provider Support**: OpenAI, Anthropic, Google AI, and custom providers
- **Automated Content Generation**: Generate emails, descriptions, summaries, and analysis
- **Conversation History**: Track and manage AI interactions
- **Security & Access Control**: Role-based permissions and usage limits
- **Cross-Module Integration**: AI capabilities added to Partners, Sales, Projects, HR, and Accounting

## Installation

1. **Copy Module**: Place the `ai_llm_integration` folder in your Odoo addons directory
2. **Update Apps List**: Go to Apps menu and click "Update Apps List"
3. **Install Module**: Search for "AI LLM Integration" and click Install

## Configuration

### 1. Configure AI Providers

Navigate to **AI Assistant > Configuration > AI Providers**

Default providers are pre-configured:
- OpenAI GPT-4
- OpenAI GPT-3.5 Turbo
- Anthropic Claude 3
- Google Gemini Pro

### 2. Create AI Accounts

Navigate to **AI Assistant > AI Accounts**

1. Click "Create"
2. Enter account name
3. Select provider
4. Enter API key (obtain from provider's website)
5. Set usage limits
6. Assign users (optional - leave empty for all users)
7. Click "Activate"

### 3. Assign User Permissions

Navigate to **Settings > Users & Companies > Users**

Assign appropriate AI groups:
- **AI User**: Basic access to AI features
- **AI Manager**: Can manage accounts and view all conversations
- **AI Administrator**: Full access including provider configuration

## Usage

### Universal AI Assistant

1. **From Any Record**: Click the "AI Assistant" button on any form view
2. **Chat Widget**: Use the floating AI chat widget (if enabled)
3. **Menu Access**: Navigate to AI Assistant menu for conversations

### Content Generation

The AI assistant can help with:

- **Summaries**: Generate concise summaries of records
- **Emails**: Draft professional emails
- **Descriptions**: Create product or service descriptions
- **Analysis**: Analyze data and provide insights
- **Custom Requests**: Any specific AI assistance needed

### Context-Aware Assistance

The AI automatically understands the context of your current record:

- **Partners**: Knows customer/vendor details, contact info, history
- **Sales Orders**: Understands order details, products, amounts
- **Projects**: Aware of tasks, deadlines, team members
- **Invoices**: Knows billing details, amounts, due dates
- **Employees**: Understands roles, departments, managers

## API Integration

### Getting API Keys

#### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create account or sign in
3. Navigate to API Keys section
4. Create new secret key
5. Copy and paste into Odoo AI Account

#### Anthropic
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create account or sign in
3. Navigate to API Keys
4. Generate new key
5. Copy and paste into Odoo AI Account

#### Google AI
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Create account or sign in
3. Generate API key
4. Copy and paste into Odoo AI Account

## Security

### Data Protection
- API keys are encrypted and only visible to administrators
- Conversations are isolated by user (unless manager/admin)
- Company-based access control for multi-company setups

### Usage Controls
- Monthly usage limits per account
- Rate limiting to prevent abuse
- Audit trail of all AI interactions

## Customization

### Adding AI to Custom Models

```python
class MyCustomModel(models.Model):
    _name = 'my.custom.model'
    _inherit = ['my.custom.model', 'ai.llm.mixin']
    
    def _get_ai_context(self):
        """Provide model-specific context for AI"""
        context = super()._get_ai_context()
        context_data = json.loads(context)
        context_data.update({
            'custom_field': self.custom_field,
            'related_data': self.related_id.name,
        })
        return json.dumps(context_data)
```

### Custom Prompt Types

Extend the wizard to add custom prompt types:

```python
class AiContentGenerator(models.TransientModel):
    _inherit = 'ai.content.generator'
    
    prompt_type = fields.Selection(
        selection_add=[
            ('custom_type', 'My Custom Type'),
        ]
    )
```

## Troubleshooting

### Common Issues

1. **"No active AI account available"**
   - Ensure at least one AI account is activated
   - Check user permissions
   - Verify API key is correct

2. **API Connection Errors**
   - Verify API key is valid
   - Check internet connectivity
   - Ensure API endpoint is correct

3. **Permission Denied**
   - Check user has appropriate AI group assigned
   - Verify account user restrictions

### Debug Mode

Enable developer mode to access:
- Conversation metadata
- API request/response details
- Error logs

## Support

For issues and feature requests:
1. Check the conversation logs in AI Assistant > Conversations
2. Review Odoo logs for detailed error messages
3. Verify API provider status and quotas

## License

This module is licensed under LGPL-3.

## Credits

Developed for Odoo 18 Community and Enterprise editions.
