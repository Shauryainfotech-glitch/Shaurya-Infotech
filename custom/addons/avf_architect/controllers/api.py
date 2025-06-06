# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import json

class ArchitectAPI(http.Controller):
    @http.route('/api/architect/projects', type='http', auth='user', methods=['GET'], csrf=False)
    def get_projects(self, **kw):
        try:
            projects = request.env['architect.project'].search_read(
                domain=[('user_id', '=', request.env.user.id)],
                fields=['id', 'name', 'code', 'partner_id', 'progress', 'stage_id']
            )
            return request.make_response(
                json.dumps({'status': 'success', 'data': projects}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )

    @http.route('/api/architect/projects/<int:project_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_project(self, project_id, **kw):
        try:
            project = request.env['architect.project'].search_read(
                domain=[('id', '=', project_id), ('user_id', '=', request.env.user.id)],
                fields=['id', 'name', 'code', 'partner_id', 'description', 'progress', 'stage_id', 'start_date', 'deadline']
            )
            if not project:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Project not found or access denied'}),
                    headers=[('Content-Type', 'application/json')]
                )
            return request.make_response(
                json.dumps({'status': 'success', 'data': project[0]}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )

    @http.route('/api/architect/drawings/<int:project_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_project_drawings(self, project_id, **kw):
        try:
            drawings = request.env['architect.drawing'].search_read(
                domain=[('project_id', '=', project_id), ('project_id.user_id', '=', request.env.user.id)],
                fields=['id', 'name', 'code', 'drawing_type', 'state', 'create_date']
            )
            return request.make_response(
                json.dumps({'status': 'success', 'data': drawings}),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )
