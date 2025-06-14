# Employee Location Tracker with AI - Odoo 18 Module

A comprehensive employee location tracking system with AI-powered analytics, geofencing, and real-time monitoring capabilities.

## Features

### Core Features
- **Real-time GPS Location Tracking**: Track employee locations with high accuracy
- **Geofencing**: Create circular, rectangular, or polygon geofences with automated actions
- **AI-Powered Analytics**: Detect anomalies, analyze behavior patterns, and provide insights
- **Attendance Integration**: Automatic attendance marking based on geofence entry/exit
- **Mobile API**: RESTful API for mobile app integration
- **Advanced Reporting**: Comprehensive reports with PDF, Excel, and CSV export

### AI & Analytics
- **Anomaly Detection**: Detect unusual location patterns, unrealistic speeds, and GPS accuracy issues
- **Behavior Pattern Analysis**: Classify employee movement patterns (normal, traveling, stationary, etc.)
- **Route Optimization**: Analyze and suggest optimal routes
- **Predictive Analytics**: Predict next locations based on historical data
- **Confidence Scoring**: AI confidence scores for location validation

### Geofencing
- **Multiple Geofence Types**: Circle, polygon, and rectangle geofences
- **Automated Actions**: Auto-attendance, alerts on entry/exit
- **Time Restrictions**: Configure allowed hours for geofences
- **Employee Permissions**: Control which employees can access specific geofences

### Security & Privacy
- **Role-Based Access Control**: User, Manager, and Administrator roles
- **Data Retention**: Configurable data retention policies
- **Privacy Mode**: Employee-controlled tracking activation
- **Battery Optimization**: Smart tracking based on battery levels

## Installation

### Prerequisites
- Odoo 18.0+
- Python 3.8+
- PostgreSQL 12+

### Required Python Packages
```bash
pip install requests
pip install xlsxwriter  # For Excel reports
pip install shapely     # For advanced geospatial operations
pip install pyproj      # For coordinate transformations
```

### Installation Steps

1. **Download the module**:
   ```bash
   cd /path/to/odoo/addons
   git clone <repository-url> employee_location_tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r employee_location_tracker/requirements.txt
   ```

3. **Update Odoo addons list**:
   - Go to Apps menu in Odoo
   - Click "Update Apps List"

4. **Install the module**:
   - Search for "Employee Location Tracker"
   - Click Install

5. **Configure the module**:
   - Go to Location Tracking > Configuration
   - Set up geofences and tracking settings
   - Configure AI analysis parameters

## Configuration

### Basic Setup

1. **Create Geofences**:
   - Navigate to Location Tracking > Geofences
   - Create geofences for office locations, client sites, etc.
   - Configure automation rules (auto-attendance, alerts)

2. **Configure Tracking Settings**:
   - Go to Location Tracking > Configuration > Tracking Settings
   - Set up tracking frequency, privacy settings, and data retention
   - Configure battery optimization and notification preferences

3. **Set Up User Permissions**:
   - Assign users to appropriate groups:
     - Location Tracking User: Basic access
     - Location Tracking Manager: Full access to team data
     - Location Tracking Administrator: Full system access

### API Configuration

The module provides REST API endpoints for mobile app integration:

- `POST /api/location/submit` - Submit location data
- `POST /api/location/bulk_submit` - Submit multiple locations
- `GET /api/location/employee/<id>` - Get employee locations
- `POST /api/geofence/check` - Check geofence status
- `GET /api/analytics/summary` - Get analytics summary

### AI Configuration

Configure AI parameters in Settings:
- `location_tracker.ai_enabled` - Enable/disable AI features
- `location_tracker.ai_confidence_threshold` - Minimum confidence for auto-validation
- `location_tracker.max_speed_threshold` - Maximum realistic speed (km/h)
- `location_tracker.gps_accuracy_threshold` - GPS accuracy threshold (meters)

## Usage

### For Employees
1. **Location Submission**: Use mobile app or web interface to submit locations
2. **Privacy Control**: Enable/disable tracking through privacy mode
3. **View Own Data**: Access personal location history and analytics

### For Managers
1. **Team Monitoring**: View real-time locations of team members
2. **Analytics Dashboard**: Access comprehensive analytics and insights
3. **Report Generation**: Create detailed reports for analysis
4. **Geofence Management**: Set up and manage location boundaries

### For Administrators
1. **System Configuration**: Configure global settings and AI parameters
2. **User Management**: Manage permissions and access rights
3. **Data Management**: Handle data retention and cleanup
4. **Advanced Analytics**: Access all system analytics and reports

## API Reference

### Submit Location
```http
POST /api/location/submit
Content-Type: application/json

{
  "employee_id": 1,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "accuracy": 10,
  "location_type": "work_location",
  "battery_level": 85,
  "network_type": "wifi"
}
```

### Check Geofence
```http
POST /api/geofence/check
Content-Type: application/json

{
  "latitude": 37.7749,
  "longitude": -122.4194
}
```

## Troubleshooting

### Common Issues

1. **GPS Accuracy Problems**:
   - Check device GPS settings
   - Ensure location permissions are granted
   - Consider environmental factors (indoor/outdoor)

2. **AI Analysis Not Working**:
   - Verify AI is enabled in configuration
   - Check if sufficient historical data exists
   - Review error logs for specific issues

3. **Geofence Detection Issues**:
   - Verify geofence coordinates are correct
   - Check geofence is active
   - Test with manual coordinate input

### Performance Optimization

1. **Database Optimization**:
   - Regularly clean up old location data
   - Index frequently queried fields
   - Monitor database performance

2. **API Performance**:
   - Implement rate limiting for API endpoints
   - Use bulk operations when possible
   - Cache frequently accessed data

## Development

### Module Structure
```
employee_location_tracker/
├── __manifest__.py          # Module manifest
├── models/                  # Data models
├── controllers/             # HTTP controllers
├── views/                   # XML views
├── security/               # Access control
├── data/                   # Demo and configuration data
├── static/                 # JavaScript, CSS, images
├── utils/                  # Utility functions
├── wizard/                 # Wizards
└── reports/                # Report templates
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Testing

Run tests with:
```bash
python -m odoo -c odoo.conf -d test_db --test-enable --stop-after-init -i employee_location_tracker
```

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Contact: support@yourcompany.com
- Documentation: https://docs.yourcompany.com/location-tracker

## Changelog

### Version 1.0.0
- Initial release
- Basic location tracking
- Geofencing support
- AI analytics
- Mobile API
- Reporting system
"""

# requirements.txt
requests>=2.25.0
xlsxwriter>=3.0.0
shapely>=1.8.0
pyproj>=3.2.0
numpy>=1.21.0
