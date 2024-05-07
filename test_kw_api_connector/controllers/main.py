import logging

from odoo import http
from odoo.http import Response

_logger = logging.getLogger(__name__)


class Controller(http.Controller):

    @http.route(route=['/test_kw_api_connector/test1'],
                type='http', auth='public', website=False, sitemap=False, )
    def kw_api_connector_test(self, **kw):
        response = Response('{"a": 1}', status=200, )
        return response
