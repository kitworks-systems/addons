from odoo import models, fields, api


class KwAutocompleteTest(models.Model):
    _name = 'kw.autocomplete.test'
    _description = 'Autocomplete Test Model'
    _inherit = ['kw.autocomplete.mixin']

    name = fields.Char(string='Name', required=True)

    country_id = fields.Many2one('res.country', string='Country')
    partner_id = fields.Many2one('res.partner', string='Partner')

    city_model_method = fields.Char(
        string='City (Model Method)',
        help='Test autocomplete with model method source',
    )
    partner_domain = fields.Char(
        string='Partner (Domain Search)',
        help='Test autocomplete with domain search source',
    )
    country_domain = fields.Char(
        string='Country (Domain Search)',
        help='Test autocomplete with domain search source',
    )
    product_json = fields.Char(
        string='Product (JSON Endpoint)',
        help='Test autocomplete with JSON endpoint source',
    )

    selected_partner_email = fields.Char(
        string='Selected Partner Email',
        help='Auto-filled from partner selection',
    )
    selected_partner_phone = fields.Char(
        string='Selected Partner Phone',
        help='Auto-filled from partner selection',
    )

    @api.model
    def autocomplete_cities(self, query, dep_values=None):
        """Autocomplete method - searches countries as demo."""
        if not query or len(query) < 2:
            return []

        domain = [('name', 'ilike', query)]

        countries = self.env['res.country'].search_read(
            domain,
            ['name', 'code'],
            limit=10
        )

        return [{
            'label': '{} ({})'.format(c['name'], c['code']),
            'value': c['name'],
            'data': c,
        } for c in countries]

    @api.model
    def autocomplete_partners(self, query, dep_values=None):
        """Autocomplete method for partners."""
        if not query or len(query) < 2:
            return []

        domain = [
            '|',
            ('name', 'ilike', query),
            ('email', 'ilike', query),
        ]

        partners = self.env['res.partner'].search_read(
            domain,
            ['name', 'email', 'phone', 'city'],
            limit=10
        )

        return [{
            'label': '{} <{}>'.format(
                p['name'],
                p.get('email') or 'no email'
            ),
            'value': p['name'],
            'data': p,
        } for p in partners]

    @api.model
    def autocomplete_countries(self, query, dep_values=None):
        """Autocomplete method for countries."""
        if not query or len(query) < 1:
            return []

        countries = self.env['res.country'].search_read(
            [('name', 'ilike', query)],
            ['name', 'code'],
            limit=10
        )

        return [{
            'label': '{} ({})'.format(c['name'], c['code']),
            'value': c['name'],
            'data': c,
        } for c in countries]

    @api.model
    def apply_partner_selection(self, record_id, data):
        """Callback method when partner is selected."""
        return {
            'selected_partner_email': data.get('email', ''),
            'selected_partner_phone': data.get('phone', ''),
        }
