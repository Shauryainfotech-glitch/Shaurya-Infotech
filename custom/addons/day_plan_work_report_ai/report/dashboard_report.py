from odoo import models, fields, api
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import LineChart
from reportlab.graphics.charts.spider import SpiderChart
import io
import json
import base64
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class DashboardReportPDF(models.AbstractModel):
    _name = 'report.day_plan_work_report_ai.report_dashboard_pdf'
    _description = 'Dashboard PDF Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Prepare data for report"""
        if data and data.get('dashboard_id'):
            dashboard_id = data.get('dashboard_id')
        else:
            dashboard_id = docids[0]
        
        dashboard = self.env['day.plan.dashboard'].browse(dashboard_id)
        return {
            'doc_ids': docids,
            'doc_model': 'day.plan.dashboard',
            'docs': dashboard,
            'data': data,
        }
    
    def _render_qweb_pdf(self, docids, data=None):
        """Override to use reportlab instead of wkhtmltopdf"""
        if not data:
            data = {}
        
        # Get dashboard data
        if data and data.get('dashboard_id'):
            dashboard_id = data.get('dashboard_id')
        else:
            dashboard_id = docids[0]
        
        dashboard = self.env['day.plan.dashboard'].browse(dashboard_id)
        
        # Generate PDF using reportlab
        return self._generate_dashboard_pdf(dashboard), 'pdf'
    
    def _generate_dashboard_pdf(self, dashboard):
        """Generate dashboard PDF using reportlab"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Custom styles
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.darkblue
        )
        
        # Content elements
        elements = []
        
        # Title and date
        elements.append(Paragraph(f"Productivity Dashboard Report", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
        elements.append(Spacer(1, 20))
        
        # Summary metrics
        elements.append(Paragraph("Summary Metrics", subtitle_style))
        summary_data = [
            ["Total Plans", "Plans Today", "Completed Plans", "Pending Tasks"],
            [str(dashboard.total_plans), str(dashboard.plans_today), 
             str(dashboard.completed_plans), str(dashboard.pending_tasks)]
        ]
        summary_table = Table(summary_data, colWidths=[100, 100, 100, 100])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (3, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Productivity metrics
        elements.append(Paragraph("Productivity Metrics", subtitle_style))
        productivity_data = [
            ["Productivity Score", "Efficiency Rating", "Wellbeing Score"],
            [f"{dashboard.productivity_score:.1f}%", f"{dashboard.efficiency_rating:.1f}%", 
             f"{dashboard.wellbeing_assessment:.1f}%"]
        ]
        productivity_table = Table(productivity_data, colWidths=[133, 133, 133])
        productivity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.darkgreen),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (2, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(productivity_table)
        elements.append(Spacer(1, 20))
        
        # Task Statistics
        elements.append(Paragraph("Task Statistics", subtitle_style))
        task_data = [
            ["Tasks Due Today", "Overdue Tasks", "Attention Items", "Completion Rate"],
            [str(dashboard.tasks_due_today), str(dashboard.overdue_tasks), 
             str(dashboard.attention_items), f"{dashboard.completion_rate:.1f}%"]
        ]
        task_table = Table(task_data, colWidths=[100, 100, 100, 100])
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), colors.lightpink),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.darkred),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (3, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(task_table)
        elements.append(Spacer(1, 20))
        
        # Bar Chart - Tasks Completed vs Planned
        elements.append(Paragraph("Weekly Task Completion", subtitle_style))
        try:
            chart_data = json.loads(dashboard.chart_data.replace("'", "\""))
            drawing = Drawing(400, 200)
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 125
            bc.width = 300
            bc.data = [
                chart_data['datasets'][0]['data'],  # Completed Tasks
                chart_data['datasets'][1]['data']   # Planned Tasks
            ]
            bc.strokeColor = colors.black
            bc.valueAxis.valueMin = 0
            bc.valueAxis.valueMax = max(max(bc.data[0]), max(bc.data[1])) + 2
            bc.valueAxis.valueStep = 1
            bc.categoryAxis.labels.boxAnchor = 'ne'
            bc.categoryAxis.labels.dx = 8
            bc.categoryAxis.labels.dy = -2
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.categoryNames = chart_data['labels']
            bc.bars[0].fillColor = colors.lightblue
            bc.bars[1].fillColor = colors.lightgreen
            drawing.add(bc)
            elements.append(drawing)
            
            # Add legend
            legend_data = [
                ["Blue: Completed Tasks", "Green: Planned Tasks"]
            ]
            legend_table = Table(legend_data)
            legend_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Oblique'),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.lightblue),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.lightgreen),
            ]))
            elements.append(legend_table)
        except Exception as e:
            _logger.error("Error rendering bar chart: %s", str(e))
            elements.append(Paragraph("Error rendering bar chart: " + str(e), normal_style))
        
        elements.append(Spacer(1, 20))
        
        # Pie Chart - Task Distribution
        elements.append(Paragraph("Task Distribution", subtitle_style))
        try:
            pie_data = json.loads(dashboard.pie_chart_data.replace("'", "\""))
            drawing = Drawing(400, 200)
            pc = Pie()
            pc.x = 150
            pc.y = 50
            pc.width = 100
            pc.height = 100
            pc.data = pie_data['datasets'][0]['data']
            pc.labels = pie_data['labels']
            pc.slices.strokeWidth = 0.5
            
            # Set slice colors
            colors_list = [colors.lightblue, colors.lightgreen, colors.lightcyan, colors.lightgrey]
            for i, color in enumerate(colors_list):
                pc.slices[i].fillColor = color
            
            drawing.add(pc)
            elements.append(drawing)
        except Exception as e:
            _logger.error("Error rendering pie chart: %s", str(e))
            elements.append(Paragraph("Error rendering pie chart: " + str(e), normal_style))
        
        elements.append(Spacer(1, 20))
        
        # Line Chart - Productivity Trend
        elements.append(Paragraph("Productivity Trend", subtitle_style))
        try:
            line_data = json.loads(dashboard.line_chart_data.replace("'", "\""))
            drawing = Drawing(400, 200)
            lc = LineChart()
            lc.x = 50
            lc.y = 50
            lc.height = 125
            lc.width = 300
            lc.data = [line_data['datasets'][0]['data']]
            lc.lines[0].strokeColor = colors.blue
            lc.lines[0].symbol = None
            lc.fillColor = colors.lightblue
            lc.categoryAxis.categoryNames = line_data['labels']
            lc.categoryAxis.labels.boxAnchor = 'n'
            lc.valueAxis.valueMin = 0
            lc.valueAxis.valueMax = 100
            lc.valueAxis.valueStep = 10
            drawing.add(lc)
            elements.append(drawing)
        except Exception as e:
            _logger.error("Error rendering line chart: %s", str(e))
            elements.append(Paragraph("Error rendering line chart: " + str(e), normal_style))
            
        elements.append(Spacer(1, 20))
        
        # Add footer
        elements.append(Paragraph("Generated by Day Plan Work Report AI", normal_style))
        
        # Build PDF document
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
