from datetime import timedelta
from odoo import registry, fields
from odoo.tests import TransactionCase
from odoo.modules.registry import Registry


class TestHTTPRequestLog(TransactionCase):

    def setUp(self):
        super().setUp()
        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log_source = env1['test.log.source'].create({
                'name': 'Test Source Log',
                'active': True,
                'log_retention_period': 30,
                'body_text_log_limit': 10,
            })
            self.log_source_id = log_source.id
            env1.cr.commit()
        self.env.invalidate_all()

    def test_create_log(self):
        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'headers': '{"Content-Type": "application/json"}',
                'request_body': '{"test": "data"}',
                'response_body': '{"result": "ok"}',
                'code': '200',
                'log_source_id': self.log_source_id,
            })
            log_id = log.id
            env1.cr.commit()

        with registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertTrue(log.id)
            self.assertEqual(log.name, 'https://test.com')
            self.assertEqual(log.method, 'POST')
            self.assertEqual(
                log.headers, '{"Content-Type": "application/json"}')
            self.assertEqual(
                log.request_body, '{\n  "test": "data"\n}')
            self.assertEqual(
                log.response_body, '{\n  "result": "ok"\n}')
            self.assertEqual(log.code, '200')

    def test_create_log_with_large_body(self):
        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            large_body = 'x' * 11 * 1024  # More than body_text_log_limit
            log = env1['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'request_body': large_body,
                'response_body': large_body,
                'log_source_id': self.log_source_id,
            })
            log_id = log.id
            env1.cr.commit()

        with registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertTrue(log.request_body_file)
            self.assertTrue(log.response_body_file)
            self.assertFalse(log.request_body)
            self.assertFalse(log.response_body)

    def test_create_in_new_transaction(self):
        log_model = self.env['kw.http.request.log']
        log_id = log_model.create_in_new_transaction({
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source_id,
        })

        with registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertTrue(log.id)
            self.assertEqual(log.name, 'https://test.com')

    def test_write_in_new_transaction(self):
        with registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'log_source_id': self.log_source_id,
            })
            log_id = log.id
            env1.cr.commit()

        log_model = self.env['kw.http.request.log']
        log_model.write_in_new_transaction(log_id, {'code': '500'})

        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertEqual(log.code, '500')

    def test_compute_log_process_time(self):
        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'log_source_id': self.log_source_id,
                'process_time': fields.Datetime.now(),
            })
            log_id = log.id
            env1.cr.commit()

        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertGreaterEqual(log.log_process_time, 0)

    def test_cron_delete_outdated_logs(self):
        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'log_source_id': self.log_source_id,
            })
            log_id = log.id
            env1.cr.commit()

        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            log.write({
                'delete_by_date': fields.Date.today() - timedelta(days=10),
            })
            env1.cr.commit()

        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            env1['kw.http.request.log'].cron_delete_outdated_logs()

        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertFalse(log.exists())

    def test_format_html_request_body(self):
        """Test HTML formatting in request body"""
        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            html_content = '<div><p>Test</p></div>'
            log = env1['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'request_body': html_content,
                'log_source_id': self.log_source_id,
            })
            log_id = log.id
            env1.cr.commit()

        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertIn('<div>', log.request_body)
            self.assertIn('<p>', log.request_body)
            self.assertIn('Test', log.request_body)

    def test_format_different_data_types(self):
        """Test formatting of different data types"""
        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].create({
                'name': 'https://test.com',
                'method': 'POST',
                'request_body': {'test': 'data', 'number': 123},
                'response_body': ['item1', 'item2'],
                'log_source_id': self.log_source_id,
            })
            log_id = log.id
            env1.cr.commit()

        # with registry(self.env.cr.dbname).cursor() as cr1:
        with Registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertIn('"test": "data"', log.request_body)
            self.assertIn('"number": 123', log.request_body)
            self.assertIn('"item1"', log.response_body)
            self.assertIn('"item2"', log.response_body)

    def test_create_log_with_invalid_source(self):
        """Test log creation with invalid source"""
        with self.assertRaises(Exception):
            self.env['kw.http.request.log'].create_in_new_transaction({
                'name': 'https://test.com',
                'method': 'POST',
                'log_source_id': 9999,  # Non-existent source
            })

    def test_create_log_with_inactive_source(self):
        # Deactivate the source
        (self.env['kw.http.request.log.source']
            .browse(self.log_source_id)
            .write({'active': False}))

        # Call create_in_new_transaction
        log_id = self.env['kw.http.request.log'].create_in_new_transaction({
            'name': 'https://test.com',
            'method': 'POST',
            'log_source_id': self.log_source_id,
        })
        # Verify that the log was not created
        self.assertFalse(log_id)
