import logging
from datetime import timedelta

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class HTTPRequestLogSource(models.Model):
    _name = 'kw.http.request.log.source'
    _description = 'HTTP Request Log Source'
    _order = 'sequence, id'
    _sql_constraints = [
        ('name_uniq', 'unique (name)', '"name" must be unique.'), ]

    name = fields.Char(
        required=True, readonly=True, )
    active = fields.Boolean(
        default=True, )
    sequence = fields.Integer(
        default=1, )
    is_log_enabled = fields.Boolean(
        default=True, string='Log enabled',
        help='If enabled, all HTTP requests to API will be stored '
             'in the HTTP Request Log.', )
    log_retention_period = fields.Integer(
        string='Retention period', help='Log Retention Period in days', )
    body_text_log_limit = fields.Integer(
        default=100, string='Body limit, Kb',
        help='If request or response body data bigger then limit, '
             'it will stored to attachment file', )

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
        log_model = self.env['kw.http.request.log'].sudo()
        return log_model.write_in_new_transaction(log_id, vals)


class HTTPRequestSourceMixin(models.AbstractModel):
    _name = 'kw.http.request.log.source.mixin'
    _description = 'HTTP Request Log Source mixin'

    kw_http_request_log_source_id = fields.Many2one(
        comodel_name='kw.http.request.log.source', string='Request source',
        required=True, delegate=True, )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'kw_http_request_log_source_id' in vals:
                continue
            if vals.get('name'):
                vals['kw_http_request_log_source_id'] = \
                    self.env['kw.http.request.log.source'].sudo().create({
                        'name': vals.get('name'), }).id

        return super().create(vals_list)
