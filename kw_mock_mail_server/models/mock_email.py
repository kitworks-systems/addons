import logging
import email
import email.utils
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from odoo import fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MockEmail(models.Model):
    _name = 'kw.mock.email'
    _description = 'Email Test Emulator'

    name = fields.Char(
        string='Subject',
        required=True, )
    email_from = fields.Char(
        required=True, )
    email_to = fields.Char(
        required=True, )
    body = fields.Text()

    server_id = fields.Many2one(
        comodel_name='fetchmail.server',
        domain=[('server_type', '=', 'odoo_test_server')])
    state = fields.Selection(
        default='draft',
        selection=[
            ('draft', 'Draft'),
            ('queued', 'Queued for Processing'),
            ('processing', 'Processing'),
            ('processed', 'Processed'),
            ('error', 'Error')
        ], )
    res_id = fields.Integer(
        string='Resource ID')
    res_model = fields.Char(
        string='Resource Model')
    res_name = fields.Char(
        string='Resource Name',
        compute='_compute_res_name')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned User')
    processing_log = fields.Text(
        default='', )
    error_message = fields.Text(
        default='', )

    def _compute_res_name(self):
        for rec in self:
            if rec.res_model and rec.res_id:
                try:
                    record = self.env[rec.res_model].sudo().browse(rec.res_id)
                    if record.exists():
                        rec.res_name = record.display_name
                    else:
                        rec.res_name = (
                            f"Deleted {rec.res_model} ({rec.res_id})")
                except Exception as e:
                    _logger.debug(e)
                    rec.res_name = f"Invalid {rec.res_model} ({rec.res_id})"
            else:
                rec.res_name = False

    def action_queue_test_email(self):
        self.ensure_one()

        if not self.server_id:
            raise UserError(_('Please select a test server first'))

        if self.server_id.server_type != 'odoo_test_server':
            raise UserError(_('Selected server is not a test server'))

        self.state = 'queued'

        log_message = f"\nTest email queued for processing: {self.name}\n"
        log_message += f"From: {self.email_from}\n"
        log_message += f"To: {self.email_to}\n"
        log_message += f"Subject: {self.name}\n"
        log_message += f"Test Server: {self.server_id.name}\n"

        self.processing_log = str(self.processing_log or '') + log_message

    def action_process_now(self):
        self.ensure_one()
        if not self.server_id:
            raise UserError(_('Please select a test server first'))
        self.action_queue_test_email()
        self.server_id.fetch_mail()

    def _prepare_raw_message(self):
        message_id = f"<test-{self.id}-{datetime.now().timestamp()}@odoo.test>"

        msg = MIMEMultipart()
        msg['Message-ID'] = message_id
        msg['Subject'] = self.name
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Date'] = email.utils.formatdate()

        if self.body:
            body_part = MIMEText(self.body, 'plain', 'utf-8')
            msg.attach(body_part)

        return msg.as_bytes()

    def _update_processing_results(self, res_id):
        self.ensure_one()
        log_message = "\nEmail processing completed successfully!\n"

        if not res_id:
            log_message += "No record was created\n"
            self.processing_log = log_message
            return

        rec = self.env[self.server_id.object_id.model].browse(res_id)

        log_message += f"Created record ID: {rec.id}\n"
        log_message += f"Created record model: {rec._name}\n"

        self.res_id = rec.id
        self.res_model = rec._name

        if hasattr(rec, 'user_id') and rec.user_id:
            self.user_id = rec.user_id.id
            log_message += f"Assigned user: {rec.user_id.name}\n"

        self.processing_log = str(self.processing_log or '') + log_message

    def action_reset_test(self):
        self.write({
            'state': 'draft',
            'user_id': False,
            'res_id': False,
            'res_model': False,
            'processing_log': '',
            'error_message': '',
        })
