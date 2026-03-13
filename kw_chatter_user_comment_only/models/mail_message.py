from odoo import models, api
from odoo.fields import Domain


class Message(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _message_fetch(self, domain, max_id=None, min_id=None, limit=30):
        domain = Domain.AND([domain, [('message_type', '=', 'comment')]])
        return super()._message_fetch(
            domain=domain,
            max_id=max_id,
            min_id=min_id,
            limit=limit
        )
