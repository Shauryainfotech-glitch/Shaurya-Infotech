# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import base64
from datetime import datetime


class ArchitectPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        if 'project_count' in counters:
            project_count = request.env['architect.project'].search_count([
                ('partner_id', '=', partner.id)
            ])
            values['project_count'] = project_count

        return values

    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content',
                           **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ArchitectProject = request.env['architect.project']

        domain = [('partner_id', '=', partner.id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'deadline': {'label': _('Deadline'), 'order': 'deadline'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'name': {'input': 'name', 'label': _('Search in Name')},
            'code': {'input': 'code', 'label': _('Search in Code')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = ['|', ('name', 'ilike', search), ('description', 'ilike', search)]
            if search_in in ('name', 'all'):
                search_domain = ['|'] + search_domain + [('name', 'ilike', search)]
            if search_in in ('code', 'all'):
                search_domain = ['|'] + search_domain + [('code', 'ilike', search)]
            domain += search_domain

        # count for pager
        project_count = ArchitectProject.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/projects",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=project_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        projects = ArchitectProject.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_projects_history'] = projects.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'projects': projects,
            'page_name': 'project',
            'archive_groups': [],
            'default_url': '/my/projects',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
        })
        return request.render("avf_architect.portal_my_projects", values)

    @http.route(['/my/project/<int:project_id>'], type='http', auth="public", website=True)
    def portal_my_project(self, project_id=None, access_token=None, **kw):
        try:
            project_sudo = self._document_check_access('architect.project', project_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'project': project_sudo,
            'page_name': 'project',
        }
        return request.render("avf_architect.portal_my_project", values)

    @http.route(['/my/drawings', '/my/drawings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_drawings(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        domain = [
            ('project_id.partner_id', '=', partner.id),
            ('website_published', '=', True)
        ]

        # count for pager
        drawing_count = request.env['architect.drawing'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/drawings",
            total=drawing_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager
        drawings = request.env['architect.drawing'].search(
            domain,
            limit=self._items_per_page,
            offset=pager['offset'],
            order='create_date desc'
        )

        values.update({
            'drawings': drawings,
            'page_name': 'drawing',
            'pager': pager,
        })
        return request.render("avf_architect.portal_my_drawings", values)

    @http.route(['/my/drawing/<int:drawing_id>'], type='http', auth="public", website=True)
    def portal_my_drawing(self, drawing_id=None, access_token=None, **kw):
        try:
            drawing_sudo = self._document_check_access('architect.drawing', drawing_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'drawing': drawing_sudo,
            'page_name': 'drawing',
        }
        return request.render("avf_architect.portal_my_drawing", values)

    @http.route(['/my/documents', '/my/documents/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_documents(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        domain = [
            ('project_id.partner_id', '=', partner.id),
            ('portal_visible', '=', True)
        ]

        # count for pager
        document_count = request.env['architect.document'].search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/documents",
            total=document_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager
        documents = request.env['architect.document'].search(
            domain,
            limit=self._items_per_page,
            offset=pager['offset'],
            order='create_date desc'
        )

        values.update({
            'documents': documents,
            'page_name': 'document',
            'pager': pager,
        })
        return request.render("avf_architect.portal_my_documents", values)

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.sudo()

        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if access_token and document_sudo.access_token and access_token == document_sudo.access_token:
                return document_sudo
            else:
                raise
        return document

    @http.route(['/my/compliance'], type='http', auth="user", website=True)
    def portal_my_compliance(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        compliance_items = request.env['architect.compliance'].search([
            ('project_id.partner_id', '=', partner.id)
        ])

        values.update({
            'compliance_items': compliance_items,
            'page_name': 'compliance',
        })
        return request.render("avf_architect.portal_my_compliance", values)