import base64
import json
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HTTPRequestLog(models.Model):
    _name = 'kw.http.request.log'
    _inherit = 'generic.mixin.transaction.utils'
    _description = 'HTTP Requests Log'
    _order = 'create_date DESC'

    name = fields.Char(
        string='URL', required=True, )
    method = fields.Char()

    headers = fields.Text()

    request_body = fields.Text(
        string='Request', )
    request_body_file = fields.Binary()

    params = fields.Char()

    error = fields.Text()

    response_body = fields.Text(
        string='Response', )
    response_body_file = fields.Binary()

    delete_by_date = fields.Date(
        default=fields.Date.today, )
    log_source_id = fields.Many2one(
        comodel_name='kw.http.request.source', string='Source',
        required=True, )

    @staticmethod
    def try_convert2formatted_json(val):
        try:
            val = json.dumps(json.loads(val), indent=2, ensure_ascii=False)
        except Exception as e:
            _logger.debug(e)
        return val

    @api.model
    def prepare_value(self, vals):
        log_source = self.env['kw.http.request.source'].sudo().browse(
            vals.get('log_source_id'))
        for x in ['request_body', 'response_body', 'error']:
            if not vals.get(x):
                continue
            vals[x] = self.try_convert2formatted_json(vals.get(x))
            file_field = f'{x}_file'
            if file_field not in self._fields:
                continue
            if len(vals.get(x)) > log_source.body_text_log_limit * 1024:
                vals[x] = str.encode(vals[x])
                vals[file_field] = base64.b64encode(vals[x])
                vals[x] = ''
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals = self.prepare_value(vals)
            log_source = self.env['kw.http.request.source'].sudo().browse(
                vals.get('log_source_id'))
            vals['delete_by_date'] = log_source.get_deletion_date()
        return super().create(vals_list)

    def write(self, vals):
        return super().write(self.prepare_value(vals))

    @api.model
    def create_in_new_transaction(self, vals):
        log_source_name = vals.get('log_source_name')
        log_source = False
        if log_source_name:
            log_source = self.env['kw.http.request.source'].sudo().search(
                [('name', '=', log_source_name)], limit=1)
        if not log_source:
            log_source_id = vals.get('log_source_id')
            if not log_source_id:
                return False
            log_source = self.env['kw.http.request.source'].sudo().browse(
                log_source_id)
        if not log_source.is_log_enabled:
            return False
        vals['delete_by_date'] = log_source.get_deletion_date()

        result = False
        with self._in_new_transaction(no_raise=True) as nself:
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
