# AVGC Tender Management System

A comprehensive Odoo module for managing tenders, GeM bids, vendors, and documents with AI-powered analysis capabilities.

## Features

### Core Functionality
- **Tender Management**: Complete lifecycle management of tenders from creation to award
- **GeM Bid Management**: Specialized handling of Government e-Marketplace bids
- **Vendor Management**: Comprehensive vendor database with performance tracking
- **Document Management**: Secure document storage with version control and sharing
- **Task Management**: Project-based task tracking with templates and workflows

### Advanced Features
- **AI Analysis**: Document analysis using multiple AI providers (OpenAI, Claude, Gemini)
- **OCR Processing**: Automated text extraction from scanned documents
- **Analytics Dashboard**: Real-time insights and performance metrics
- **Financial Management**: Budget tracking and payment schedules
- **Approval Workflows**: Multi-level approval processes
- **Audit Logging**: Comprehensive activity tracking

## Module Structure

```
avgc_tender_management/
├── __manifest__.py                 # Module manifest
├── README.md                       # This file
├── models/                         # Python model files
│   ├── __init__.py
│   ├── tender.py                   # Tender models
│   ├── gem_bid.py                  # GeM bid models
│   ├── vendor.py                   # Vendor models
│   ├── document.py                 # Document models
│   ├── task.py                     # Task models
│   ├── finance.py                  # Finance models
│   ├── ai_analysis.py              # AI analysis models
│   ├── ocr_service.py              # OCR service models
│   ├── analytics.py                # Analytics models
│   └── settings.py                 # System settings
├── views/                          # XML view definitions
│   ├── tender_views.xml            # Tender views
│   ├── vendor_views.xml            # Vendor views
│   ├── gem_bid_views.xml           # GeM bid views
│   ├── document_views.xml          # Document views
│   ├── analytics_views.xml         # Analytics and dashboard views
│   ├── ocr_views.xml               # OCR processing views
│   ├── finance_views.xml           # Finance management views
│   ├── task_views.xml              # Task management views
│   ├── firm_views.xml              # Firm management views
│   ├── settings_views.xml          # System settings views
│   └── menu_views.xml              # Menu structure
├── wizards/                        # Wizard definitions
│   ├── ai_analysis_wizard.xml      # AI analysis wizard
│   └── tender_processing_wizard.xml # Tender processing wizard
├── reports/                        # Report templates
│   └── tender_reports.xml          # PDF report templates
├── data/                           # Master data
│   ├── tender_categories.xml       # Tender categories
│   ├── tender_stages.xml           # Tender workflow stages
│   ├── gem_bid_stages.xml          # GeM bid stages
│   ├── task_templates.xml          # Task templates
│   └── firm_data.xml               # Firm master data
├── demo/                           # Demo data
│   └── tender_demo.xml             # Sample records
├── security/                       # Security definitions
│   ├── tender_security.xml         # Security groups and rules
│   └── ir.model.access.csv         # Access control matrix
└── static/                         # Static assets
    ├── description/
    │   └── icon.png                # Module icon
    ├── src/
    │   ├── js/
    │   │   └── tender_dashboard.js  # Dashboard JavaScript
    │   └── css/
    │       └── tender_style.css     # Custom styles
    └── img/
        └── tender_banner.png        # Banner image
```

## Installation

1. Copy the module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the "AVGC Tender Management" module
4. Configure system settings as needed

## Configuration

### AI Configuration
1. Go to AI & Analytics > AI Configuration
2. Set up your preferred AI provider (OpenAI, Claude, or Gemini)
3. Enter API keys and configure analysis parameters

### OCR Configuration
1. Navigate to AI & Analytics > OCR Processing
2. Configure OCR provider settings
3. Set up document processing workflows

### Security Setup
1. Assign users to appropriate security groups:
   - Tender User: Basic tender operations
   - Tender Manager: Advanced tender management
   - Tender Admin: Full system administration

## Usage

### Creating a Tender
1. Go to Tender Management > Tenders
2. Click "Create" and fill in tender details
3. Add required documents and specifications
4. Publish the tender when ready

### Managing GeM Bids
1. Navigate to GeM Bid Management > GeM Bids
2. Create new bid entries for government tenders
3. Track progress through predefined stages
4. Monitor win probability and submission status

### Vendor Management
1. Access Vendor Management > Vendors
2. Add vendor information and documents
3. Track performance metrics and ratings
4. Manage vendor categories and evaluations

### Document Processing
1. Upload documents through Document Management
2. Use AI analysis for automatic document review
3. Apply OCR for text extraction from scanned files
4. Share documents with stakeholders securely

## API Integration

The module supports integration with:
- Government e-Marketplace (GeM) APIs
- AI service providers (OpenAI, Anthropic, Google)
- OCR services (Tesseract, Google Vision, AWS Textract)
- Email and notification services

## Reporting

Available reports include:
- Tender Summary Reports
- Vendor Performance Analysis
- Financial Reports
- AI Analysis Statistics
- Custom analytics dashboards

## Support

For technical support and customization requests, please contact the development team.

## License

This module is licensed under LGPL-3.
