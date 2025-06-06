from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from odoo.tools import consteq
import base64


class EstimationPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'estimation_count' in counters:
            estimation_count = request.env['mrp.estimation'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id)
            ])
            values['estimation_count'] = estimation_count
        return values

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        values['page_name'] = 'estimation'
        return values

    def _estimation_get_page_view_values(self, estimation, access_token, **kwargs):
        values = {
            'estimation': estimation,
            'user': request.env.user
        }
        return self._get_page_view_values(
            estimation, access_token, values,
            'my_estimations_history', False, **kwargs
        )

    @http.route(['/my/estimations', '/my/estimations/page/<int:page>'], 
                type='http', auth="user", website=True)
    def portal_my_estimations(self, page=1, date_begin=None, date_end=None, 
                             sortby=None, search=None, search_in='content', 
                             groupby='none', filterby='all', **kw):
        
        values = self._prepare_portal_layout_values()
        Estimation = request.env['mrp.estimation']
        
        domain = [('partner_id', '=', request.env.user.partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Estimation Date'), 'order': 'estimation_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'sent': {'label': _('Sent'), 'domain': [('state', '=', 'sent')]},
            'confirmed': {'label': _('Confirmed'), 'domain': [('state', '=', 'confirmed')]},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'name': {'input': 'name', 'label': _('Search in Reference')},
        }

        # Default sort order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Default filter
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # Search
        if search and search_in:
            search_domain = []
            if search_in in ('content', 'all'):
                search_domain = ['|', ('name', 'ilike', search), ('product_id.name', 'ilike', search)]
            if search_in in ('name', 'all'):
                search_domain = [('name', 'ilike', search)]
            domain += search_domain

        # Date filter
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # Count for pager
        estimation_count = Estimation.search_count(domain)

        # Pager
        pager = request.website.pager(
            url="/my/estimations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=estimation_count,
            page=page,
            step=self._items_per_page
        )

        # Get estimations
        estimations = Estimation.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_estimations_history'] = estimations.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'estimations': estimations,
            'page_name': 'estimation',
            'archive_groups': [],
            'default_url': '/my/estimations',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'filterby': filterby,
            'groupby': groupby,
        })
        return request.render("mrp_estimation.portal_my_estimations", values)

    @http.route(['/my/estimation/<int:estimation_id>'], type='http', auth="public", website=True)
    def portal_my_estimation(self, estimation_id=None, access_token=None, **kw):
        try:
            estimation_sudo = self._document_check_access('mrp.estimation', estimation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._estimation_get_page_view_values(estimation_sudo, access_token, **kw)
        return request.render("mrp_estimation.portal_estimation_detail", values)

    @http.route(['/my/estimation/<int:estimation_id>/download'], type='http', auth="public", website=True)
    def portal_estimation_download(self, estimation_id=None, access_token=None, **kw):
        try:
            estimation_sudo = self._document_check_access('mrp.estimation', estimation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # Generate PDF
        report = request.env.ref('mrp_estimation.action_report_estimation')
        pdf_content, content_type = report.sudo()._render_qweb_pdf([estimation_sudo.id])
        
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', f'attachment; filename="Estimation_{estimation_sudo.name}.pdf"')
        ]
        
        return request.make_response(pdf_content, headers=pdfhttpheaders)

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.sudo()
        
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(document_sudo.access_token, access_token):
                raise
                
        return document_sudo 