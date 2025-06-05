# AI LLM Integration Module

## Overview

The AI LLM Integration module provides comprehensive AI-powered assistance across all Odoo modules, with specialized focus on Purchase Management. This module integrates Large Language Models (LLMs) to enhance productivity, automate content generation, and provide intelligent insights.

## Key Features

### Core AI Integration
- **Multiple LLM Provider Support**: OpenAI, Anthropic Claude, and extensible architecture for additional providers
- **Context-Aware AI**: Intelligent understanding of business context across all modules
- **Conversation History**: Complete tracking of AI interactions
- **Security Groups**: Granular permission control for AI features

### AI Purchase Assistant & Vendor Guide

The module includes advanced AI-powered purchase management capabilities:

#### 🔍 **Vendor Discovery & Analysis**
- **Smart Vendor Search**: AI analyzes product requirements and suggests alternative vendors
- **Performance Scoring**: Automated vendor scoring based on historical data, delivery performance, and quality metrics
- **Category Matching**: Intelligent matching of vendors to product categories
- **Geographic Optimization**: Consider location factors in vendor recommendations

#### 💰 **Price Analysis & Optimization**
- **Historical Price Tracking**: Compare current prices with historical averages
- **Market Trend Analysis**: Identify price trends and seasonal patterns
- **Volume Discount Opportunities**: Suggest bulk purchasing strategies
- **Cost Optimization**: Recommendations for reducing procurement costs

#### 🤝 **Negotiation Strategy**
- **Vendor Relationship Analysis**: Leverage historical business relationships
- **Negotiation Tips**: AI-generated strategies based on vendor behavior patterns
- **Timing Optimization**: Identify best times for negotiations (end of quarter, seasonal patterns)
- **Competitive Leverage**: Use market intelligence for better negotiations

#### ⚠️ **Risk Assessment**
- **Vendor Concentration Risk**: Alert on over-dependence on single vendors
- **Single Source Risk**: Identify products with limited supplier options
- **Delivery Risk Assessment**: Evaluate timeline and capacity risks
- **Quality Risk Indicators**: Flag potential quality issues

#### 📊 **Market Intelligence**
- **Category Analysis**: Deep insights into product category markets
- **Price Benchmarking**: Compare prices across vendors and time periods
- **Supply Chain Insights**: Market conditions and supplier landscape analysis
- **Procurement Recommendations**: Strategic purchasing advice

## Installation & Setup

### Prerequisites
- Odoo 16.0 or later
- Python packages: `requests`, `json`
- AI Provider API keys (OpenAI, Anthropic, etc.)

### Installation Steps

1. **Install the Module**
   ```bash
   # Copy module to addons directory
   cp -r mll /path/to/odoo/addons/
   
   # Update module list and install
   odoo-bin -d your_database -u mll
   ```

2. **Configure AI Providers**
   - Navigate to `AI Assistant → AI Providers`
   - Configure your preferred LLM providers with API credentials

3. **Set Up AI Accounts**
   - Go to `AI Assistant → AI Accounts`
   - Create accounts linking providers with usage limits and user permissions

4. **Configure Security Groups**
   - Assign users to appropriate AI security groups:
     - `AI User`: Basic AI features access
     - `AI Manager`: Advanced features and analytics
     - `AI Administrator`: Full configuration access

## Usage Guide

### Purchase Team Workflow

#### 1. **AI Purchase Dashboard**
Access the enhanced purchase dashboard via `Purchase → AI Purchase Assistant → AI Dashboard`

Features:
- Kanban view with AI insights badges
- Quick access to vendor analysis
- Real-time AI recommendations display

#### 2. **Vendor Analysis Workflow**

**Step 1: Create/Open Purchase Order**
- Create a new purchase order or open existing draft order
- Add product lines with quantities and specifications

**Step 2: Launch AI Analysis**
- Click "AI Vendor Analysis" button in the purchase order
- Select analysis type:
  - **Find Alternative Vendors**: Discover new supplier options
  - **Price Analysis**: Compare current pricing with market data
  - **Negotiation Strategy**: Get tailored negotiation advice
  - **Risk Assessment**: Identify potential procurement risks
  - **Market Analysis**: Understand market conditions

**Step 3: Review AI Recommendations**
- Analyze vendor suggestions with performance scores
- Review negotiation tips and market insights
- Use "Contact Vendor" or "Create RFQ" for recommended suppliers

