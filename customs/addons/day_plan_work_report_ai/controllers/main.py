# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime, timedelta
from odoo import fields

class DayPlanWorkReportController(http.Controller):
    
    @http.route('/day_plan_work_report_ai/report/work_report/<int:day_plan_id>', type='http', auth='user')
    def generate_work_report(self, day_plan_id, **kw):
        """Generate a work report PDF using reportlab directly"""
        # Check if user has access to the report
        if not request.env.user.has_group('day_plan_work_report_ai.group_day_plan_user'):
            return request.render('web.403')
        
        # Get the day plan
        day_plan = request.env['day.plan'].browse(day_plan_id)
        if not day_plan.exists():
            return request.not_found()
            
        # Get employee and date information from the day plan
        employee_id = day_plan.employee_id
        date = day_plan.date
        
        # Get work reports for this day
        work_reports = request.env['day.plan.work.report'].search([
            ('date', '=', date),
            ('employee_id', '=', employee_id.id if employee_id else False)
        ])
        
        # Create PDF with reportlab
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = styles['Heading1']
        title = Paragraph("Work Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.25*inch))
        
        # Date and Employee
        date_text = f"Date: {date.strftime('%Y-%m-%d')}"
        if employee_id:
            date_text += f" - Employee: {employee_id.name}"
        date_para = Paragraph(date_text, styles['Normal'])
        elements.append(date_para)
        elements.append(Spacer(1, 0.25*inch))
        
        # Day Plan Summary
        elements.append(Paragraph("Day Plan", styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Plan status
        status_text = f"Status: {day_plan.state.capitalize()}"
        status = Paragraph(status_text, styles['Normal'])
        elements.append(status)
        
        # Tasks
        if day_plan.task_ids:
            elements.append(Paragraph("Tasks", styles['Heading3']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Create table for tasks
            task_data = [['Task', 'Priority', 'Status', 'Hours']]
            
            for task in day_plan.task_ids:
                task_data.append([
                    task.name,
                    task.priority or 'Normal',
                    task.state.capitalize(),
                    str(task.planned_hours or 0)
                ])
            
            task_table = Table(task_data, colWidths=[3*inch, 1*inch, 1*inch, 0.7*inch])
            task_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (3, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(task_table)
            elements.append(Spacer(1, 0.25*inch))
        
        # Work Reports
        if work_reports:
            elements.append(Paragraph("Work Report Details", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            for report in work_reports:
                if report.summary:
                    summary = Paragraph(f"Summary: {report.summary}", styles['Normal'])
                    elements.append(summary)
                    elements.append(Spacer(1, 0.1*inch))
                
                if report.achievements:
                    achievements = Paragraph(f"Achievements: {report.achievements}", styles['Normal'])
                    elements.append(achievements)
                    elements.append(Spacer(1, 0.1*inch))
                
                if report.challenges:
                    challenges = Paragraph(f"Challenges: {report.challenges}", styles['Normal'])
                    elements.append(challenges)
                    elements.append(Spacer(1, 0.1*inch))
                
                if report.next_day_plan:
                    next_day = Paragraph(f"Next Day Plan: {report.next_day_plan}", styles['Normal'])
                    elements.append(next_day)
                    elements.append(Spacer(1, 0.1*inch))
        
        # AI Analysis if available
        ai_analysis = request.env['day.plan.ai.analysis'].search([
            ('day_plan_id', '=', day_plan_id)
        ], limit=1)
        
        if ai_analysis and ai_analysis.analysis_text:
            elements.append(Paragraph("AI Analysis", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            analysis_text = Paragraph(ai_analysis.analysis_text, styles['Normal'])
            elements.append(analysis_text)
            elements.append(Spacer(1, 0.25*inch))
        
        # Build PDF
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Return the PDF
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_data)),
            ('Content-Disposition', 'attachment; filename="work_report_%s.pdf"' % day_plan_id)
        ]
        
        return request.make_response(pdf_data, headers=pdfhttpheaders)
        
    # Keep the original route for backward compatibility with the wizard
    @http.route('/day_plan/generate_report', type='http', auth='user')
    def generate_report_from_wizard(self, **kw):
        """Generate a work report PDF from the wizard"""
        # Check if user has access to the report
        if not request.env.user.has_group('day_plan_work_report_ai.group_day_plan_user'):
            return request.render('web.403')
        
        # Get active wizard if coming from wizard, or create default parameters
        wizard_id = kw.get('wizard_id')
        if wizard_id:
            wizard = request.env['day.plan.report.generator'].browse(int(wizard_id))
            if not wizard.exists():
                return request.not_found()
            date_from = wizard.date_from
            date_to = wizard.date_to
            employee_id = wizard.employee_id
        else:
            # Default to current user's employee and today
            date_from = date_to = fields.Date.context_today(request.env.user)
            employee_id = request.env.user.employee_id
        
        # Get the work reports and plans for the period
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
        ]
        
        if employee_id:
            domain.append(('employee_id', '=', employee_id.id))
            
        work_reports = request.env['day.plan.work.report'].search(domain)
        day_plans = request.env['day.plan'].search(domain)
        
        # Create PDF with reportlab
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = styles['Heading1']
        title = Paragraph("Work Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.25*inch))
        
        # Period
        period_text = f"Period: {date_from} to {date_to}"
        if employee_id:
            period_text += f" - Employee: {employee_id.name}"
        period = Paragraph(period_text, styles['Normal'])
        elements.append(period)
        elements.append(Spacer(1, 0.25*inch))
        
        # Day Plans Summary
        if day_plans:
            elements.append(Paragraph("Day Plans", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Create table for day plans
            plan_data = [['Date', 'Status', 'Tasks Planned', 'Tasks Completed']]
            
            for plan in day_plans:
                planned = len(plan.task_ids)
                completed = len(plan.task_ids.filtered(lambda t: t.state == 'done'))
                plan_data.append([
                    plan.date.strftime('%Y-%m-%d'),
                    plan.state.capitalize(),
                    str(planned),
                    str(completed)
                ])
            
            plan_table = Table(plan_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1.5*inch])
            plan_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(plan_table)
            elements.append(Spacer(1, 0.25*inch))
        
        # Work Reports
        if work_reports:
            elements.append(Paragraph("Work Reports", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            for report in work_reports:
                report_date = Paragraph(f"Date: {report.date.strftime('%Y-%m-%d')}", styles['Heading3'])
                elements.append(report_date)
                
                if report.summary:
                    summary = Paragraph(f"Summary: {report.summary}", styles['Normal'])
                    elements.append(summary)
                
                if report.achievements:
                    achievements = Paragraph(f"Achievements: {report.achievements}", styles['Normal'])
                    elements.append(achievements)
                
                if report.challenges:
                    challenges = Paragraph(f"Challenges: {report.challenges}", styles['Normal'])
                    elements.append(challenges)
                
                if report.next_day_plan:
                    next_day = Paragraph(f"Next Day Plan: {report.next_day_plan}", styles['Normal'])
                    elements.append(next_day)
                
                elements.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(elements)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Return the PDF
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_data)),
            ('Content-Disposition', 'attachment; filename="work_report.pdf"')
        ]
        
        return request.make_response(pdf_data, headers=pdfhttpheaders)
