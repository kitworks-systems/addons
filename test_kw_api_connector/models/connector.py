import logging

from odoo import models

_logger = logging.getLogger(__name__)


class TestApiConnector(models.Model):
    _name = 'test.kw.api.connector'
    _inherit = ['kw.api.connector', ]
    _description = 'Test Api Connector'
