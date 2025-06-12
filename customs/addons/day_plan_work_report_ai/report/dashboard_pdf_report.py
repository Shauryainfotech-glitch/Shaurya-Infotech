import logging
import json
from odoo import models, api
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import io
import base64

_logger = logging.getLogger(__name__)


class DashboardPdfReport(models.AbstractModel):
    _name = 'report.day_plan_work_report_ai.dashboard_pdf_report'
    _description = 'Dashboard PDF Report with ReportLab'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Prepare data for PDF report"""
        dashboards = self.env['day.plan.dashboard'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'day.plan.dashboard',
            'docs': dashboards,
            'data': data,
        }

    def _create_pdf_content(self, dashboard):
        """Create PDF content using ReportLab"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )

        elements = []

        # Title
        elements.append(Paragraph('Productivity Dashboard Report', title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Date range
        elements.append(Paragraph(f'Report Period: {dashboard.date_from} to {dashboard.date_to}', styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

        # KPIs Section
        elements.append(Paragraph('Key Performance Indicators', styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))

        kpi_data = [
            ['Metric', 'Value'],
            ['Total Plans', str(dashboard.total_plans)],
            ['Completion Rate', f'{dashboard.completion_rate:.1f}%'],
            ['Average Productivity', f'{dashboard.avg_productivity:.1f}'],
        ]

        kpi_table = Table(kpi_data, colWidths=[3 * inch, 2 * inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(kpi_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Recent Plans Section
        plans = self.env['day.plan'].search([
            ('date', '>=', dashboard.date_from),
            ('date', '<=', dashboard.date_to)
        ], limit=10)

        if plans:
            elements.append(Paragraph('Recent Plans', styles['Heading2']))
            elements.append(Spacer(1, 0.1 * inch))

            plan_data = [['Date', 'Plan Title', 'Completion %']]
            for plan in plans:
                plan_data.append([
                    str(plan.date),
                    plan.name[:30] + ('...' if len(plan.name) > 30 else ''),
                    f'{plan.completion_ratio:.1f}%'
                ])

            plan_table = Table(plan_data, colWidths=[1.5 * inch, 3 * inch, 1.5 * inch])
            plan_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(plan_table)

        # Footer
        elements.append(Spacer(1, 1 * inch))
        elements.append(Paragraph(
            'Generated automatically by Day Plan & Work Report AI System',
            styles['Normal']
        ))

        # Build PDF
        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()

        return pdf_content

    @api.model
    def _render_qweb_pdf(self, docids, data=None):
        """Override to use ReportLab instead of wkhtmltopdf"""
        dashboards = self.env['day.plan.dashboard'].browse(docids)
        if not dashboards:
            return b'', 'pdf'

        dashboard = dashboards[0]
        pdf_content = self._create_pdf_content(dashboard)

        return pdf_content, 'pdf'