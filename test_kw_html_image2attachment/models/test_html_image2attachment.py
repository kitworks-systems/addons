from odoo import models, fields


class TestHtmlImage2Attachment(models.Model):
    _name = 'test.html_image2attachment'
    _description = 'Test Html Image to Attachment'
    _inherit = ['kw.html_image2attachment.mixin']

    _kw_html_image2attachment_fields = ['description', 'note']

    name = fields.Char(required=True)
    description = fields.Html()
    note = fields.Html()
