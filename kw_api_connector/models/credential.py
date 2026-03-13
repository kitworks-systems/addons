import json
import logging
from datetime import datetime

import html
import requests

from odoo import models, fields, exceptions, _
from odoo.addons.kw_mixin.tools import use_fname

_logger = logging.getLogger(__name__)


class ApiCredential(models.AbstractModel):
    _name = 'kw.api.credential'
    _inherit = [
        'generic.mixin.transaction.utils',
        'kw.http.request.log.source.mixin', ]
    _description = 'Api Credential'
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'Api Credential "name" must be unique'), ]

    name = fields.Char(
        help='Unique identifier for the API credential', )
    active = fields.Boolean(
        default=True,
        help='Whether this credential is active and can be used', )
    company_id = fields.Many2one(
        comodel_name='res.company',
        help='Company associated with this API credential', )
    api_connector_id = fields.Many2one(
        comodel_name='kw.api.connector',
        required=True,
        help='API connector configuration for this credential', )
    code = fields.Char(
        string='Connector name',
        related='api_connector_id.name',
        store=True,
        help='Technical name of the associated API connector', )
    type = fields.Selection(
        related='api_connector_id.type',
        help='Data format used by the API connector', )

    @use_fname()
    def get_api_url(self, ext='', **kwargs):
        def urljoin(*args):
            return "/".join(map(lambda x: str(x).strip('/'), args))
        return urljoin(
            self.api_connector_id.api_url.strip('/'), ext.strip('/'))

    @use_fname()
    def get_api_headers(self, **kwargs):
        return {'Content-Type': 'application/json',
                'Accept': 'application/json', }

    @use_fname()
    def is_api_success(self, response, **kwargs):
        return 200 <= response.status_code < 300

    @use_fname()
    def parse_api_error(self, response, **kwargs):
        return {'message': response.text, }

    @use_fname()
    def parse_response(self, response, **kwargs):
        try:
            res = response.json()
        except Exception as e:
            self.kw_http_request_log_source_id.update_log(
                kwargs.get('log'),
                {
                    'code': response.status_code,
                    'response_body': response.text,
                    'error': e,
                })

            return False
        return res

    @use_fname()
    def action_refresh_api_token(self, **kwargs):
        return False

    # pylint: disable=too-many-branches,too-many-return-statements
    # pylint: disable=too-many-locals
    @use_fname()
    def api_request(
            self, method, url=False, renew_token=False, silent=True, **kwargs):
        log = False
        kw = {}
        for x in ['json', 'data', 'params', 'auth', 'headers', 'files']:
            if kwargs.get(x):
                kw[x] = kwargs.get(x)

        if 'headers' not in kw:
            kw['headers'] = self.get_api_headers(renew_token=renew_token)

        full_url = self.get_api_url(url or '')

        data = kwargs.get('data') or kwargs.get('json')
        if self.type == 'xml' and data:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            elif isinstance(data, str):
                data = data.encode('utf-8').decode('utf-8')
            kw['data'] = data.encode('utf-8')
        if self.type == 'html':
            data = html.unescape(data).encode('utf-8').decode('utf-8')
        # if self.type == 'html' and 'data' in kw:
        #     kw['data'] = kw['data'].encode('utf-8')

        if self.is_log_enabled:
            body = data
            if isinstance(body, (bytes, bytearray)):
                body = None

            log = self.kw_http_request_log_source_id.sudo(
            ).create_log({
                'name': full_url,
                'method': method,
                'headers': kw['headers'],
                'params': json.dumps(kwargs.get('params')),
                'request_body': body, })

        try:
            _logger.info(f'BEFORE {kw}')
            response = requests.request(
                method=method, url=full_url, timeout=60,
                allow_redirects=True, **kw)
            _logger.info(f'after {response.text}')
        except Exception as e:
            if self.is_log_enabled:
                self.kw_http_request_log_source_id.update_log(
                    log, {
                        'error': e,
                        'process_time': fields.Datetime.now()
                    })
                _logger.info(f'RESPONSE ERROR {e}')
            if not silent:
                raise exceptions.ValidationError(_(
                    'Connector "%(credential)s" connection error: "%(error)s"'
                ) % {'credential': self.name, 'error': e})
            return False

        if self.is_api_success(response):
            try:
                res = self.parse_response(
                    response=response, log=log, silent=True, )
            except Exception as e:
                if self.is_log_enabled and log:
                    self.kw_http_request_log_source_id.update_log(
                        log, {'code': response.status_code,
                              'response_body': response.text, 'error': e,
                              'process_time': datetime.now()})
                return False

            if self.is_log_enabled and log:
                self.kw_http_request_log_source_id.update_log(
                    log,
                    {'code': response.status_code,
                     'response_body': response.text,
                     'process_time': datetime.now()})
            return res

        parse_result = self.parse_api_error(
            response=response, log=log, silent=True, )

        if self.is_log_enabled and log:
            self.kw_http_request_log_source_id.update_log(
                log, {
                    'code': response.status_code,
                    'response_body': response.text,
                    'error': parse_result['message'],
                    'process_time': datetime.now()})

        if not renew_token and parse_result.get('is_refresh_api_token_needed'):
            if self.action_refresh_api_token():
                return self.api_request(
                    method=method, url=url, data=data,
                    params=kwargs.get('params'), silent=silent,
                    renew_token=renew_token, )

        if not silent:
            raise exceptions.ValidationError(_(
                'Connector "%(credential)s" connection error: "%(error)s"'
                '') % {'credential': self.name, 'error': parse_result})
        return False
