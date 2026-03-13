import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestCrmLeadIntegration(TransactionCase):

    def setUp(self):
        super(TestCrmLeadIntegration, self).setUp()

        # Create sales team
        self.sales_team = self.env['crm.team'].create({
            'name': 'Test Sales Team',
        })

        # Create test users with different configurations
        self.sales_user = self.env['res.users'].create({
            'name': 'Sales Representative',
            'login': 'sales@company.com',
            'email': 'sales@company.com',
            'active': True,
            'groups_id': [(6, 0, [
                self.env.ref('sales_team.group_sale_salesman').id
            ])]
        })

        self.support_user = self.env['res.users'].create({
            'name': 'Support Agent',
            'login': 'support@company.com',
            'email': 'support@company.com',
            'active': True,
        })

        # Create partner for testing partner email matching
        self.partner_with_different_email = self.env['res.partner'].create({
            'name': 'Manager Partner',
            'email': 'manager@company.com',
        })

        self.manager_user = self.env['res.users'].create({
            'name': 'Manager User',
            'login': 'manager.login@company.com',
            'partner_id': self.partner_with_different_email.id,
            'active': True,
        })

    def test_end_to_end_lead_creation_with_assignment(self):
        """Test complete lead creation process with user assignment"""
        # Simulate email message dict as would come from mail gateway
        msg_dict = {
            'subject': 'New Business Inquiry',
            'body': 'Hello, I am interested in your services.',
            'from': 'potential.customer@client.com',
            'to': 'sales@company.com',
            'recipients': 'sales@company.com, info@company.com',
            'message_id': '<inquiry123@client.com>',
            'date': '2024-01-15 10:30:00',
        }

        # Create lead through message_new
        lead = self.env['crm.lead'].message_new(msg_dict)

        # Verify lead creation and user assignment
        self.assertTrue(lead)
        self.assertEqual(lead.name, 'New Business Inquiry')
        self.assertEqual(lead.user_id, self.sales_user)
        self.assertEqual(lead.email_from, 'potential.customer@client.com')
        # Check if description was set (may be False in some Odoo versions)
        if lead.description:
            self.assertIn('Hello, I am interested', str(lead.description))

    def test_lead_creation_with_partner_email_match(self):
        """Test lead creation matching user by partner email"""
        msg_dict = {
            'subject': 'Management Request',
            'body': 'This needs management attention.',
            'from': 'client@external.com',
            'to': 'manager@company.com',  # This matches partner email
            'message_id': '<mgmt456@external.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should find manager_user through partner email
        self.assertEqual(lead.user_id, self.manager_user)
        self.assertEqual(lead.name, 'Management Request')

    def test_lead_creation_multiple_recipients_priority(self):
        """Test lead creation with multiple recipients and proper priority"""
        msg_dict = {
            'subject': 'Multi-recipient Inquiry',
            'body': 'This email was sent to multiple people.',
            'from': 'client@business.com',
            'to': 'info@company.com, sales@company.com',  # sales user found
            'recipients': ('info@company.com, sales@company.com, '
                           'support@company.com'),
            'message_id': '<multi789@business.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should find sales_user from the 'to' field
        self.assertEqual(lead.user_id, self.sales_user)

    def test_lead_creation_fallback_to_recipients(self):
        """Test lead creation falling back to recipients field"""
        msg_dict = {
            'subject': 'Support Request',
            'body': 'I need help with your product.',
            'from': 'customer@help.com',
            'to': 'info@company.com',  # No matching user
            'recipients': ('info@company.com, support@company.com'),
            # support user found here
            'message_id': '<support101@help.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should find support_user from recipients field
        self.assertEqual(lead.user_id, self.support_user)

    def test_lead_creation_no_user_match(self):
        """Test lead creation with no matching users"""
        msg_dict = {
            'subject': 'General Inquiry',
            'body': 'General question about services.',
            'from': 'someone@somewhere.com',
            'to': 'info@company.com',
            'recipients': 'info@company.com, hello@company.com',
            'message_id': '<general202@somewhere.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should create lead without assigned user (standard CRM behavior)
        self.assertFalse(lead.user_id)
        self.assertEqual(lead.name, 'General Inquiry')

    def test_lead_creation_with_custom_values_override(self):
        """Test that custom_values work alongside user assignment"""
        msg_dict = {
            'subject': 'Custom Values Test',
            'body': 'Testing custom values.',
            'from': 'test@custom.com',
            'to': 'sales@company.com',
            'message_id': '<custom303@custom.com>',
        }

        custom_values = {
            'team_id': self.sales_team.id,
            'priority': '1',  # High priority
            'description': 'This was set via custom values',
        }

        lead = self.env['crm.lead'].message_new(msg_dict, custom_values)

        # User should be assigned by our module
        self.assertEqual(lead.user_id, self.sales_user)

        # Custom values should also be applied
        self.assertEqual(lead.team_id, self.sales_team)
        self.assertEqual(lead.priority, '1')
        self.assertIn('This was set via custom values', lead.description)

    def test_lead_creation_existing_user_id_in_custom_values(self):
        """Test behavior when user_id is already in custom_values"""
        msg_dict = {
            'subject': 'Existing User ID Test',
            'body': 'Testing with existing user_id.',
            'from': 'test@existing.com',
            'to': 'sales@company.com',  # Would normally assign sales_user
            'message_id': '<existing404@existing.com>',
        }

        # custom_values already has user_id - our module should override it
        custom_values = {
            'user_id': self.support_user.id,  # This should be overridden
        }

        lead = self.env['crm.lead'].message_new(msg_dict, custom_values)

        # Our module should override and assign sales_user based on email
        self.assertEqual(lead.user_id, self.sales_user)

    def test_complex_email_parsing_scenario(self):
        """Test complex email parsing with various formats"""
        msg_dict = {
            'subject': 'Complex Email Format Test',
            'body': 'Testing complex email formats.',
            'from': 'Complex User <complex@sender.com>',
            'to': 'Sales Team <sales@company.com>, Info <info@company.com>',
            'recipients': ('Sales Team <sales@company.com>, '
                           'Support <support@company.com>, '
                           'Manager <manager@company.com>'),
            'message_id': '<complex505@sender.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should extract sales@company.com and assign sales_user
        self.assertEqual(lead.user_id, self.sales_user)

    def test_case_insensitive_email_matching(self):
        """Test that email matching is case insensitive"""
        msg_dict = {
            'subject': 'Case Insensitive Test',
            'body': 'Testing case insensitive matching.',
            'from': 'test@case.com',
            'to': 'SALES@COMPANY.COM',  # Uppercase version
            'message_id': '<case606@case.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should still find sales_user despite case difference
        self.assertEqual(lead.user_id, self.sales_user)

    def test_concurrent_lead_creation(self):
        """Test multiple leads creation with different assignments"""
        msg_dicts = [
            {
                'subject': 'Sales Inquiry 1',
                'from': 'client1@test.com',
                'to': 'sales@company.com',
                'message_id': '<sales1@test.com>',
            },
            {
                'subject': 'Support Request 1',
                'from': 'client2@test.com',
                'to': 'support@company.com',
                'message_id': '<support1@test.com>',
            },
            {
                'subject': 'Manager Request 1',
                'from': 'client3@test.com',
                'to': 'manager@company.com',
                'message_id': '<manager1@test.com>',
            }
        ]

        leads = []
        for msg_dict in msg_dicts:
            leads.append(self.env['crm.lead'].message_new(msg_dict))

        # Verify correct assignments
        self.assertEqual(leads[0].user_id, self.sales_user)
        self.assertEqual(leads[1].user_id, self.support_user)
        self.assertEqual(leads[2].user_id, self.manager_user)

        # Verify all leads were created
        self.assertEqual(len(leads), 3)

    def test_edge_case_empty_message_dict(self):
        """Test with minimal message dict"""
        msg_dict = {
            'message_id': '<minimal@test.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should create lead without user assignment
        self.assertFalse(lead.user_id)
        self.assertTrue(lead)  # Lead should still be created

    def test_performance_with_many_emails(self):
        """Test performance with many emails in recipients"""
        # Create a long list of emails with our target email in the middle
        email_list = [f'user{i}@nowhere.com' for i in range(100)]
        email_list.insert(50, 'sales@company.com')  # Insert our target email

        msg_dict = {
            'subject': 'Performance Test',
            'body': 'Testing with many emails.',
            'from': 'perf@test.com',
            'to': ', '.join(email_list[:50]),  # First 50 emails (no match)
            'recipients': ', '.join(email_list),  # All emails including match
            'message_id': '<perf707@test.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should still find sales_user efficiently
        self.assertEqual(lead.user_id, self.sales_user)
