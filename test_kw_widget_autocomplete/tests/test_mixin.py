from odoo.tests.common import TransactionCase


class TestAutocompleteMixin(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_model = cls.env['kw.autocomplete.test']
        cls.ukraine = cls.env.ref('base.ua')
        cls.usa = cls.env.ref('base.us')
        cls.germany = cls.env.ref('base.de')

        cls.partner1 = cls.env['res.partner'].create({
            'name': 'Test Partner One',
            'email': 'partner1@test.com',
            'phone': '+380991234567',
        })
        cls.partner2 = cls.env['res.partner'].create({
            'name': 'Test Partner Two',
            'email': 'partner2@test.com',
        })

    def test_autocomplete_cities_returns_list(self):
        results = self.test_model.autocomplete_cities(query='Ukr')
        self.assertIsInstance(results, list)

    def test_autocomplete_cities_finds_ukraine(self):
        results = self.test_model.autocomplete_cities(query='Ukr')
        self.assertTrue(any('Ukr' in r['label'] for r in results))

    def test_autocomplete_cities_min_chars(self):
        results = self.test_model.autocomplete_cities(query='U')
        self.assertEqual(results, [])

        results = self.test_model.autocomplete_cities(query='Uk')
        self.assertIsInstance(results, list)

    def test_autocomplete_cities_result_format(self):
        results = self.test_model.autocomplete_cities(query='Ukraine')
        if results:
            item = results[0]
            self.assertIn('label', item)
            self.assertIn('value', item)
            self.assertIn('data', item)

    def test_autocomplete_partners_returns_list(self):
        results = self.test_model.autocomplete_partners(query='Test Partner')
        self.assertIsInstance(results, list)

    def test_autocomplete_partners_finds_created(self):
        results = self.test_model.autocomplete_partners(query='Test Partner')
        self.assertTrue(len(results) >= 2)
        labels = [r['label'] for r in results]
        self.assertTrue(any('partner1@test.com' in lbl for lbl in labels))

    def test_autocomplete_partners_search_by_email(self):
        results = self.test_model.autocomplete_partners(query='partner1@test')
        self.assertTrue(results)
        self.assertIn('Test Partner One', results[0]['value'])

    def test_autocomplete_partners_min_chars(self):
        results = self.test_model.autocomplete_partners(query='T')
        self.assertEqual(results, [])

    def test_autocomplete_countries_returns_list(self):
        results = self.test_model.autocomplete_countries(query='Ger')
        self.assertIsInstance(results, list)
        self.assertTrue(any('Germany' in r['label'] for r in results))

    def test_autocomplete_countries_min_chars(self):
        results = self.test_model.autocomplete_countries(query='')
        self.assertEqual(results, [])

    def test_apply_partner_selection_callback(self):
        data = {
            'id': self.partner1.id,
            'name': self.partner1.name,
            'email': self.partner1.email,
            'phone': self.partner1.phone,
        }
        result = self.test_model.apply_partner_selection(
            record_id=False,
            data=data
        )
        self.assertEqual(result['selected_partner_email'], 'partner1@test.com')
        self.assertEqual(result['selected_partner_phone'], '+380991234567')

    def test_apply_partner_selection_empty_fields(self):
        data = {'id': 1, 'name': 'Test'}
        result = self.test_model.apply_partner_selection(
            record_id=False,
            data=data
        )
        self.assertEqual(result['selected_partner_email'], '')
        self.assertEqual(result['selected_partner_phone'], '')


class TestAutocompleteMixinSearch(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_model = cls.env['kw.autocomplete.test']
        cls.test_record = cls.test_model.create({
            'name': 'Test Search Record Alpha',
        })
        cls.test_record2 = cls.test_model.create({
            'name': 'Test Search Record Beta',
        })

    def test_kw_autocomplete_search_basic(self):
        results = self.test_model.kw_autocomplete_search(
            query='Alpha',
            field_name='name',
            domain=[],
            limit=10,
        )
        self.assertTrue(any('Alpha' in r['label'] for r in results))

    def test_kw_autocomplete_search_with_label_template(self):
        results = self.test_model.kw_autocomplete_search(
            query='Alpha',
            field_name='name',
            display_fields=['name', 'id'],
            label_template='{name} (ID:{id})',
        )
        if results:
            self.assertIn('(ID:', results[0]['label'])

    def test_kw_autocomplete_search_limit(self):
        results = self.test_model.kw_autocomplete_search(
            query='Test',
            field_name='name',
            limit=1,
        )
        self.assertLessEqual(len(results), 1)

    def test_kw_autocomplete_search_no_results(self):
        results = self.test_model.kw_autocomplete_search(
            query='NonExistentRecordXYZ',
            field_name='name',
        )
        self.assertEqual(results, [])


class TestAutocompleteProxyRest(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mixin = cls.env['kw.autocomplete.mixin']

    def test_proxy_rest_no_credential_model(self):
        config = {'endpoint': '/api/test'}
        results = self.mixin.kw_autocomplete_proxy_rest(
            query='test',
            config=config
        )
        self.assertEqual(results, [])

    def test_proxy_rest_invalid_credential_model(self):
        config = {
            'credential_model': 'non.existent.model',
            'endpoint': '/api/test',
        }
        results = self.mixin.kw_autocomplete_proxy_rest(
            query='test',
            config=config
        )
        self.assertEqual(results, [])
