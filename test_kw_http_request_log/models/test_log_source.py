from odoo import fields, models


class TestLogSource(models.Model):
    _name = 'test.log.source'
    _inherit = ['kw.http.request.log.source.mixin']
    _description = 'Test Log Source'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
