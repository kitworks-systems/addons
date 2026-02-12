from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestAutocompleteUI(HttpCase):

    def test_model_method_autocomplete_tour(self):
        self.start_tour(
            '/odoo',
            'kw_autocomplete_model_method_tour',
            login='admin'
        )

    def test_domain_search_autocomplete_tour(self):
        self.start_tour(
            '/odoo',
            'kw_autocomplete_domain_search_tour',
            login='admin'
        )
