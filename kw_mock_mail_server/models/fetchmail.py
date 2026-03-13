import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    server_type = fields.Selection(
        selection_add=[('odoo_test_server', 'Odoo Test Server')],
        ondelete={'odoo_test_server': 'cascade'}, )

    def fetch_mail(self):
        another_servers = self.filtered(
            lambda mail: not mail.server_type.startswith('odoo_test_server'))
        if another_servers:
            super(FetchmailServer, another_servers).fetch_mail()

        test_servers = self.filtered(
            lambda mail: mail.server_type.startswith('odoo_test_server'))

        if not test_servers:
            return
        additionnal_context = {'fetchmail_cron_running': True}
        MailThread = self.env['mail.thread']

        test_emails = self.env['kw.mock.email'].search([
            ('state', '=', 'queued'),
            ('server_id', 'in', test_servers.ids)
        ], order='create_date asc')

        for test_email in test_emails:
            server = test_email.server_id
            additionnal_context['default_fetchmail_server_id'] = server.id
            try:
                test_email.state = 'processing'

                message = test_email._prepare_raw_message()

                res_id = MailThread.with_context(
                    **additionnal_context).message_process(
                    server.object_id.model,
                    message,
                    save_original=server.original,
                    strip_attachments=(not server.attach)
                )

                test_email._update_processing_results(res_id)
                test_email.state = 'processed'

            except Exception as e:
                _logger.info(
                    'Failed to process test email %s from server %s.'
                    '', test_email.name, server.name, exc_info=True)
                test_email.state = 'error'
                test_email.error_message = str(e)

    def connect(self):
        if self.server_type == 'odoo_test_server':
            return True
        return super(FetchmailServer, self).connect()

    def button_confirm_login(self):
        if self.server_type == 'odoo_test_server':
            self.write({'state': 'done'})
            return True
        return super(FetchmailServer, self).button_confirm_login()

    def action_view_test_emails(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Test Emails for {self.name}',
            'res_model': 'kw.mock.email',
            'view_mode': 'tree,form',
            'domain': [('server_id', '=', self.id)],
            'context': {'server_id': self.id},
            'target': 'current',
        }

    def action_queue_test_emails(self):
        self.env['kw.mock.email'].search([
            ('server_id', 'in', self.ids)
        ]).write({'state': 'queued'})
