import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    kw_is_html2attachment_image = fields.Boolean(
        string='Is HTML2Attachment Image',
        default=False,
        index=True,
        help='This attachment was created from HTML content by '
             'kw_html_image2attachment module',
    )
