from odoo import models, fields, api
from datetime import datetime, timedelta
import base64
import io
import json
from odoo.exceptions import UserError


class LocationReportWizard(models.TransientModel):
    _name = 'hr.location.report.wizard'
    _description = 'Location Report Wizard'

    # Report Parameters
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('analytics', 'Analytics Report'),
        ('anomaly', 'Anomaly Report'),
        ('geofence', 'Geofence Report')
    ], string='Report Type', default='summary', required=True)

    # Date Range
    date_from = fields.Date(
        string='Date From',
        default=lambda self: fields.Date.today() - timedelta(days=30),
        required=True
    )
    date_to = fields.Date(
        string='Date To',
        default=fields.Date.today,
        required=True
    )

    # Filters
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees',
        help="Leave empty to include all employees"
    )
    department_ids = fields.Many2many(
        'hr.department',
        string='Departments'
    )
    geofence_ids = fields.Many2many(
        'hr.location.geofence',
        string='Geofences'
    )
    location_types = fields.Selection([
        ('work_location', 'Work Location'),
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('travel', 'Travel'),
        ('client_visit', 'Client Visit'),
        ('meeting', 'Meeting'),
        ('home', 'Home Office'),
        ('other', 'Other')
    ], string='Location Type Filter')

    # Report Options
    include_anomalies_only = fields.Boolean(
        string='Anomalies Only',
        help="Include only locations with detected anomalies"
    )
    include_map = fields.Boolean(
        string='Include Map',
        default=True,
        help="Include location map in report"
    )
    include_charts = fields.Boolean(
        string='Include Charts',
        default=True,
        help="Include analytics charts in report"
    )

    # Output Format
    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV')
    ], string='Output Format', default='pdf', required=True)

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    def action_generate_report(self):
        """Generate the location report"""
        self.ensure_one()

        # Get filtered data
        domain = self._get_report_domain()
        locations = self.env['hr.employee.location'].search(domain)

        if not locations:
            raise UserError("No location data found for the selected criteria.")

        # Generate report based on type and format
        if self.output_format == 'pdf':
            return self._generate_pdf_report(locations)
        elif self.output_format == 'xlsx':
            return self._generate_excel_report(locations)
        elif self.output_format == 'csv':
            return self._generate_csv_report(locations)

    def _get_report_domain(self):
        """Build domain for report data"""
        domain = [
            ('timestamp', '>=', self.date_from),
            ('timestamp', '<=', self.date_to),
            ('company_id', '=', self.company_id.id)
        ]

        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        elif self.department_ids:
            employees = self.env['hr.employee'].search([
                ('department_id', 'in', self.department_ids.ids)
            ])
            domain.append(('employee_id', 'in', employees.ids))

        if self.geofence_ids:
            domain.append(('geofence_id', 'in', self.geofence_ids.ids))

        if self.location_types:
            domain.append(('location_type', '=', self.location_types))

        if self.include_anomalies_only:
            domain.append(('anomaly_detected', '=', True))

        return domain

    def _generate_pdf_report(self, locations):
        """Generate PDF report"""
        report_data = self._prepare_report_data(locations)

        return self.env.ref('employee_location_tracker.location_report_pdf').report_action(
            self, data=report_data
        )

    def _generate_excel_report(self, locations):
        """Generate Excel report"""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError("xlsxwriter library not installed. Please install it to generate Excel reports.")

        # Create workbook in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Create worksheets
        self._create_summary_worksheet(workbook, locations)
        self._create_detailed_worksheet(workbook, locations)

        if self.report_type == 'analytics':
            self._create_analytics_worksheet(workbook, locations)

        if self.report_type == 'anomaly' or self.include_anomalies_only:
            anomaly_locations = locations.filtered('anomaly_detected')
            if anomaly_locations:
                self._create_anomaly_worksheet(workbook, anomaly_locations)

        workbook.close()
        output.seek(0)

        # Create attachment
        filename = f"location_report_{self.date_from}_{self.date_to}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _generate_csv_report(self, locations):
        """Generate CSV report"""
        import csv

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        header = [
            'Employee', 'Timestamp', 'Latitude', 'Longitude', 'Address',
            'Location Type', 'Accuracy (m)', 'Distance from Last (km)',
            'Geofence', 'Inside Geofence', 'AI Confidence', 'Anomaly Detected',
            'Status', 'Battery Level', 'Network Type'
        ]
        writer.writerow(header)

        # Write data
        for location in locations.sorted('timestamp'):
            row = [
                location.employee_id.name,
                location.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                location.latitude,
                location.longitude,
                location.address or '',
                location.location_type,
                location.accuracy or 0,
                location.distance_from_last,
                location.geofence_id.name if location.geofence_id else '',
                'Yes' if location.inside_geofence else 'No',
                location.ai_confidence_score or 0,
                'Yes' if location.anomaly_detected else 'No',
                location.status,
                location.battery_level or '',
                location.network_type or ''
            ]
            writer.writerow(row)

        # Create attachment
        filename = f"location_report_{self.date_from}_{self.date_to}.csv"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue().encode('utf-8')),
            'mimetype': 'text/csv'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _create_summary_worksheet(self, workbook, locations):
        """Create summary worksheet"""
        worksheet = workbook.add_worksheet('Summary')

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Write summary data
        row = 0
        worksheet.write(row, 0, 'Location Tracking Report Summary', header_format)
        row += 2

        summary_data = [
            ('Report Period', f"{self.date_from} to {self.date_to}"),
            ('Total Locations', len(locations)),
            ('Unique Employees', len(locations.mapped('employee_id'))),
            ('Total Distance (km)', sum(locations.mapped('distance_from_last'))),
            ('Anomalies Detected', len(locations.filtered('anomaly_detected'))),
            ('Average Accuracy (m)', sum(locations.mapped('accuracy')) / len(locations) if locations else 0)
        ]

        for label, value in summary_data:
            worksheet.write(row, 0, label, header_format)
            worksheet.write(row, 1, value)
            row += 1

    def _create_detailed_worksheet(self, workbook, locations):
        """Create detailed locations worksheet"""
        worksheet = workbook.add_worksheet('Detailed Locations')

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Write headers
        headers = [
            'Employee', 'Timestamp', 'Latitude', 'Longitude', 'Accuracy',
            'Location Type', 'Address', 'Geofence', 'Distance (km)',
            'AI Confidence', 'Anomaly', 'Status'
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Write data
        for row, location in enumerate(locations.sorted('timestamp'), 1):
            data = [
                location.employee_id.name,
                location.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                location.latitude,
                location.longitude,
                location.accuracy or 0,
                location.location_type,
                location.address or '',
                location.geofence_id.name if location.geofence_id else '',
                location.distance_from_last,
                location.ai_confidence_score or 0,
                'Yes' if location.anomaly_detected else 'No',
                location.status
            ]

            for col, value in enumerate(data):
                worksheet.write(row, col, value)

    def _create_analytics_worksheet(self, workbook, locations):
        """Create analytics worksheet"""
        worksheet = workbook.add_worksheet('Analytics')

        # Location type distribution
        type_counts = {}
        for location in locations:
            type_counts[location.location_type] = type_counts.get(location.location_type, 0) + 1

        row = 0
        worksheet.write(row, 0, 'Location Types Distribution', workbook.add_format({'bold': True}))
        row += 1

        for loc_type, count in type_counts.items():
            worksheet.write(row, 0, loc_type)
            worksheet.write(row, 1, count)
            row += 1

    def _create_anomaly_worksheet(self, workbook, anomaly_locations):
        """Create anomaly analysis worksheet"""
        worksheet = workbook.add_worksheet('Anomalies')

        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFE6E6',
            'border': 1
        })

        # Write headers
        headers = [
            'Employee', 'Timestamp', 'Latitude', 'Longitude',
            'Anomaly Details', 'AI Confidence', 'Status'
        ]

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Write anomaly data
        for row, location in enumerate(anomaly_locations.sorted('timestamp'), 1):
            try:
                anomaly_details = json.loads(location.anomaly_details) if location.anomaly_details else []
            except:
                anomaly_details = []

            data = [
                location.employee_id.name,
                location.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                location.latitude,
                location.longitude,
                '; '.join(anomaly_details) if anomaly_details else 'Unknown',
                location.ai_confidence_score or 0,
                location.status
            ]

            for col, value in enumerate(data):
                worksheet.write(row, col, value)
