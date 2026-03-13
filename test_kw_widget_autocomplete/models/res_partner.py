from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    kw_test_city = fields.Char(
        string='KW Test City',
        help='Test field for kw_autocomplete widget',
    )
    kw_test_tag = fields.Char(
        string='KW Test Tag',
        help='Test field for domain search autocomplete',
    )

    @api.model
    def autocomplete_cities_for_partner(self, query, dep_values=None):
        """Autocomplete cities for res.partner."""
        if not query or len(query) < 2:
            return []

        domain = [('name', 'ilike', query)]
        country_id = dep_values.get('country_id') if dep_values else None
        if country_id:
            domain.append(('country_id', '=', country_id))

        cities = self.env['res.city'].search_read(
            domain,
            ['name', 'country_id', 'zipcode'],
            limit=10
        )

        return [{
            'label': c['name'],
            'value': c['name'],
            'data': c,
        } for c in cities]
