import json
from datetime import timedelta
from odoo import fields
from odoo.tests import TransactionCase


class TestTryConvert2FormattedJson(TransactionCase):
    """Unit tests for try_convert2formatted_json method"""

    def setUp(self):
        super().setUp()
        self.log_model = self.env['kw.http.request.log']

    def test_try_convert2formatted_json_string_json(self):
        """Test try_convert2formatted_json with valid JSON string"""
        input_val = '{"test": "data", "number": 123}'
        result = self.log_model.try_convert2formatted_json(input_val)
        expected = json.dumps(
            json.loads(input_val), indent=2, ensure_ascii=False)
        self.assertEqual(result, expected)

    def test_try_convert2formatted_json_string_xml(self):
        """Test try_convert2formatted_json with XML string"""
        input_val = '<root><item>test</item></root>'
        result = self.log_model.try_convert2formatted_json(input_val)
        self.assertIn('<root>', result)
        self.assertIn('<item>test</item>', result)

    def test_try_convert2formatted_json_string_plain(self):
        """Test try_convert2formatted_json with plain string"""
        input_val = 'plain text'
        result = self.log_model.try_convert2formatted_json(input_val)
        self.assertEqual(result, input_val)

    def test_try_convert2formatted_json_dict(self):
        """Test try_convert2formatted_json with dictionary"""
        input_val = {'test': 'data', 'number': 123}
        result = self.log_model.try_convert2formatted_json(input_val)
        expected = json.dumps(
            input_val, indent=2, ensure_ascii=False)
        self.assertEqual(result, expected)

    def test_try_convert2formatted_json_list(self):
        """Test try_convert2formatted_json with list"""
        input_val = ['item1', 'item2', {'nested': 'value'}]
        result = self.log_model.try_convert2formatted_json(input_val)
        expected = json.dumps(
            input_val, indent=2, ensure_ascii=False)
        self.assertEqual(result, expected)

    def test_try_convert2formatted_json_invalid_json(self):
        """Test try_convert2formatted_json with invalid JSON"""
        input_val = '{invalid json}'
        result = self.log_model.try_convert2formatted_json(input_val)
        self.assertEqual(result, input_val)

    def test_try_convert2formatted_json_invalid_xml(self):
        """Test try_convert2formatted_json with invalid XML"""
        input_val = '<invalid><xml>'
        result = self.log_model.try_convert2formatted_json(input_val)
        self.assertEqual(result, input_val)

    def test_try_convert2formatted_json_empty_string(self):
        """Test try_convert2formatted_json with empty string"""
        input_val = ''
        result = self.log_model.try_convert2formatted_json(input_val)
        self.assertEqual(result, input_val)

    def test_try_convert2formatted_json_none(self):
        """Test try_convert2formatted_json with None"""
        input_val = None
        result = self.log_model.try_convert2formatted_json(input_val)
        self.assertEqual(result, input_val)


