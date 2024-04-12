import logging
from datetime import timedelta

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class HTTPRequestSource(models.Model):
    _name = 'kw.http.request.source'
    _description = 'HTTP Request Source'
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

    @api.model
    def create_log(self, name, vals):
        log_source = self.sudo().search([('name', '=', name)], limit=1)
        if not log_source:
            return False
        vals['log_source_id'] = log_source.id
        log_model = self.env['kw.http.request.log'].sudo()
        return log_model.create_in_new_transactionva(vals)
