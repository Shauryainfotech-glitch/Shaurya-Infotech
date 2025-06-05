from odoo import models, fields, api
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import base64
import io
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class DashboardPdfReport(models.AbstractModel):
    _name = 'report.day_plan_work_report_ai.dashboard_pdf_report'
    _description = 'Dashboard PDF Report (Direct ReportLab)'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Prepare data for the report"""
        dashboard = self.env['day.plan.dashboard'].browse(docids[0])
        return {
            'doc_ids': docids,
            'doc_model': 'day.plan.dashboard',
            'docs': dashboard,
            'data': data,
        }
    
    def _create_dashboard_pdf(self, dashboard):
        """Generate PDF using reportlab directly"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=72)
        
        # Styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Title', 
                                 parent=styles['Heading1'], 
                                 alignment=TA_CENTER,
                                 fontSize=16))
        styles.add(ParagraphStyle(name='Subtitle', 
                                 parent=styles['Heading2'], 
                                 fontSize=14))
        styles.add(ParagraphStyle(name='Center', 
                                 parent=styles['Normal'], 
                                 alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='Right', 
                                 parent=styles['Normal'], 
                                 alignment=TA_RIGHT))
        
        # Content elements
        elements = []
        
        # Title
        elements.append(Paragraph("Productivity Dashboard Report", styles['Title']))
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Right']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Summary Metrics
        elements.append(Paragraph("Summary Metrics", styles['Subtitle']))
        
        summary_data = [
            ["Total Plans", "Plans Today", "Completed Plans", "Pending Tasks"],
            [str(dashboard.total_plans), str(dashboard.plans_today), 
             str(dashboard.completed_plans), str(dashboard.pending_tasks)]
        ]
        
        summary_table = Table(summary_data, colWidths=[doc.width/4.0]*4)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Productivity Metrics
        elements.append(Paragraph("Productivity Metrics", styles['Subtitle']))
        
        productivity_data = [
            ["Productivity Score", "Completion Rate", "Avg Productivity"],
            [f"{dashboard.productivity_score:.1f}/100", f"{dashboard.completion_rate:.1f}%", 
             f"{dashboard.avg_productivity:.1f}/100"]
        ]
        
        productivity_table = Table(productivity_data, colWidths=[doc.width/3.0]*3)
        productivity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(productivity_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Task Statistics
        elements.append(Paragraph("Task Statistics", styles['Subtitle']))
        
        task_data = [
            ["Tasks Due Today", "Overdue Tasks", "Attention Items"],
            [str(dashboard.tasks_due_today), str(dashboard.overdue_tasks), 
             str(dashboard.attention_items)]
        ]
        
        task_table = Table(task_data, colWidths=[doc.width/3.0]*3)
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.salmon),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(task_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Data Analyses
        elements.append(Paragraph("Data Analysis", styles['Subtitle']))
        elements.append(Spacer(1, 0.1*inch))
        
        # We could add charts here if we had chart libraries for reportlab
        # For now, just show the data in text format
        if dashboard.chart_data:
            try:
                chart_data = json.loads(dashboard.chart_data)
                elements.append(Paragraph("Weekly Activity", styles['Subtitle']))
                
                # Extract data for weekly activity
                weekly_headers = ["Day"] + [dataset.get('label', f"Series {i+1}") 
                                          for i, dataset in enumerate(chart_data.get('datasets', []))]
                
                weekly_rows = []
                weekly_rows.append(weekly_headers)
                
                for i, day in enumerate(chart_data.get('labels', [])):
                    row = [day]
                    for dataset in chart_data.get('datasets', []):
                        data = dataset.get('data', [])
                        if i < len(data):
                            row.append(str(data[i]))
                        else:
                            row.append("N/A")
                    weekly_rows.append(row)
                
                weekly_table = Table(weekly_rows, colWidths=[doc.width/(len(weekly_headers))] * len(weekly_headers))
                weekly_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(weekly_table)
                elements.append(Spacer(1, 0.25*inch))
            except Exception as e:
                _logger.error(f"Error processing chart data: {e}")
        
        # Task Distribution (from pie chart)
        if dashboard.pie_chart_data:
            try:
                pie_data = json.loads(dashboard.pie_chart_data)
                elements.append(Paragraph("Task Distribution", styles['Subtitle']))
                
                pie_rows = []
                pie_rows.append(["Status", "Count"])
                
                labels = pie_data.get('labels', [])
                datasets = pie_data.get('datasets', [{}])
                data = datasets[0].get('data', []) if datasets else []
                
                for i, label in enumerate(labels):
                    if i < len(data):
                        pie_rows.append([label, str(data[i])])
                
                pie_table = Table(pie_rows, colWidths=[doc.width*0.7, doc.width*0.3])
                pie_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(pie_table)
                elements.append(Spacer(1, 0.25*inch))
            except Exception as e:
                _logger.error(f"Error processing pie chart data: {e}")
        
        # Footer
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph("This report was generated automatically by the Day Plan & Work Report AI system.", styles['Center']))
        
        # Build the PDF document
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    @api.model
    def _get_report_from_name(self, report_name):
        """Override to return our custom report handler"""
        if report_name == 'day_plan_work_report_ai.dashboard_pdf_report':
            return self
        return super()._get_report_from_name(report_name)
    
    @api.model
    def render_reportlab_pdf(self, docids, data=None):
        """Generate the PDF report using reportlab"""
        # Get the dashboard record
        dashboards = self.env['day.plan.dashboard'].browse(docids)
        if not dashboards:
            return None, 'pdf'
        
        dashboard = dashboards[0]
        
        # Generate the PDF
        pdf_content = self._create_dashboard_pdf(dashboard)
        
        return pdf_content, 'pdf'
