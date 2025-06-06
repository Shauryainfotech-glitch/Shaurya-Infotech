# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from odoo.tools import consteq
from collections import OrderedDict

class ArchitectPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'project_count' in counters:
            project_count = request.env['architect.project'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
            ])
            values['project_count'] = project_count

        if 'drawing_count' in counters:
            drawing_count = request.env['architect.drawing'].search_count([
                ('project_id.partner_id', '=', request.env.user.partner_id.id),
                ('website_published', '=', True),
            ])
            values['drawing_count'] = drawing_count

        if 'document_count' in counters:
            document_count = request.env['architect.document'].search_count([
                ('project_id.partner_id', '=', request.env.user.partner_id.id),
                ('portal_visible', '=', True),
            ])
            values['document_count'] = document_count

        return values

    # Projects
    @http.route(['/my/projects', '/my/projects/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Project = request.env['architect.project']

        domain = [
            ('partner_id', '=', request.env.user.partner_id.id),
        ]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
        }
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        # pager
        project_count = Project.search_count(domain)
        pager = request.website.pager(
            url="/my/projects",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=project_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        projects = Project.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'projects': projects,
            'page_name': 'project',
            'default_url': '/my/projects',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("avf_architect.portal_my_projects", values)

    @http.route(['/my/project/<int:project_id>'], type='http', auth="user", website=True)
    def portal_my_project(self, project_id=None, **kw):
        try:
            project_sudo = self._document_check_access('architect.project', project_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._prepare_portal_layout_values()
        values.update({
            'project': project_sudo,
            'page_name': 'project',
        })
        return request.render("avf_architect.portal_my_project", values)

    # Drawings
    @http.route(['/my/drawings', '/my/drawings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_drawings(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Drawing = request.env['architect.drawing']

        domain = [
            ('project_id.partner_id', '=', request.env.user.partner_id.id),
            ('website_published', '=', True),
        ]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'project': {'label': _('Project'), 'order': 'project_id'},
        }
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        # pager
        drawing_count = Drawing.search_count(domain)
        pager = request.website.pager(
            url="/my/drawings",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=drawing_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        drawings = Drawing.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'drawings': drawings,
            'page_name': 'drawings',
            'default_url': '/my/drawings',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("avf_architect.portal_my_drawings", values)

    # Documents
    @http.route(['/my/documents', '/my/documents/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_documents(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Document = request.env['architect.document']

        domain = [
            ('project_id.partner_id', '=', request.env.user.partner_id.id),
            ('portal_visible', '=', True),
        ]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
            'project': {'label': _('Project'), 'order': 'project_id'},
        }
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        # pager
        document_count = Document.search_count(domain)
        pager = request.website.pager(
            url="/my/documents",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=document_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        documents = Document.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'documents': documents,
            'page_name': 'documents',
            'default_url': '/my/documents',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("avf_architect.portal_my_documents", values)
