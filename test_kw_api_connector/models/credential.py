import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class TestApiCredential(models.Model):
    _name = 'test.kw.api.credential'
    _inherit = ['kw.api.credential', ]
    _description = 'Test Api Credential'

    api_connector_id = fields.Many2one(
        comodel_name='test.kw.api.connector', required=True, )

    def action_test1(self):
        self.api_request('GET', '/test_kw_api_connector/test1')

    def get_api_headers_test_kw_api_connector_localhost(self, **kw):
        return {'Content-Type': 'text/plain', }
