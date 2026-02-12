from odoo import http
from odoo.http import request


class AutocompleteMockController(http.Controller):

    @http.route('/test_autocomplete/products', type='json', auth='public')
    def autocomplete_products(self, query='', **kwargs):
        if not query or len(query) < 2:
            return []

        products = request.env['product.product'].sudo().search_read(
            [('name', 'ilike', query)],
            ['name', 'default_code', 'list_price'],
            limit=10
        )

        return [{
            'label': "{} [{}]".format(
                p['name'],
                p.get('default_code') or 'N/A'
            ),
            'value': p['name'],
            'data': p,
        } for p in products]

    @http.route('/test_autocomplete/countries', type='json', auth='public')
    def autocomplete_countries(self, query='', **kwargs):
        if not query:
            return []

        countries = request.env['res.country'].sudo().search_read(
            [('name', 'ilike', query)],
            ['name', 'code'],
            limit=10
        )

        return [{
            'label': "{} ({})".format(c['name'], c['code']),
            'value': c['name'],
            'data': c,
        } for c in countries]
