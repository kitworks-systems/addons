import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class TestMockEmail(TransactionCase):

    def setUp(self):
        super(TestMockEmail, self).setUp()

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

    def test_create_mock_email(self):
        """Test creating a mock email"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Test email body content',
            'server_id': self.test_server.id,
        })

        self.assertEqual(mock_email.state, 'draft')
        self.assertEqual(mock_email.name, 'Test Email Subject')
        self.assertEqual(mock_email.email_from, 'test@example.com')
        self.assertEqual(mock_email.email_to, 'recipient@example.com')
        self.assertEqual(mock_email.body, 'Test email body content')
        self.assertEqual(mock_email.server_id, self.test_server)

    def test_queue_test_email_without_server(self):
        """Test queuing email without server should raise error"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Test email body content',
        })

        with self.assertRaises(UserError) as cm:
            mock_email.action_queue_test_email()

        self.assertIn('Please select a test server first', str(cm.exception))

    def test_queue_test_email_with_wrong_server_type(self):
        """Test queuing email with wrong server type should raise error"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Test email body content',
            'server_id': self.regular_server.id,
        })

        with self.assertRaises(UserError) as cm:
            mock_email.action_queue_test_email()

        self.assertIn('Selected server is not a test server',
                      str(cm.exception))

    def test_queue_test_email_success(self):
        """Test successfully queuing test email"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Test email body content',
            'server_id': self.test_server.id,
        })

        mock_email.action_queue_test_email()

        self.assertEqual(mock_email.state, 'queued')
        self.assertIn('Test email queued for processing',
                      mock_email.processing_log)
        self.assertIn('Test Email Subject', mock_email.processing_log)
        self.assertIn('test@example.com', mock_email.processing_log)
        self.assertIn('recipient@example.com', mock_email.processing_log)

    def test_prepare_raw_message(self):
        """Test preparing raw message for processing"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Test email body content',
            'server_id': self.test_server.id,
        })

        raw_message = mock_email._prepare_raw_message()

        self.assertIsInstance(raw_message, bytes)

        # Convert to string for easier testing
        message_str = raw_message.decode('utf-8')

        self.assertIn('Subject: Test Email Subject', message_str)
        self.assertIn('From: test@example.com', message_str)
        self.assertIn('To: recipient@example.com', message_str)
        # Check for base64 encoded content or plain text
        # (VGVzdCBlbWFpbCBib2R5IGNvbnRlbnQ= is base64 for
        # 'Test email body content')
        self.assertIn('VGVzdCBlbWFpbCBib2R5IGNvbnRlbnQ=', message_str)
        self.assertIn('Message-ID:', message_str)
        self.assertIn('Date:', message_str)

    def test_prepare_raw_message_without_body(self):
        """Test preparing raw message without body"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
        })

        raw_message = mock_email._prepare_raw_message()
        message_str = raw_message.decode('utf-8')

        self.assertIn('Subject: Test Email Subject', message_str)
        self.assertIn('From: test@example.com', message_str)
        self.assertIn('To: recipient@example.com', message_str)

    def test_update_processing_results_no_record(self):
        """Test updating processing results when no record created"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
        })

        mock_email._update_processing_results(False)

        self.assertIn('No record was created', mock_email.processing_log)
        self.assertFalse(mock_email.res_id)
        self.assertFalse(mock_email.res_model)

    def test_update_processing_results_with_record(self):
        """Test updating processing results with created record"""
        # Create a test partner
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })

        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
        })

        mock_email._update_processing_results(partner.id)

        self.assertEqual(mock_email.res_id, partner.id)
        self.assertEqual(mock_email.res_model, 'res.partner')
        self.assertIn('Email processing completed successfully',
                      mock_email.processing_log)
        self.assertIn(f'Created record ID: {partner.id}',
                      mock_email.processing_log)

    def test_update_processing_results_with_user_assignment(self):
        """Test updating processing results with user assignment"""
        # Create a test partner with assigned user
        # (using user_id field if available)
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })

        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
        })

        mock_email._update_processing_results(partner.id)

        # res.partner doesn't have user_id field, so user_id should not be set
        self.assertFalse(mock_email.user_id)
        self.assertIn('Email processing completed successfully',
                      mock_email.processing_log)

    def test_compute_res_name(self):
        """Test computing resource name"""
        # Create a test partner
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@example.com',
        })

        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
            'res_id': partner.id,
            'res_model': 'res.partner',
        })

        self.assertEqual(mock_email.res_name, partner.display_name)

    def test_compute_res_name_nonexistent_record(self):
        """Test computing resource name for non-existent record"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
            'res_id': 99999,  # Non-existent ID
            'res_model': 'res.partner',
        })

        self.assertIn('Deleted res.partner (99999)', mock_email.res_name)

    def test_action_reset_test(self):
        """Test resetting test email"""
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Email Subject',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'server_id': self.test_server.id,
            'state': 'processed',
            'res_id': 1,
            'res_model': 'res.partner',
            'processing_log': 'Some log',
            'error_message': 'Some error',
        })

        # Create a test user and assign it
        test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser@example.com',
            'email': 'testuser@example.com',
        })
        mock_email.user_id = test_user

        mock_email.action_reset_test()

        self.assertEqual(mock_email.state, 'draft')
        self.assertFalse(mock_email.user_id)
        self.assertFalse(mock_email.res_id)
        self.assertFalse(mock_email.res_model)
        self.assertEqual(mock_email.processing_log, '')
        self.assertEqual(mock_email.error_message, '')
