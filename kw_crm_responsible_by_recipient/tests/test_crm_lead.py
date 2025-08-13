import logging
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestCrmLeadResponsibleByRecipient(TransactionCase):

    def setUp(self):
        super(TestCrmLeadResponsibleByRecipient, self).setUp()

        # Create test users
        self.user1 = self.env['res.users'].create({
            'name': 'Test User 1',
            'login': 'user1@example.com',
            'email': 'user1@example.com',
            'active': True,
        })

        self.user2 = self.env['res.users'].create({
            'name': 'Test User 2',
            'login': 'user2@example.com',
            'email': 'user2@example.com',
            'active': True,
        })

        # Create inactive user (create as active first, then deactivate)
        self.inactive_user = self.env['res.users'].create({
            'name': 'Inactive User',
            'login': 'inactive@example.com',
            'email': 'inactive@example.com',
            'active': True,
        })
        # Use sudo to bypass access restrictions for deactivation
        self.inactive_user.sudo().write({'active': False})

        # Create user with partner email different from login
        self.user_partner = self.env['res.users'].create({
            'name': 'User with Partner Email',
            'login': 'partneruser@example.com',
            'partner_id': self.env['res.partner'].create({
                'name': 'Partner User',
                'email': 'partner@example.com',
            }).id
        })

    def test_kw_search_user_by_emails_empty_string(self):
        """Test searching user with empty email string"""
        lead = self.env['crm.lead']
        result = lead.kw_search_user_by_emails('')
        self.assertFalse(result)

    def test_kw_search_user_by_emails_none(self):
        """Test searching user with None email string"""
        lead = self.env['crm.lead']
        result = lead.kw_search_user_by_emails(None)
        self.assertFalse(result)

    def test_kw_search_user_by_emails_single_email_by_login(self):
        """Test searching user by login email"""
        lead = self.env['crm.lead']
        result = lead.kw_search_user_by_emails('user1@example.com')
        self.assertEqual(result, self.user1)

    def test_kw_search_user_by_emails_single_email_by_partner(self):
        """Test searching user by partner email"""
        lead = self.env['crm.lead']
        result = lead.kw_search_user_by_emails('partner@example.com')
        self.assertEqual(result, self.user_partner)

    def test_kw_search_user_by_emails_multiple_emails(self):
        """Test searching user in multiple emails string"""
        lead = self.env['crm.lead']
        result = lead.kw_search_user_by_emails(
            'unknown@example.com, user2@example.com, another@example.com')
        self.assertEqual(result, self.user2)

    def test_kw_search_user_by_emails_no_match(self):
        """Test searching user with no matching email"""
        lead = self.env['crm.lead']
        result = lead.kw_search_user_by_emails('nomatch@example.com')
        self.assertFalse(result)

    def test_kw_search_user_by_emails_inactive_user(self):
        """Test that inactive users are not returned"""
        lead = self.env['crm.lead']
        # First verify user exists but is inactive
        inactive_user = self.env['res.users'].with_context(
            active_test=False).search([
                ('login', '=', 'inactive@example.com'),
                ('active', '=', False)
            ])
        self.assertTrue(inactive_user)

        # But shouldn't be found by our search
        # (Odoo ORM automatically filters active records)
        result = lead.kw_search_user_by_emails('inactive@example.com')
        self.assertFalse(result)

    def test_kw_search_user_by_emails_malformed_email(self):
        """Test searching with malformed email addresses"""
        lead = self.env['crm.lead']
        result = lead.kw_search_user_by_emails('not-an-email')
        self.assertFalse(result)

    def test_kw_find_responsible_user_by_email_to_field(self):
        """Test finding responsible user from 'to' field"""
        lead = self.env['crm.lead']
        msg_dict = {
            'to': 'user1@example.com',
            'recipients': 'user2@example.com'
        }
        result = lead.kw_find_responsible_user_by_email(msg_dict)
        self.assertEqual(result, self.user1.id)

    def test_kw_find_responsible_user_by_email_recipients_field(self):
        """Test finding responsible user from 'recipients' field"""
        lead = self.env['crm.lead']
        msg_dict = {
            'to': 'unknown@example.com',
            'recipients': 'user2@example.com'
        }
        result = lead.kw_find_responsible_user_by_email(msg_dict)
        self.assertEqual(result, self.user2.id)

    def test_kw_find_responsible_user_by_email_no_match(self):
        """Test finding responsible user with no matching emails"""
        lead = self.env['crm.lead']
        msg_dict = {
            'to': 'unknown1@example.com',
            'recipients': 'unknown2@example.com'
        }
        result = lead.kw_find_responsible_user_by_email(msg_dict)
        self.assertFalse(result)

    def test_kw_find_responsible_user_by_email_empty_fields(self):
        """Test finding responsible user with empty email fields"""
        lead = self.env['crm.lead']
        msg_dict = {
            'to': '',
            'recipients': ''
        }
        result = lead.kw_find_responsible_user_by_email(msg_dict)
        self.assertFalse(result)

    def test_kw_find_responsible_user_by_email_missing_fields(self):
        """Test finding responsible user with missing email fields"""
        lead = self.env['crm.lead']
        msg_dict = {}
        result = lead.kw_find_responsible_user_by_email(msg_dict)
        self.assertFalse(result)

    def test_message_new_with_user_assignment(self):
        """Test message_new method assigns user correctly"""
        msg_dict = {
            'subject': 'Test Lead Subject',
            'body': 'Test lead body',
            'from': 'customer@example.com',
            'to': 'user1@example.com',
            'message_id': '<test@example.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        self.assertEqual(lead.user_id, self.user1)
        self.assertEqual(lead.name, 'Test Lead Subject')

    def test_message_new_without_user_assignment(self):
        """Test message_new method without user assignment"""
        msg_dict = {
            'subject': 'Test Lead Subject',
            'body': 'Test lead body',
            'from': 'customer@example.com',
            'to': 'unknown@example.com',
            'message_id': '<test2@example.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        self.assertFalse(lead.user_id)
        self.assertEqual(lead.name, 'Test Lead Subject')

    def test_message_new_with_custom_values(self):
        """Test message_new method with custom values"""
        msg_dict = {
            'subject': 'Test Lead Subject',
            'body': 'Test lead body',
            'from': 'customer@example.com',
            'to': 'user2@example.com',
            'message_id': '<test3@example.com>',
        }

        custom_values = {
            'description': 'Custom description',
            'phone': '+1234567890'
        }

        lead = self.env['crm.lead'].message_new(msg_dict, custom_values)

        self.assertEqual(lead.user_id, self.user2)
        self.assertIn('Custom description', lead.description)
        self.assertEqual(lead.phone, '+1234567890')

    def test_message_new_priority_to_over_recipients(self):
        """Test that 'to' field has priority over 'recipients' field"""
        msg_dict = {
            'subject': 'Priority Test Lead',
            'body': 'Test lead body',
            'from': 'customer@example.com',
            'to': 'user1@example.com',
            'recipients': 'user2@example.com',
            'message_id': '<priority@example.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should assign user1 (from 'to' field) not user2 (from 'recipients')
        self.assertEqual(lead.user_id, self.user1)

    def test_message_new_fallback_to_recipients(self):
        """Test fallback to 'recipients' field when 'to' has no match"""
        msg_dict = {
            'subject': 'Fallback Test Lead',
            'body': 'Test lead body',
            'from': 'customer@example.com',
            'to': 'unknown@example.com',
            'recipients': 'user2@example.com, unknown2@example.com',
            'message_id': '<fallback@example.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should assign user2 from recipients field
        self.assertEqual(lead.user_id, self.user2)

    def test_message_new_with_cc_bcc_in_recipients(self):
        """Test with CC and BCC emails in recipients field"""
        msg_dict = {
            'subject': 'CC BCC Test Lead',
            'body': 'Test lead body',
            'from': 'customer@example.com',
            'to': 'sales@company.com',  # No matching user
            'recipients': ('sales@company.com, user1@example.com, '
                           'support@company.com'),
            'message_id': '<ccbcc@example.com>',
        }

        lead = self.env['crm.lead'].message_new(msg_dict)

        # Should find user1 in the recipients list
        self.assertEqual(lead.user_id, self.user1)

    def test_email_normalization(self):
        """Test that email normalization works correctly"""
        # Create user with lowercase email (Odoo normalizes login)
        user_lower = self.env['res.users'].create({
            'name': 'Lower Case User',
            'login': 'lower@example.com',
            'email': 'lower@example.com',
            'active': True,
        })

        lead = self.env['crm.lead']

        # Test with uppercase
        result = lead.kw_search_user_by_emails('LOWER@EXAMPLE.COM')
        self.assertEqual(result, user_lower)

        # Test with mixed case
        result = lead.kw_search_user_by_emails('Lower@Example.Com')
        self.assertEqual(result, user_lower)

    def test_multiple_emails_first_match_wins(self):
        """Test that the first matching email is returned"""
        lead = self.env['crm.lead']

        # Both users are in the email string, but user1 comes first
        result = lead.kw_search_user_by_emails(
            'user1@example.com, user2@example.com')
        self.assertEqual(result, self.user1)

        # Reverse order - user2 should be found first
        result = lead.kw_search_user_by_emails(
            'user2@example.com, user1@example.com')
        self.assertEqual(result, self.user2)

    def test_search_with_whitespace_and_formatting(self):
        """Test searching with various whitespace and formatting"""
        lead = self.env['crm.lead']

        # Test with extra whitespace
        result = lead.kw_search_user_by_emails('  user1@example.com  ')
        self.assertEqual(result, self.user1)

        # Test with mixed formatting
        result = lead.kw_search_user_by_emails(
            'unknown@example.com,   user2@example.com   , another@example.com')
        self.assertEqual(result, self.user2)
