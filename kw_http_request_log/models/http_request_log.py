import base64
import json
import logging
from lxml import etree  # nosec
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HTTPRequestLog(models.Model):
    _name = 'kw.http.request.log'
    _inherit = 'generic.mixin.transaction.utils'
    _description = 'HTTP Requests Log'
    _order = 'create_date DESC'

    name = fields.Char(
        string='URL',
        required=True,
        help='The full URL of the HTTP request, including protocol, domain, '
             'and path.')
    method = fields.Char(
        help='The HTTP method used in the request '
             '(GET, POST, PUT, DELETE, etc.)')
    headers = fields.Text(
        help='HTTP request headers in JSON format. Contains information like '
             'content type and authentication.')
    request_body = fields.Text(
        string='Request',
        help='The body/payload of the HTTP request. For small payloads '
             '(<body_text_log_limit), stored directly in this field. For '
             'larger requests, the body is stored in a separate file.')
    request_body_xml = fields.Text(
        string='Request',
        compute='_compute_request_body_xml',)
    request_body_file = fields.Binary(
        help='Binary storage for large request bodies that exceed the '
             'body_text_log_limit. Used to prevent database performance '
             'issues with large requests.')
    code = fields.Char(
        help='HTTP response status code (e.g., 200 for success, 404 for '
             'not found, etc.).')
    params = fields.Char(
        help='URL query parameters or form data parameters in JSON format.')
    error = fields.Text(
        help='Error message or stack trace if the request processing failed. '
             'Helps in debugging issues with failed requests.')
    response_body = fields.Text(
        string='Response',
        help='The response body returned by the server. For small responses '
             '(body_text_log_limit), stored directly in this field. For '
             'larger responses, the body is stored in a separate file.')
    response_body_file = fields.Binary(
        help='Binary storage for large response bodies that exceed the '
             'body_text_log_limit. Used to prevent database performance '
             'issues with large responses.')
    response_body_xml = fields.Text(
        string='Response',
        compute='_compute_response_body_xml',)
    delete_by_date = fields.Date(
        default=fields.Date.today,
        help='Date when this log entry should be deleted. Calculated based '
             'on the retention policy.')
    log_source_id = fields.Many2one(
        comodel_name='kw.http.request.log.source',
        string='Source',
        required=True,
        ondelete='cascade',
        help='Reference to the log source configuration. Determines retention '
             'period and body size limits for this log entry.')
    type = fields.Selection(
        related='log_source_id.type',)
    log_process_time = fields.Integer(
        compute='_compute_log_process_time',
        store=True, readonly=True,
        help='Displays processing time in seconds', )
    process_time = fields.Datetime(
        readonly=True, )

    def _compute_request_body_xml(self):
        for obj in self:
            obj.request_body_xml = obj.request_body

    def _compute_response_body_xml(self):
        for obj in self:
            obj.response_body_xml = obj.response_body

    @api.depends('process_time', 'create_date')
    def _compute_log_process_time(self):
        for obj in self:
            if obj.process_time and obj.create_date:
                obj.log_process_time = (
                    obj.process_time - obj.create_date
                ).seconds
            else:
                obj.log_process_time = 0

    def _compute_request_body_xml(self):
        for obj in self:
            obj.request_body_xml = obj.request_body

    def _compute_response_body_xml(self):
        for obj in self:
            obj.response_body_xml = obj.response_body

    @staticmethod
    def try_convert2formatted_json(val):
        if isinstance(val, str):
            try:
                val = json.dumps(json.loads(val), indent=2, ensure_ascii=False)
            except Exception as e:
                _logger.debug(e)
                try:
                    parser = etree.XMLParser(resolve_entities=False)
                    tree = etree.fromstring(val, parser)  # nosec
                    val = etree.tostring(
                        tree, pretty_print=True, encoding='unicode')
                except Exception as e1:
                    _logger.debug(e1)
        elif isinstance(val, (dict, list)):
            try:
                val = json.dumps(val, indent=2, ensure_ascii=False)
            except Exception as e:
                _logger.debug(e)
        return val

    def prepare_value(self, vals):
        if self:
            log_source = self.log_source_id
        else:
            log_source = self.env['kw.http.request.log.source'].sudo().browse(
                vals.get('log_source_id'))
        for x in ['request_body', 'response_body', 'error']:
            if not vals.get(x):
                continue
            vals[x] = self.try_convert2formatted_json(vals.get(x))
            if f'{x}_file' not in self._fields:
                continue
            if len(vals.get(x)) < log_source.body_text_log_limit * 1024:
                continue
            vals[f'{x}_file'] = base64.b64encode(str.encode(vals[x]))
            vals[x] = ''
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals = self.prepare_value(vals)
            log_source = self.env['kw.http.request.log.source'].sudo().browse(
                vals.get('log_source_id'))
            if not log_source.active:
                raise Exception('Log source is not active')
            vals['delete_by_date'] = log_source.get_deletion_date()
        return super().create(vals_list)

    def write(self, vals):
        for obj in self:
            super(HTTPRequestLog, obj).write(self.prepare_value(vals))
        return True

    @api.model
    def create_in_new_transaction(self, vals):
        log_source_name = vals.get('log_source_name')
        log_source = False
        if log_source_name:
            log_source = self.env['kw.http.request.log.source'].sudo().search(
                [('name', '=', log_source_name)], limit=1)
        if not log_source:
            log_source_id = vals.get('log_source_id')
            if not log_source_id:
                return False
            log_source = self.env['kw.http.request.log.source'].sudo().browse(
                log_source_id)
        if not log_source.is_log_enabled or not log_source.active:
            return False
        vals['delete_by_date'] = log_source.get_deletion_date()

        result = False
        with self._in_new_transaction(no_raise=False) as nself:
            log = nself.create(vals)
            if log:
                result = log.id
        return result

    @api.model
    def write_in_new_transaction(self, log_id, vals):
        result = False
        with self._in_new_transaction(no_raise=True) as nself:
            log = nself.sudo().browse(log_id)
            if log:
                result = log.write(vals)
        return result

    @api.model
    def cron_delete_outdated_logs(self):
        """Delete logs older than log_retention_period"""
        self.env['kw.http.request.log'].sudo().search([
            ('delete_by_date', '<', fields.Date.today()),
        ]).unlink()
