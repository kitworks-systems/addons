import logging

from odoo import models, api, tools

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        if custom_values is None:
            custom_values = {}

        custom_values['user_id'] = \
            self.kw_find_responsible_user_by_email(msg_dict)

        return super(CrmLead, self).message_new(msg_dict, custom_values)

    def kw_find_responsible_user_by_email(self, msg_dict):
        user = self.kw_search_user_by_emails(msg_dict.get('to', ''))
        if user:
            return user.id

        user = self.kw_search_user_by_emails(msg_dict.get('recipients', ''))
        if user:
            return user.id

        return False

    def kw_search_user_by_emails(self, email_string):
        if not email_string:
            return False

        emails = tools.email_split(email_string)

        for email in emails:
            normalized_email = tools.email_normalize(email)
            if not normalized_email:
                continue

            user = self.env['res.users'].search([
                '|', ('login', '=', normalized_email),
                ('partner_id.email', '=', normalized_email),
            ], limit=1)

            if user:
                return user

        return False
