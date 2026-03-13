# pylint: disable=E8102
from odoo.tests.common import TransactionCase


class TestCommon(TransactionCase):
    def setUp(self):
        super().setUp()
        self.source = self.env['kw.http.request.log.source'].create({
            'name': 'Test Source',
            'active': True,
            'sequence': 1,
            'is_log_enabled': True,
            'log_retention_period': 30,
            'body_text_log_limit': 100,
        })

    def tearDown(self):
        super().tearDown()
        # self.env['kw.http.request.log'].sudo()._cr.execute(
        #     "SELECT setval('kw_http_request_log_id_seq', 1)"
        # )
        # self.env['kw.http.request.log.source'].sudo()._cr.execute(
        #     "SELECT setval('kw_http_request_log_source_id_seq', 1)"
        # )
        self.env['kw.http.request.log'].search([
            ('log_source_id', '=', self.source.id)
        ]).unlink()
        self.source.unlink()
        # Видалено self.env.cr.commit() - у тестах Odoo 15.0 транзакції
        # управляються автоматично
