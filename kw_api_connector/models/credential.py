import json
import logging
import os

import requests
from html2text import html2text

from odoo import models, fields, exceptions, _

_logger = logging.getLogger(__name__)


class ApiCredential(models.AbstractModel):
    _name = 'kw.api.credential'
    _inherit = ['kw.http.request.log.source.mixin', ]
    _description = 'Api Credential'
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'Api Credential "name" must be unique'), ]

    name = fields.Char()

    active = fields.Boolean(
        default=True, )
    company_id = fields.Many2one(
        comodel_name='res.company', )
    api_connector_id = fields.Many2one(
        comodel_name='kw.api.connector', required=True, )
    code = fields.Char(
        related='api_connector_id.name', string='Code', )

    def get_api_url(self, ext=''):
        self.ensure_one()
        fname = f'get_api_url_{self.code}'
        if hasattr(self, fname):
            return getattr(self, fname)(ext)
        return os.path.join(
            self.api_connector_id.api_url.strip('/'), ext.strip('/'))

    def get_api_headers(self, **kw):
        self.ensure_one()
        fname = f'get_api_headers_{self.code}'
        if hasattr(self, fname):
            return getattr(self, fname)(**kw)
        return {'Content-Type': 'application/json',
                'Accept': 'application/json', }

    def is_api_success(self, response):
        self.ensure_one()
        fname = f'is_api_success_{self.code}'
        if hasattr(self, fname):
            return getattr(self, fname)(response)
        return 200 <= response.status_code < 300

    def parse_api_error(self, response, res=None, log=None, silent=True):
        self.ensure_one()
        fname = f'parse_api_error_{self.code}'
        if hasattr(self, fname):
            return getattr(self, fname)(response, res=res, log=log,
                                        silent=silent)
        return {'message': response.text}

    def action_refresh_api_token(self):
        self.ensure_one()
        fname = f'action_refresh_api_token_{self.code}'
        if hasattr(self, fname):
            return getattr(self, fname)()
        return False

    # pylint: disable=too-many-branches,too-many-return-statements
    def api_request(self, method, url, data=None, params=None,
                    headers=None, silent=True, renew_token=False):
        self.ensure_one()
        fname = f'api_request_{self.code}'
        if hasattr(self, fname):
            return getattr(self, fname)(
                method, url, data=None, params=None,
                headers=None, silent=True, renew_token=False)
        if headers is None:
            headers = self.get_api_headers(renew_token=renew_token)
        log = False
        if self.is_log_enabled:
            log = self.kw_http_request_log_source_id.sudo(
            ).create_log({
                'name': self.get_api_url(url), 'method': method,
                'headers': headers, 'params': json.dumps(params),
                'request_body': data, })
        try:
            response = requests.request(
                method=method, url=self.get_api_url(url), json=data,
                allow_redirects=True,
                params=params, headers=headers, timeout=60, )
        except Exception as e:
            if self.is_log_enabled:
                self.kw_http_request_log_source_id.update_log(
                    log, {'error': e})
            if not silent:
                raise exceptions.ValidationError(_(
                    'Connector "%(credential)s" connection error: "%(error)s"'
                    '') % {'credential': self.name, 'error': e})
            return False

        if self.is_api_success(response):
            try:
                res = response.json()
            except Exception as e:
                if self.is_log_enabled and log:
                    self.kw_http_request_log_source_id.update_log(
                        log, {'code': response.status_code,
                              'response_body': response.text, 'error': e, })
                return False

            if self.is_log_enabled and log:
                self.kw_http_request_log_source_id.update_log(
                    log,
                    {'code': response.status_code, 'response_body': res, })
            return res

        try:
            res = response.json()
        except Exception as e:
            if self.is_log_enabled and log:
                _logger.debug(e)
                self.kw_http_request_log_source_id.update_log(
                    log, {
                        'code': response.status_code,
                        'response_body': response.text,
                        'error': html2text(response.text).split('\n')[0]})
            if not silent:
                raise exceptions.ValidationError(_(
                    'Connector "%(credential)s" connection error: "%(error)s"'
                    '') % {'credential': self.name,
                           'error': html2text(response.text)})
            return False

        parse_result = self.parse_api_error(
            response=response, res=res, log=log, silent=True, )

        if self.is_log_enabled and log:
            self.kw_http_request_log_source_id.update_log(
                log, {
                    'code': response.status_code,
                    'response_body': response.text,
                    'error': parse_result['message']})

        if not renew_token and parse_result.get('is_refresh_api_token_needed'):
            if self.action_refresh_api_token():
                return self.api_request(
                    method=method, url=url, data=data, params=params,
                    silent=silent, renew_token=renew_token, )

        if not silent:
            raise exceptions.ValidationError(_(
                'Connector "%(credential)s" connection error: "%(error)s"'
                '') % {'credential': self.name, 'error': parse_result})
        return False
