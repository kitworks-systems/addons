from odoo import models, fields


class TestHtmlImage2AttachmentModel(models.Model):
    _name = 'test.html_image2attachment'
    _description = 'Test HTML Image to Attachment Model'
    _inherit = ['kw.html_image2attachment.mixin']

    name = fields.Char(required=True)
    description = fields.Html()
    note = fields.Html()

    _kw_html_image2attachment_fields = ['description', 'note']
