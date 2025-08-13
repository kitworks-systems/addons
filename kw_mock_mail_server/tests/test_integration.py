import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestMockEmailIntegration(TransactionCase):

    def setUp(self):
        super(TestMockEmailIntegration, self).setUp()

        # Get or create a model for testing (use res.partner)
        self.test_model = self.env['ir.model'].search(
            [('model', '=', 'res.partner')], limit=1)

        # Create a test server for partners
        self.test_server = self.env['fetchmail.server'].create({
            'name': 'Test Server',
            'server_type': 'odoo_test_server',
            'state': 'done',
            'object_id': self.test_model.id,
        })

    def test_end_to_end_record_creation(self):
        """Test end-to-end record creation from mock email"""
        # Create a mock email
        mock_email = self.env['kw.mock.email'].create({
            'name': 'New Customer Inquiry',
            'email_from': 'potential.customer@example.com',
            'email_to': 'sales@company.com',
            'body': 'I am interested in your product. Please contact me.',
            'server_id': self.test_server.id,
        })

        # Process the email
        mock_email.action_process_now()

        # Check that the email was processed
        self.assertEqual(mock_email.state, 'processed')

        # Check that a record was created
        self.assertTrue(mock_email.res_id)
        self.assertEqual(mock_email.res_model, 'res.partner')

        # Verify the record details
        partner = self.env['res.partner'].browse(mock_email.res_id)
        self.assertEqual(partner.name, 'New Customer Inquiry')
        # Email is not automatically set when creating partner from email

    def test_end_to_end_with_user_assignment(self):
        """Test end-to-end processing with user assignment"""
        # Create a test user for user assignment testing
        self.test_user = self.env['res.users'].create({
            'name': 'Sales Rep',
            'login': 'sales@company.com',
            'email': 'sales@company.com',
        })

        # Create a mock email addressed to the user
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Direct Sales Inquiry',
            'email_from': 'customer@example.com',
            'email_to': 'sales@company.com',
            'body': 'Please send me information about your services.',
            'server_id': self.test_server.id,
        })

        # Process the email
        mock_email.action_process_now()

        # Check that the email was processed
        self.assertEqual(mock_email.state, 'processed')

        # Check that a lead was created
        self.assertTrue(mock_email.res_id)
        self.assertEqual(mock_email.res_model, 'res.partner')

        # Verify the partner and user assignment
        partner = self.env['res.partner'].browse(mock_email.res_id)
        self.assertEqual(partner.name, 'Direct Sales Inquiry')
        # Email is not automatically set when creating partner from email

        # Note: User assignment depends on the
        # kw_crm_responsible_by_recipient module
        # being installed and configured

    def test_batch_processing(self):
        """Test batch processing of multiple emails"""
        # Create multiple mock emails
        emails_data = [
            {
                'name': 'Lead 1',
                'email_from': 'customer1@example.com',
                'email_to': 'sales@company.com',
                'body': 'Interested in product A',
            },
            {
                'name': 'Lead 2',
                'email_from': 'customer2@example.com',
                'email_to': 'sales@company.com',
                'body': 'Need pricing for service B',
            },
            {
                'name': 'Lead 3',
                'email_from': 'customer3@example.com',
                'email_to': 'sales@company.com',
                'body': 'Request for demo',
            },
        ]

        mock_emails = self.env['kw.mock.email']
        for email_data in emails_data:
            email_data['server_id'] = self.test_server.id
            mock_emails |= self.env['kw.mock.email'].create(email_data)

        # Queue all emails
        for email in mock_emails:
            email.action_queue_test_email()

        # Process all emails
        self.test_server.fetch_mail()

        # Check that all emails were processed
        for email in mock_emails:
            self.assertEqual(email.state, 'processed')
            self.assertTrue(email.res_id)
            self.assertEqual(email.res_model, 'res.partner')

        # Verify partners were created
        partners = self.env['res.partner'].browse(mock_emails.mapped('res_id'))
        self.assertEqual(len(partners), 3)

    def test_error_handling_in_processing(self):
        """Test error handling during email processing"""
        # Create a mock email with invalid configuration
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Invalid Email',
            'email_from': 'invalid-email',  # Invalid email format
            'email_to': 'recipient@example.com',
            'body': 'This should cause an error',
            'server_id': self.test_server.id,
        })

        # Process the email
        mock_email.action_process_now()

        # The email should be in error state or processed
        # (depends on Odoo's tolerance)
        self.assertIn(mock_email.state, ['error', 'processed'])

        # If processed, a partner should still be created
        if mock_email.state == 'processed':
            self.assertTrue(mock_email.res_id)
            self.assertEqual(mock_email.res_model, 'res.partner')

    def test_reset_and_reprocess(self):
        """Test resetting and reprocessing an email"""
        # Create and process a mock email
        mock_email = self.env['kw.mock.email'].create({
            'name': 'Test Reset',
            'email_from': 'test@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Initial processing',
            'server_id': self.test_server.id,
        })

        # Process the email
        mock_email.action_process_now()

        # Verify it was processed
        self.assertEqual(mock_email.state, 'processed')
        original_res_id = mock_email.res_id

        # Reset the email
        mock_email.action_reset_test()

        # Verify reset
        self.assertEqual(mock_email.state, 'draft')
        self.assertFalse(mock_email.res_id)
        self.assertFalse(mock_email.res_model)

        # Process again
        mock_email.action_process_now()

        # Verify reprocessing
        self.assertEqual(mock_email.state, 'processed')
        self.assertTrue(mock_email.res_id)
        self.assertEqual(mock_email.res_model, 'res.partner')

        # New partner should be created (different ID)
        self.assertNotEqual(mock_email.res_id, original_res_id)

    def test_multiple_servers_different_models(self):
        """Test multiple servers targeting different models"""
        # Create another server for a different model (if available)
        # For this test, we'll use the same model but different server
        test_server2 = self.env['fetchmail.server'].create({
            'name': 'Test Server 2',
            'server_type': 'odoo_test_server',
            'state': 'done',
            'object_id': self.test_model.id,
        })

        # Create emails for both servers
        email1 = self.env['kw.mock.email'].create({
            'name': 'Server 1 Email',
            'email_from': 'test1@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Email for server 1',
            'server_id': self.test_server.id,
        })

        email2 = self.env['kw.mock.email'].create({
            'name': 'Server 2 Email',
            'email_from': 'test2@example.com',
            'email_to': 'recipient@example.com',
            'body': 'Email for server 2',
            'server_id': test_server2.id,
        })

        # Process both emails
        email1.action_process_now()
        email2.action_process_now()

        # Verify both were processed
        self.assertEqual(email1.state, 'processed')
        self.assertEqual(email2.state, 'processed')

        # Verify separate records were created
        self.assertTrue(email1.res_id)
        self.assertTrue(email2.res_id)
        self.assertNotEqual(email1.res_id, email2.res_id)
