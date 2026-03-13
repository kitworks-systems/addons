import logging
from unittest.mock import patch
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestFetchmailServer(TransactionCase):

    def setUp(self):
        super(TestFetchmailServer, self).setUp()

        # Get or create a model for testing (use res.partner)
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'res.partner')], limit=1)

        # Create a test server
        self.test_server = self.env['fetchmail.server'].create({
            'name': 'Test Server',
            'server_type': 'odoo_test_server',
            'state': 'done',
            'object_id': self.test_model.id,
        })

        # Create a regular server for comparison
        self.regular_server = self.env['fetchmail.server'].create({
            'name': 'Regular Server',
            'server_type': 'imap',
            'state': 'draft',
            'object_id': self.test_model.id,
        })

    def test_server_type_selection(self):
        """Test that odoo_test_server is available in selection"""
        server_types = dict(
            self.env['fetchmail.server']._fields['server_type'].selection)
        self.assertIn('odoo_test_server', server_types)
        self.assertEqual(server_types['odoo_test_server'], 'Odoo Test Server')

    def test_connect_test_server(self):
        """Test connecting to test server"""
        result = self.test_server.connect()
        self.assertTrue(result)

    def test_connect_regular_server(self):
        """Test connecting to regular server calls super"""
        with patch.object(self.test_server.__class__.__bases__[0],
                          'connect') as mock_super:
            mock_super.return_value = True
            result = self.regular_server.connect()
            mock_super.assert_called_once()
            self.assertTrue(result)

    def test_button_confirm_login_test_server(self):
        """Test confirming login for test server"""
        result = self.test_server.button_confirm_login()
        self.assertTrue(result)
        self.assertEqual(self.test_server.state, 'done')

    def test_button_confirm_login_regular_server(self):
        """Test confirming login for regular server calls super"""
        with patch.object(self.test_server.__class__.__bases__[0],
                          'button_confirm_login') as mock_super:
            mock_super.return_value = True
            result = self.regular_server.button_confirm_login()
            mock_super.assert_called_once()
            self.assertTrue(result)

    def test_action_view_test_emails(self):
        """Test action to view test emails"""
        action = self.test_server.action_view_test_emails()

        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'kw.mock.email')
        self.assertEqual(action['view_mode'], 'tree,form')
        self.assertEqual(action['domain'],
                         [('server_id', '=', self.test_server.id)])
        self.assertEqual(action['context']['server_id'], self.test_server.id)

    def test_action_queue_test_emails(self):
        """Test action to queue test emails"""
        # Create test emails
        email1 = self.env['kw.mock.email'].create({
            'name': 'Test Email 1',
            'email_from': 'test1@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
            'state': 'draft',
        })

        email2 = self.env['kw.mock.email'].create({
            'name': 'Test Email 2',
            'email_from': 'test2@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
            'state': 'draft',
        })

        # Queue emails
        self.test_server.action_queue_test_emails()

        # Check that emails are queued
        self.assertEqual(email1.state, 'queued')
        self.assertEqual(email2.state, 'queued')

    def test_fetch_mail_with_regular_server(self):
        """Test fetch_mail with regular server calls super"""
        with patch.object(self.test_server.__class__.__bases__[0],
                          'fetch_mail') as mock_super:
            (self.regular_server + self.test_server).fetch_mail()
            mock_super.assert_called_once()

    def test_fetch_mail_with_test_server_no_emails(self):
        """Test fetch_mail with test server but no queued emails"""
        # Should complete without error
        self.test_server.fetch_mail()

    def test_fetch_mail_with_test_server_and_queued_emails(self):
        """Test fetch_mail with test server and queued emails"""
        # Create a queued test email
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Test email body content',
            'server_id': self.test_server.id,
            'state': 'queued',
        })

        # Mock the message_process to avoid actual processing
        with patch('odoo.addons.mail.models.mail_thread.'
                   'MailThread.message_process') as mock_process:
            mock_process.return_value = False  # No record created

            # Fetch mail
            self.test_server.fetch_mail()

            # Check that email was processed
            self.assertEqual(mock_email.state, 'processed')
            mock_process.assert_called_once()

    def test_fetch_mail_with_test_server_creating_record(self):
        """Test fetch_mail with test server creating a record"""
        # Create a queued test email
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Test email body content',
            'server_id': self.test_server.id,
            'state': 'queued',
        })

        # Create a test partner that will be "created" by message_process
        test_partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })

        # Mock the message_process to return the partner ID
        with patch('odoo.addons.mail.models.mail_thread.'
                   'MailThread.message_process') as mock_process:
            mock_process.return_value = test_partner.id

            # Fetch mail
            self.test_server.fetch_mail()

            # Check that email was processed and results updated
            self.assertEqual(mock_email.state, 'processed')
            self.assertEqual(mock_email.res_id, test_partner.id)
            self.assertEqual(mock_email.res_model, 'res.partner')
            mock_process.assert_called_once()

    # def test_fetch_mail_with_test_server_error_handling(self):
    #     """Test fetch_mail with test server handles errors"""
    #     # Create a queued test email
    #     mock_email = self.env['kw.mock.email'].create({
    #         'name': 'Test Email Subject',
    #         'email_from': 'test@example.com',
    #         'email_to': 'recipient@example.com',
    #         'body': 'Test email body content',
    #         'server_id': self.test_server.id,
    #         'state': 'queued',
    #     })
    #
    #     # Mock the message_process to raise an error
    #     with patch('odoo.addons.mail.models.mail_thread.'
    #                'MailThread.message_process') as mock_process:
    #         mock_process.side_effect = Exception('Test error')
    #
    #         # Fetch mail
    #         self.test_server.fetch_mail()
    #
    #         # Check that email is in error state
    #         self.assertEqual(mock_email.state, 'error')
    #         self.assertEqual(mock_email.error_message, 'Test error')
    #         mock_process.assert_called_once()

    def test_fetch_mail_multiple_test_servers(self):
        """Test fetch_mail with multiple test servers"""
        # Create another test server
        test_server2 = self.env['fetchmail.server'].create({
            'name': 'Test Server 2',
            'server_type': 'odoo_test_server',
            'state': 'done',
            'object_id': self.test_model.id,
        })

        # Create queued emails for both servers
        email1 = self.env['kw.mock.email'].create({
            'name': 'Test Email 1',
            'email_from': 'test1@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
            'state': 'queued',
        })

        email2 = self.env['kw.mock.email'].create({
            'name': 'Test Email 2',
            'email_from': 'test2@example.com',
            'email_to': 'recipient@example.com',
            'server_id': test_server2.id,
            'state': 'queued',
        })

        # Mock the message_process
        with patch('odoo.addons.mail.models.mail_thread.'
                   'MailThread.message_process') as mock_process:
            mock_process.return_value = False

            # Fetch mail for both servers
            (self.test_server + test_server2).fetch_mail()

            # Check that both emails were processed
            self.assertEqual(email1.state, 'processed')
            self.assertEqual(email2.state, 'processed')
            self.assertEqual(mock_process.call_count, 2)

    def test_fetch_mail_mixed_server_types(self):
        """Test fetch_mail with mixed server types"""
        # Create queued email for test server
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
            'state': 'queued',
        })

        # Test that test server processes emails when called alone
        self.test_server.fetch_mail()
        self.assertEqual(mock_email.state, 'processed')

        # Test that both servers can be called together without errors
        # This should work regardless of whether there are queued emails
        with patch.object(self.test_server.__class__.__bases__[0],
                          'fetch_mail') as mock_super:
            # This should call super for regular servers
            (self.regular_server + self.test_server).fetch_mail()

            # Check that super was called for regular server
            mock_super.assert_called_once()
