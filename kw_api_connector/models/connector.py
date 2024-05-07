import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class ApiConnector(models.AbstractModel):
    _name = 'kw.api.connector'
    _description = 'Api Connector'

    name = fields.Char(
        readonly=True, )
    image_128 = fields.Image(
        string='Image', max_width=128, max_height=128, readonly=True, )
    api_url = fields.Char(
        readonly=False, )
    is_api_token_used = fields.Boolean(
        string='Use token', readonly=True, )
    is_api_token_static = fields.Boolean(
        string='Static token', readonly=True, )
