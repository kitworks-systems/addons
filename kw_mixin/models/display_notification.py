import logging

from odoo import models

_logger = logging.getLogger(__name__)


class DisplayNotification(models.AbstractModel):
    _name = 'kw.display.notification'
    _description = 'Display Notification'

    @staticmethod
    def success(message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    @staticmethod
    def danger(message):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'danger',
                'sticky': False,
            }
        }
