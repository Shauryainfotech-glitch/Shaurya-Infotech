{
    'name': 'Manufacturing Material Requisitions',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Comprehensive material requisition management for manufacturing environments',
    'description': """
Manufacturing Material Requisitions - Advanced Edition

This comprehensive module provides a complete solution for managing material requisitions 
in manufacturing environments. Features include:

Core Features:
- Multi-department requisitions with approval workflows
- Template-based creation for recurring materials
- Emergency requisition fast-track processing
- Comprehensive cost estimation and tracking
- Integration with purchase and inventory modules

Shop Floor Integration:
- Dedicated terminals for production operators
- Real-time material availability displays
- Barcode scanning and mobile support
- Production line integration with MRP

Advanced Analytics & AI:
- Predictive demand forecasting
- AI-powered approval recommendations
- Performance dashboards and KPIs
- Custom reporting with visualizations

Automation & Optimization:
- Intelligent scheduling based on stock levels
- Multi-algorithm optimization engine
- Rule-based automation
- Bulk processing capabilities

API Integration:
- RESTful API for external systems
- Real-time webhooks
- Bidirectional synchronization
- Multiple authentication methods

Quality & Maintenance:
- Quality control integration
- Maintenance schedule integration
- Supplier performance tracking
- Compliance management

Mobile & Responsive:
- Progressive Web App (PWA) support
- Touch-optimized interfaces
- Offline capability
- Cross-platform compatibility

This module is fully Odoo 18 compliant with modern UI components and security features.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'stock',
        'purchase',
        'mrp',
        'quality_control',
        'maintenance',
        'mail',
        'web',
        'account'
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/requisition_sequence.xml',
        'data/email_templates.xml',
        'data/requisition_categories.xml',
        
        # Views - Core
        'views/manufacturing_requisition_views.xml',
        'views/requisition_dashboard_views.xml',
        
        # Views - Shop Floor
        'views/shop_floor_views.xml',
        'views/mobile_views.xml',
        
        # Views - Analytics & AI
        'views/analytics_views.xml',
        'views/requisition_ai_views.xml',
        
        # Views - Automation
        'views/requisition_scheduling_views.xml',
        
        # Views - Integration
        'views/purchase_integration_views.xml',
        'views/inventory_integration_views.xml',
        'views/mrp_integration_views.xml',
        'views/quality_requisition_views.xml',
        'views/maintenance_requisition_views.xml',
        
        # Wizards
        'views/bulk_requisition_wizard_views.xml',
        'views/emergency_requisition_wizard_views.xml',
        'views/mrp_requisition_wizard_views.xml',
        
        # Reports
        'reports/manufacturing_requisition_reports.xml',
        'reports/analytics_reports.xml',
        
        # Demo Data
        'demo/manufacturing_demo.xml',
        'demo/shop_floor_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'manufacturing_material_requisitions/static/src/css/requisition.css',
            'manufacturing_material_requisitions/static/src/css/shop_floor.css',
            'manufacturing_material_requisitions/static/src/css/mobile.css',
            'manufacturing_material_requisitions/static/src/js/requisition_dashboard.js',
            'manufacturing_material_requisitions/static/src/js/shop_floor_terminal.js',
            'manufacturing_material_requisitions/static/src/js/barcode_scanner.js',
            'manufacturing_material_requisitions/static/src/xml/dashboard_templates.xml',
            'manufacturing_material_requisitions/static/src/xml/shop_floor_templates.xml',
        ],
        'web.assets_frontend': [
            'manufacturing_material_requisitions/static/src/css/mobile.css',
            'manufacturing_material_requisitions/static/src/js/mobile_app.js',
        ],
        'web.qunit_suite_tests': [
            'manufacturing_material_requisitions/static/tests/**/*',
        ],
    },
    'demo': [
        'demo/manufacturing_demo.xml',
        'demo/shop_floor_demo.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 95,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
} 