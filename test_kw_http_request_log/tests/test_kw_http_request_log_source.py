from odoo import registry
from odoo.tests import TransactionCase


class TestHttpRequestLog(TransactionCase):

    def setUp(self):
        super().setUp()
        with registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log_source = env1['test.log.source'].create({
                'name': 'Test Source',
                'active': True,
            })
            self.log_source_id = log_source.id
            env1.cr.commit()
        self.env.invalidate_all()

    def test_create_log(self):
        log_source = self.env['test.log.source'].browse(
            self.log_source_id)
        log_id = log_source.kw_http_request_log_create({
            'headers': {'Content-Type': 'application/json'},
            'method': 'POST',
            'name': 'https://test.com',
            'code': 200,
        })

        with registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)

            self.assertTrue(log.id)
            self.assertIn('Test Source', log.log_source_id.name)
            self.assertEqual(
                log.headers, "{'Content-Type': 'application/json'}")
            self.assertEqual(log.method, 'POST')
            self.assertEqual(log.name, 'https://test.com')
            self.assertEqual(log.code, '200')

    def test_write_log(self):
        with registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log_source = env1['test.log.source'].browse(
                self.log_source_id)
            log_id = log_source.kw_http_request_log_create({
                'headers': {'Content-Type': 'application/json'},
                'method': 'POST',
                'name': 'https://test.com',
                'code': 200,
            })
            log_source.kw_http_request_log_update(
                log_id, {'code': 500, })

        with registry(self.env.cr.dbname).cursor() as cr1:
            env1 = self.env(cr=cr1)
            log = env1['kw.http.request.log'].browse(log_id)
            self.assertEqual(log.code, '500')
