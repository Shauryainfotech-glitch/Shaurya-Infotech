# Manufacturing Material Requisitions Module for Odoo 18

## Overview
Advanced Material Purchase Requisitions system designed specifically for manufacturing operations in Odoo 18.

## Features
- Manufacturing Order Material Requisitions
- Shop Floor Emergency Requisitions
- MRP Integration with Auto-Requisitions
- Quality Control Material Management
- Maintenance Material Requisitions
- Real-time Inventory Integration
- AI-Powered Demand Forecasting (Optional)
- Mobile Shop Floor App
- Advanced Analytics Dashboard
- Multi-location Manufacturing Support

## Installation

1. Place the module in your Odoo addons directory
2. Update the apps list in Odoo
3. Install the module from Apps menu

## Optional AI Features

The module includes advanced AI capabilities that require additional Python libraries. These are **optional** - the module will work without them, but AI features will be disabled.

### Installing AI Dependencies (Optional)

If you want to enable AI features, install these Python packages:

```bash
pip install numpy pandas scikit-learn requests
```

Or in your Odoo environment:

```bash
cd /path/to/odoo
./odoo-bin shell -d your_database
>>> import subprocess
>>> subprocess.check_call(['pip', 'install', 'numpy', 'pandas', 'scikit-learn', 'requests'])
```

### AI Features Available with Dependencies
- Demand Forecasting
- Cost Prediction
- Vendor Recommendation
- Lead Time Prediction
- Quality Prediction
- Anomaly Detection

## Configuration

### Basic Setup
1. Navigate to Manufacturing → Configuration → Settings
2. Configure approval workflows
3. Set up user permissions

### AI Configuration (if dependencies installed)
1. Navigate to Manufacturing → Configuration → AI Models
2. Train each model using historical data
3. Activate models for automatic predictions

## User Groups
- Manufacturing User - Basic access to create requisitions
- Shop Floor Operator - Create emergency requisitions
- Shop Floor Supervisor - Approve requisitions
- Manufacturing Manager - Full system control

## Emergency Requisitions
For production line emergencies:
1. Use the emergency requisition wizard
2. System sends automatic alerts
3. Bypasses normal approval for critical situations

## Support
For issues or questions, please contact the Manufacturing Solutions Team. 