class TestPrepareValue(TransactionCase):
    """Unit tests for prepare_value method"""

    def setUp(self):
        super().setUp()
        self.log_model = self.env['kw.http.request.log']
        self.log_source = self.env['kw.http.request.log.source'].create({
            'name': 'Test Source Log',
            'active': True,
            'log_retention_period': 30,
            'body_text_log_limit': 10,
        })

    def test_prepare_value_basic(self):
        """Test prepare_value with basic data"""
        vals = {
            'log_source_id': self.log_source.id,
            'request_body': '{"test": "data"}',
            'response_body': '{"result": "ok"}',
            'error': 'Test error'
        }
        result = self.log_model.prepare_value(vals)
        self.assertIn('"test": "data"', result['request_body'])
        self.assertIn('"result": "ok"', result['response_body'])
        self.assertEqual(result['error'], 'Test error')

    def test_prepare_value_large_body(self):
        """Test prepare_value with large body that should be stored in file"""
        large_content = 'x' * 11 * 1024  # More than body_text_log_limit
        vals = {
            'log_source_id': self.log_source.id,
            'request_body': large_content,
            'response_body': large_content
        }
        result = self.log_model.prepare_value(vals)
        self.assertEqual(result['request_body'], '')
        self.assertEqual(result['response_body'], '')
        self.assertTrue(result.get('request_body_file'))
        self.assertTrue(result.get('response_body_file'))

    def test_prepare_value_empty_fields(self):
        """Test prepare_value with empty fields"""
        vals = {
            'log_source_id': self.log_source.id,
            'request_body': '',
            'response_body': None,
            'error': False
        }
        result = self.log_model.prepare_value(vals)
        self.assertEqual(result['request_body'], '')
        self.assertIsNone(result['response_body'])
        self.assertFalse(result['error'])

    def test_prepare_value_with_instance(self):
        """Test prepare_value when called on existing instance"""
        log = self.log_model.create({
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source.id,
        })
        vals = {
            'request_body': '{"updated": "data"}',
            'response_body': '{"response": "updated"}'
        }
        result = log.prepare_value(vals)
        self.assertIn('"updated": "data"', result['request_body'])
        self.assertIn('"response": "updated"', result['response_body'])

    def test_prepare_value_json_formatting(self):
        """Test prepare_value with different JSON types"""
        vals = {
            'log_source_id': self.log_source.id,
            'request_body': {'test': 'data', 'number': 123},
            'response_body': ['item1', 'item2'],
            'error': {'error_code': 500, 'message': 'Internal Error'}
        }
        result = self.log_model.prepare_value(vals)
        self.assertIn('"test": "data"', result['request_body'])
        self.assertIn('"number": 123', result['request_body'])
        self.assertIn('"item1"', result['response_body'])
        self.assertIn('"item2"', result['response_body'])
        self.assertIn('"error_code": 500', result['error'])

    def test_prepare_value_xml_formatting(self):
        """Test prepare_value with XML data"""
        vals = {
            'log_source_id': self.log_source.id,
            'request_body': '<root><item>test</item></root>',
            'response_body': '<response><status>ok</status></response>'
        }
        result = self.log_model.prepare_value(vals)
        self.assertIn('<root>', result['request_body'])
        self.assertIn('<item>test</item>', result['request_body'])
        self.assertIn('<response>', result['response_body'])
        self.assertIn('<status>ok</status>', result['response_body'])