**Step 4: Execute Procurement Strategy**
- Apply AI recommendations to your procurement process
- Track results and vendor performance
- Build historical data for improved future recommendations

#### 3. **Advanced Features**

**AI Insights Tab**
Every purchase order includes an "AI Insights" tab showing:
- Vendor suggestions with performance metrics
- Negotiation tips based on vendor history
- Market intelligence and pricing trends

**Automated Vendor Scoring**
The system automatically calculates vendor scores based on:
- Historical delivery performance
- Order frequency and reliability
- Geographic proximity
- Quality ratings (if available)
- Business relationship value

**Smart Notifications**
AI-powered alerts for:
- Price anomalies (above historical average)
- Vendor concentration risks
- Single-source dependencies
- Optimal negotiation timing

## AI Capabilities by Module

### Sales Management
- Quotation content generation
- Product description enhancement
- Customer communication optimization

### Project Management
- Task description generation
- Project planning assistance
- Resource allocation recommendations

### Human Resources
- Employee profile insights
- Performance analysis support
- Training recommendations

### Accounting
- Invoice analysis and categorization
- Financial report insights
- Expense optimization suggestions

## Security & Permissions

### Security Groups
- **AI User** (`mll.group_ai_user`): Basic AI features
- **AI Manager** (`mll.group_ai_manager`): Advanced analytics and management
- **AI Administrator** (`mll.group_ai_admin`): Full system configuration

### Data Protection
- API keys are encrypted and access-controlled
- Conversation history is user-specific
- Sensitive fields are protected by security groups
- Audit trail for all AI interactions

## Configuration

### AI Provider Setup
1. Navigate to `AI Assistant → AI Providers`
2. Configure providers:
   - **OpenAI**: Requires API key and model selection
   - **Anthropic Claude**: Requires API key and model version
   - **Custom Providers**: Extensible architecture for additional LLMs

### Account Management
1. Go to `AI Assistant → AI Accounts`
2. Create accounts with:
   - Provider selection
   - API credentials (admin-only access)
   - Usage limits and monitoring
   - User access permissions

### Usage Monitoring
- Track API usage per account
- Monitor costs and limits
- Performance analytics
- User activity reports

## Troubleshooting

### Common Issues

**AI Features Not Visible**
- Check user security group assignments
- Verify module installation and dependencies
- Ensure AI accounts are properly configured

**API Connection Errors**
- Verify API keys are correct and active
- Check internet connectivity
- Validate provider account status and limits

**Performance Issues**
- Monitor API usage and rate limits
- Optimize conversation history cleanup
- Review system resources and database performance

### Support & Maintenance

**Regular Maintenance**
- Monitor API usage and costs
- Update provider configurations as needed
- Review and clean conversation history
- Update security permissions as organization changes

**Performance Optimization**
- Implement caching for frequently accessed AI insights
- Optimize database queries for large datasets
- Consider API rate limiting for high-volume usage

## Extending the Module

### Adding New AI Providers
1. Extend the `ai.llm.provider` model
2. Implement provider-specific API integration
3. Add configuration fields and validation
4. Update security and access controls

### Custom AI Features
1. Inherit from `ai.llm.mixin` for new models
2. Implement context-specific AI methods
3. Create custom wizards for specialized workflows
4. Add appropriate security and permissions

### Integration with Other Modules
The module is designed for easy integration with custom Odoo modules:
- Inherit from AI mixin classes
- Implement model-specific context methods
- Add AI-powered features to existing workflows

## API Reference

### Core Models
- `ai.llm.provider`: LLM provider configuration
- `ai.llm.account`: AI account management
- `ai.llm.conversation`: Conversation tracking
- `ai.llm.mixin`: Base AI functionality for models

### Purchase-Specific Models
- `ai.purchase.assistant`: Purchase analysis wizard
- `ai.vendor.recommendation`: Vendor recommendation system

### Key Methods
- `_get_ai_context()`: Generate model-specific context
- `action_ai_analyze_vendor()`: Launch vendor analysis
- `_compute_ai_vendor_suggestions()`: Generate vendor recommendations
- `_compute_ai_negotiation_tips()`: Create negotiation strategies

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Support

For support and customization requests, contact your Odoo implementation partner or system administrator.
