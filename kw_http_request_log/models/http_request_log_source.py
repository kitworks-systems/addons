import logging
import os
from base64 import b64encode
from datetime import timedelta

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class HTTPRequestLogSource(models.Model):
    _name = 'kw.http.request.log.source'
    _description = 'HTTP Request Log Source'
    _order = 'sequence, id'
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'HTTP Request Log Source "name" must be unique'), ]

    name = fields.Char(
        required=True,
        readonly=True,
        help='Unique identifier for the log source. Used to identify where '
             'the requests are coming from.')
    active = fields.Boolean(
        default=True,
        help='If unchecked, this source will be hidden from the list view '
             'and will not accept new logs.')
    sequence = fields.Integer(
        default=1,
        help='Determines the order of sources in the list view. Lower numbers '
             'appear first.')
    is_log_enabled = fields.Boolean(
        default=True,
        string='Log enabled',
        help='If enabled, all HTTP requests on this source will be stored in '
             'the HTTP Request Log. Disable to temporarily stop logging '
             'without removing the source.')
    log_retention_period = fields.Integer(
        string='Retention time, days',
        help='Log Retention Period in days, after this date logs will be '
             'removed automatically by the cleanup cron job. Set to 0 to '
             'keep logs indefinitely.')
    body_text_log_limit = fields.Integer(
        default=100,
        string='Body limit, Kb',
        help='If request or response body data bigger then limit, it will be '
             'stored as an attachment file instead of text field. This helps '
             'to manage database size and performance.')

    type = fields.Selection(
        default='json',
        selection=[
            ('json', 'JSON'),
            ('xml', 'XML'),
            ('html', 'HTML')], )

    def get_deletion_date(self):
        self.ensure_one()
        return (fields.Datetime.now() + timedelta(
            days=self.log_retention_period)).date()

    def create_log(self, vals):
        self.ensure_one()
        vals['log_source_id'] = self.id
        log_model = self.env['kw.http.request.log'].sudo()
        return log_model.create_in_new_transaction(vals)

    @api.model
    def update_log(self, log_id, vals):
        if not log_id:
            return False
        log_model = self.env['kw.http.request.log'].sudo()
        return log_model.write_in_new_transaction(log_id, vals)


class HTTPRequestSourceMixin(models.AbstractModel):
    _name = 'kw.http.request.log.source.mixin'
    _description = 'HTTP Request Log Source mixin'

    kw_http_request_log_source_id = fields.Many2one(
        comodel_name='kw.http.request.log.source',
        string='Request source',
        required=True,
        delegate=True,
        ondelete='cascade',
        help='Reference to the log source configuration. Defines logging '
             'settings such as retention period and body size limits.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'kw_http_request_log_source_id' in vals:
                continue
            name = b64encode(os.urandom(6)).decode('utf-8')
            name = f'{vals.get("name")}_{name}'
            vals['kw_http_request_log_source_id'] = \
                self.env['kw.http.request.log.source'].sudo().create({
                    'name': name, }).id

        return super().create(vals_list)

    def write(self, vals):
        if 'active' in vals:
            self.mapped('kw_http_request_log_source_id').write({
                'active': vals['active']})
        return super().write(vals)

    def kw_http_request_log_create(self, vals):
        self.ensure_one()
        return self.kw_http_request_log_source_id.create_log(vals)

    def kw_http_request_log_update(self, log_id, vals):
        return self.kw_http_request_log_source_id.update_log(log_id, vals)