class TestHTTPRequestLogCRUD(TransactionCase):
    """Tests for CRUD operations without transaction isolation"""

    def setUp(self):
        super().setUp()
        self.log_source = self.env['kw.http.request.log.source'].create({
            'name': 'Test Source Log',
            'active': True,
            'log_retention_period': 30,
            'body_text_log_limit': 10,
        })
        self.log_source_id = self.log_source.id

    def test_create_log_basic(self):
        vals = {
            'name': 'https://test.com',
            'method': 'POST',
            'headers': '{"Content-Type": "application/json"}',
            'request_body': 'raw request',
            'response_body': 'raw response',
            'code': '200',
            'log_source_id': self.log_source_id,
        }

        log = self.env['kw.http.request.log'].create(vals)

        self.assertTrue(log.id)
        self.assertEqual(log.name, vals['name'])
        self.assertEqual(log.method, vals['method'])
        self.assertEqual(log.headers, vals['headers'])
        self.assertEqual(log.code, vals['code'])
        self.assertTrue(log.delete_by_date)
        self.assertEqual(log.log_source_id.id, self.log_source_id)

    def test_create_log_validation_active_source(self):
        # Test that create calls prepare_value and validates log_source
        vals = {
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source_id,
        }

        log = self.env['kw.http.request.log'].create(vals)

        # Verify that log was created successfully
        self.assertTrue(log.exists())
        self.assertEqual(log.log_source_id.id, self.log_source_id)
        self.assertTrue(log.delete_by_date)

        # Test with invalid (non-existent) log source
        vals_invalid = {
            'name': 'https://test2.com',
            'method': 'GET',
            'log_source_id': 99999,  # Non-existent ID
        }

        with self.assertRaises(Exception):
            self.env['kw.http.request.log'].create(vals_invalid)

    def test_create_log_validation_invalid_source(self):
        """Test log creation with invalid source"""
        with self.assertRaises(Exception):
            self.env['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'log_source_id': 9999,  # Non-existent source
            })

    def test_create_log_validation_inactive_source(self):
        """Test log creation with inactive source"""
        # Deactivate the source
        self.log_source.write({'active': False})

        # Test that create raises exception with inactive source
        with self.assertRaises(Exception) as cm:
            self.env['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'log_source_id': self.log_source_id,
            })

        self.assertIn('Log source is not active', str(cm.exception))

    def test_create_log_delete_by_date_calculation(self):
        """Test that delete_by_date is calculated correctly during creation"""
        vals = {
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source_id,
        }

        log = self.env['kw.http.request.log'].create(vals)

        self.assertTrue(log.delete_by_date)
        # Should be set to some future date based on retention period
        self.assertGreater(log.delete_by_date, fields.Date.today())

    def test_write_log_basic(self):
        log = self.env['kw.http.request.log'].create({
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source_id,
        })

        original_method = log.method
        original_name = log.name

        vals_to_update = {
            'code': '500',
            'error': 'Test error message',
            'params': 'test=value'
        }

        log.write(vals_to_update)

        self.assertEqual(log.code, vals_to_update['code'])
        self.assertEqual(log.error, vals_to_update['error'])
        self.assertEqual(log.params, vals_to_update['params'])
        # Ensure unchanged fields remain the same
        self.assertEqual(log.method, original_method)
        self.assertEqual(log.name, original_name)

    def test_write_log_with_prepare_value(self):
        """Test that write method calls prepare_value correctly"""
        log = self.env['kw.http.request.log'].create({
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source_id,
        })

        vals_to_update = {
            'request_body': '{"updated": "data"}',
            'response_body': '{"response": "updated"}',
            'error': '{"error_code": 500}'
        }

        log.write(vals_to_update)

        # Check that JSON was formatted properly
        self.assertIn('"updated": "data"', log.request_body)
        self.assertIn('"response": "updated"', log.response_body)
        self.assertIn('"error_code": 500', log.error)


class TestHTTPRequestLogUtilityMethods(TransactionCase):
    """Tests for utility methods and computed fields"""

    def setUp(self):
        super().setUp()
        self.log_source = self.env['kw.http.request.log.source'].create({
            'name': 'Test Source Log',
            'active': True,
            'log_retention_period': 30,
            'body_text_log_limit': 10,
        })
        self.log_source_id = self.log_source.id

    def test_compute_log_process_time(self):
        log = self.env['kw.http.request.log'].create({
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source_id,
            'process_time': fields.Datetime.now(),
        })

        self.assertGreaterEqual(log.log_process_time, 0)

    def test_cron_delete_outdated_logs(self):
        log = self.env['kw.http.request.log'].create({
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source_id,
        })

        log.write({
            'delete_by_date': fields.Date.today() - timedelta(days=10),
        })

        self.env['kw.http.request.log'].cron_delete_outdated_logs()
        self.assertFalse(log.exists())

    def test_create_log_with_formatting(self):
        """Test create with different data types gets properly formatted"""
        log = self.env['kw.http.request.log'].create({
            'name': 'https://test.com',
            'method': 'POST',
            'request_body': {'test': 'data', 'number': 123},
            'response_body': ['item1', 'item2'],
            'log_source_id': self.log_source_id,
        })
        self.assertIn('"test": "data"', log.request_body)
        self.assertIn('"number": 123', log.request_body)
        self.assertIn('"item1"', log.response_body)
        self.assertIn('"item2"', log.response_body)

    def test_create_log_with_html_content(self):
        """Test HTML formatting in request body"""
        html_content = '<div><p>Test</p></div>'
        log = self.env['kw.http.request.log'].create({
            'name': 'https://test.com',
            'method': 'POST',
            'request_body': html_content,
            'log_source_id': self.log_source_id,
        })

        self.assertIn('<div>', log.request_body)
        self.assertIn('<p>', log.request_body)
        self.assertIn('Test', log.request_body)
