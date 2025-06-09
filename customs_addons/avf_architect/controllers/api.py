# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError, ValidationError
import json
import base64
from datetime import datetime, timedelta


class ArchitectAPIController(http.Controller):

    @http.route('/api/architect/projects', type='json', auth='user', methods=['GET'])
    def api_get_projects(self, **kwargs):
        """API endpoint to get user's projects"""
        try:
            projects = request.env['architect.project'].search([
                ('user_id', '=', request.env.user.id)
            ])

            result = []
            for project in projects:
                result.append({
                    'id': project.id,
                    'name': project.name,
                    'code': project.code,
                    'state': project.state,
                    'progress': project.progress,
                    'client': project.partner_id.name,
                    'deadline': project.deadline.isoformat() if project.deadline else None,
                    'budget': project.budget,
                    'estimated_cost': project.estimated_cost,
                })

            return {
                'status': 'success',
                'data': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/architect/project/<int:project_id>', type='json', auth='user', methods=['GET'])
    def api_get_project_details(self, project_id, **kwargs):
        """API endpoint to get project details"""
        try:
            project = request.env['architect.project'].browse(project_id)
            if not project.exists():
                return {
                    'status': 'error',
                    'message': 'Project not found'
                }

            # Check access rights
            if project.user_id.id != request.env.user.id:
                return {
                    'status': 'error',
                    'message': 'Access denied'
                }

            result = {
                'id': project.id,
                'name': project.name,
                'code': project.code,
                'description': project.description,
                'state': project.state,
                'progress': project.progress,
                'client': {
                    'id': project.partner_id.id,
                    'name': project.partner_id.name,
                },
                'project_type': project.project_type,
                'category': project.category,
                'location': project.location,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'budget': project.budget,
                'estimated_cost': project.estimated_cost,
                'actual_cost': project.actual_cost,
                'task_count': project.task_count,
                'drawing_count': project.drawing_count,
                'compliance_count': project.compliance_count,
            }

            return {
                'status': 'success',
                'data': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/architect/compliance', type='json', auth='user', methods=['GET'])
    def api_get_compliance_items(self, project_id=None, **kwargs):
        """API endpoint to get compliance items"""
        try:
            domain = []
            if project_id:
                domain.append(('project_id', '=', project_id))

            # Filter by user's projects
            user_projects = request.env['architect.project'].search([
                ('user_id', '=', request.env.user.id)
            ])
            domain.append(('project_id', 'in', user_projects.ids))

            compliance_items = request.env['architect.compliance'].search(domain)

            result = []
            for item in compliance_items:
                result.append({
                    'id': item.id,
                    'name': item.name,
                    'project': item.project_id.name,
                    'category': item.category,
                    'state': item.state,
                    'priority': item.priority,
                    'deadline': item.deadline.isoformat() if item.deadline else None,
                    'progress': item.progress,
                    'days_to_deadline': item.days_to_deadline,
                    'is_overdue': item.is_overdue,
                })

            return {
                'status': 'success',
                'data': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/architect/drawings', type='json', auth='user', methods=['GET'])
    def api_get_drawings(self, project_id=None, **kwargs):
        """API endpoint to get drawings"""
        try:
            domain = []
            if project_id:
                domain.append(('project_id', '=', project_id))

            # Filter by user's projects
            user_projects = request.env['architect.project'].search([
                ('user_id', '=', request.env.user.id)
            ])
            domain.append(('project_id', 'in', user_projects.ids))

            drawings = request.env['architect.drawing'].search(domain)

            result = []
            for drawing in drawings:
                result.append({
                    'id': drawing.id,
                    'name': drawing.name,
                    'code': drawing.code,
                    'project': drawing.project_id.name,
                    'drawing_type': drawing.drawing_type,
                    'state': drawing.state,
                    'scale': drawing.scale,
                    'revision': drawing.revision,
                    'designer': drawing.designer_id.name,
                    'file_name': drawing.file_name,
                })

            return {
                'status': 'success',
                'data': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/architect/ai/chat', type='json', auth='user', methods=['POST'])
    def api_ai_chat(self, session_id=None, message=None, **kwargs):
        """API endpoint for AI chat"""
        try:
            if not message:
                return {
                    'status': 'error',
                    'message': 'Message is required'
                }

            # Get or create AI session
            if session_id:
                ai_session = request.env['architect.ai.assistant'].browse(session_id)
                if not ai_session.exists() or ai_session.user_id.id != request.env.user.id:
                    return {
                        'status': 'error',
                        'message': 'Session not found or access denied'
                    }
            else:
                ai_session = request.env['architect.ai.assistant'].create({
                    'name': f'API Session {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                    'user_id': request.env.user.id,
                    'session_type': 'general'
                })

            # Send message and get response
            response_msg = ai_session.send_message(message)

            return {
                'status': 'success',
                'data': {
                    'session_id': ai_session.id,
                    'response': response_msg.message,
                    'timestamp': response_msg.timestamp.isoformat()
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/architect/dashboard/stats', type='json', auth='user', methods=['GET'])
    def api_dashboard_stats(self, **kwargs):
        """API endpoint for dashboard statistics"""
        try:
            user = request.env.user

            # Project stats
            projects = request.env['architect.project'].search([
                ('user_id', '=', user.id)
            ])

            project_stats = {
                'total': len(projects),
                'active': len(projects.filtered(lambda p: p.state in ['confirmed', 'in_progress'])),
                'completed': len(projects.filtered(lambda p: p.state == 'completed')),
                'overdue': len(projects.filtered(
                    lambda p: p.deadline and p.deadline < datetime.now().date() and p.state not in ['completed',
                                                                                                    'cancelled']))
            }

            # Compliance stats
            compliance_items = request.env['architect.compliance'].search([
                ('project_id', 'in', projects.ids)
            ])

            compliance_stats = {
                'total': len(compliance_items),
                'pending': len(compliance_items.filtered(lambda c: c.state == 'pending')),
                'approved': len(compliance_items.filtered(lambda c: c.state == 'approved')),
                'overdue': len(compliance_items.filtered(lambda c: c.is_overdue))
            }

            # Drawing stats
            drawings = request.env['architect.drawing'].search([
                ('project_id', 'in', projects.ids)
            ])

            drawing_stats = {
                'total': len(drawings),
                'draft': len(drawings.filtered(lambda d: d.state == 'draft')),
                'approved': len(drawings.filtered(lambda d: d.state == 'approved')),
                'under_review': len(drawings.filtered(lambda d: d.state == 'review'))
            }

            return {
                'status': 'success',
                'data': {
                    'projects': project_stats,
                    'compliance': compliance_stats,
                    'drawings': drawing_stats
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/architect/export/project/<int:project_id>', type='http', auth='user', methods=['GET'])
    def api_export_project_data(self, project_id, format='json', **kwargs):
        """API endpoint to export project data"""
        try:
            project = request.env['architect.project'].browse(project_id)
            if not project.exists():
                return request.not_found()

            # Check access rights
            if project.user_id.id != request.env.user.id:
                return request.not_found()

            # Prepare data
            data = {
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'code': project.code,
                    'description': project.description,
                    'state': project.state,
                    'progress': project.progress,
                },
                'drawings': [],
                'compliance': [],
                'documents': []
            }

            # Add drawings
            for drawing in project.drawing_ids:
                data['drawings'].append({
                    'name': drawing.name,
                    'code': drawing.code,
                    'type': drawing.drawing_type,
                    'state': drawing.state,
                    'revision': drawing.revision
                })

            # Add compliance items
            compliance_items = request.env['architect.compliance'].search([
                ('project_id', '=', project.id)
            ])
            for item in compliance_items:
                data['compliance'].append({
                    'name': item.name,
                    'category': item.category,
                    'state': item.state,
                    'deadline': item.deadline.isoformat() if item.deadline else None
                })

            if format == 'json':
                return request.make_response(
                    json.dumps(data, indent=2, default=str),
                    headers=[
                        ('Content-Type', 'application/json'),
                        ('Content-Disposition', f'attachment; filename=project_{project.code}.json')
                    ]
                )

            return request.not_found()

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )