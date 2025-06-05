# OmniHR AI Platform for Odoo 18

## Overview
Advanced Multi-AI HR Management System with OpenAI, Claude & Gemini Integration for Odoo 18.

## Features
- Multi-AI Provider Integration (OpenAI, Claude, Gemini)
- Intelligent Recruitment & Candidate Assessment
- Predictive Performance Analytics
- Real-time Employee Sentiment Analysis
- Advanced HR Chatbot with Consensus Intelligence
- Automated HR Workflows & Decision Making

## Installation

### Prerequisites
- Odoo 18.0
- Python 3.10+
- Required Python packages (install via pip):
  ```bash
  pip install requests
  ```

### Deployment Steps

1. **Upload Module**
   - Upload the `omnihr_ai_platform` folder to your Odoo addons directory
   - Or upload as a ZIP file to Odoo.sh

2. **Install Module**
   - Go to Apps menu in Odoo
   - Update Apps List
   - Search for "OmniHR AI Platform"
   - Click Install

3. **Configure AI Providers**
   - Go to OmniHR AI Platform > Configuration > AI Providers
   - Add your API keys for OpenAI, Claude, and/or Gemini
   - Set provider priorities and configurations

4. **Set Permissions**
   - Assign users to appropriate groups:
     - AI Platform User: Basic access
     - AI Platform Manager: Management access
     - AI Platform Administrator: Full access

## Configuration

### AI Provider Setup
1. Navigate to Configuration > AI Providers
2. Configure each provider with:
   - API Key
   - Model selection
   - Rate limits
   - Cost settings

### AI Configuration
1. Go to Configuration > AI Configuration
2. Set up:
   - Multi-provider settings
   - Consensus mode
   - Budget limits
   - Quality assurance settings

## Usage

### Employee Intelligence
- Analyze employee personality, skills, and performance
- Get AI-powered insights and recommendations
- Track sentiment and flight risk

### Recruitment AI
- Automated resume screening
- Candidate assessment and scoring
- Interview evaluation assistance

### Performance Analytics
- Predictive performance modeling
- Trend analysis and forecasting
- Training recommendations

### AI Chat
- Interactive HR assistant
- Context-aware conversations
- Multi-language support

## Troubleshooting

### Common Issues

1. **Module Installation Fails**
   - Check Odoo version compatibility (requires 18.0)
   - Verify all dependencies are installed
   - Check server logs for specific errors

2. **AI Providers Not Working**
   - Verify API keys are correct
   - Check internet connectivity
   - Review provider-specific rate limits

3. **Views Not Loading**
   - Update module after changes
   - Clear browser cache
   - Check for JavaScript errors in browser console

### Support
For technical support, contact: support@omnihr.ai

## License
LGPL-3

## Version
18.0.1.0.0 