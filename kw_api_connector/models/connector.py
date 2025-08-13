import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class ApiConnector(models.AbstractModel):
    _name = 'kw.api.connector'
    _description = 'Api Connector'

    name = fields.Char(
        readonly=True,
        help='Technical name of the API connector', )
    image_128 = fields.Image(
        string='Image',
        max_width=128,
        max_height=128,
        readonly=True,
        help='Icon representing the API service', )
    type = fields.Selection(
        selection=[
            ('xml', 'XML'),
            ('json', 'JSON'),
            ('html', 'HTML'), ],
        default='json',
        help='Data format used for API communication', )
    api_url = fields.Char(
        readonly=False,
        help='Base URL for API endpoints', )
    is_api_token_used = fields.Boolean(
        string='Use token',
        readonly=True,
        help='Indicates if authentication token is required for API calls', )
    is_api_token_static = fields.Boolean(
        string='Static token',
        readonly=True,
        help='Indicates if the API uses a static token that does not expire', )
