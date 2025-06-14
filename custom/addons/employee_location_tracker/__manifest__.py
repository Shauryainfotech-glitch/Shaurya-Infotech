{
    'name': 'Employee Location Tracker with AI',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Advanced employee location tracking with AI analytics and geofencing',
    'description': '''
        Employee Location Tracking App with AI Features:
        - Real-time GPS location tracking
        - Geofencing and attendance automation
        - AI-powered route optimization
        - Behavioral pattern analysis
        - Predictive analytics for workforce management
        - Smart alerts and notifications
        - Mobile API integration
        - Advanced reporting and analytics
    ''',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'hr',
        'hr_attendance',
        'mail',
        'web',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ai_analysis_data.xml',
        'data/geofence_demo_data.xml',
        'views/employee_location_views.xml',
        'views/location_tracking_views.xml',
        'views/ai_dashboard_views.xml',
        'views/geofence_views.xml',
        'views/analytics_views.xml',
        'wizard/location_report_wizard_views.xml',
        'reports/location_report.xml',
        'reports/location_report_template.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'employee_location_tracker/static/src/js/location_widget.js',
            'employee_location_tracker/static/src/js/ai_dashboard.js',
            'employee_location_tracker/static/src/js/map_widget.js',
            'employee_location_tracker/static/src/xml/location_templates.xml',
            'employee_location_tracker/static/src/css/location_tracker.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}