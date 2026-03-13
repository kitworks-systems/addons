import json

from odoo import fields
from odoo.exceptions import UserError

from .common import TestSignupProtectionBase


class TestPendingSignup(TestSignupProtectionBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PendingSignup = cls.env['kw.pending.signup'].sudo()
        cls._set_param(cls, 'email_verification', 'True')
        cls._set_param(cls, 'token_expiration_hours', '24')

    def _create_pending(  # nosec B107
            self, login='test@example.com',
            name='Test User',
            password='TestPass123!',
            ip='127.0.0.1'):
        return self.PendingSignup.create_pending({
            'login': login,
            'name': name,
            'password': password,
        }, ip_address=ip)

    def test_create_pending(self):
        pending = self._create_pending()
        self.assertEqual(pending.state, 'pending')
        self.assertEqual(pending.login, 'test@example.com')
        self.assertEqual(pending.name, 'Test User')
        self.assertTrue(pending.token)
        self.assertEqual(len(pending.token), 20)
        self.assertTrue(
            pending.expiration > fields.Datetime.now())

    def test_verify_creates_user(self):
        pending = self._create_pending(
            login='verify_test@example.com')
        login, _password = pending.verify()
        self.assertEqual(login, 'verify_test@example.com')
        self.assertEqual(pending.state, 'verified')
        user = self.env['res.users'].sudo().search(
            [('login', '=', 'verify_test@example.com')])
        self.assertTrue(
            user, 'User should be created after verification')

    def test_expired_token_rejected(self):
        pending = self._create_pending(
            login='expired@example.com')
        pending.expiration = fields.Datetime.subtract(
            fields.Datetime.now(), hours=1)
        pending.flush_recordset()
        with self.assertRaises(UserError):
            pending.verify()

    def test_double_verify_rejected(self):
        pending = self._create_pending(
            login='double@example.com')
        pending.verify()
        with self.assertRaises(UserError):
            pending.verify()

    def test_rate_limit_email(self):
        for i in range(3):
            self._create_pending(
                login='ratelimit@example.com',
                ip='10.0.0.%d' % (i + 1))
        with self.assertRaises(UserError):
            self.PendingSignup._check_rate_limit(
                'ratelimit@example.com', '10.0.0.100')

    def test_rate_limit_ip(self):
        for i in range(5):
            self._create_pending(
                login='ip_test_%d@example.com' % i,
                ip='192.168.1.1')
        with self.assertRaises(UserError):
            self.PendingSignup._check_rate_limit(
                'new_email@example.com', '192.168.1.1')

    def test_duplicate_invalidation(self):
        first = self._create_pending(login='dup@example.com')
        self.assertEqual(first.state, 'pending')
        self._create_pending(login='dup@example.com')
        first.invalidate_recordset()
        self.assertEqual(first.state, 'expired')

    def test_extra_signup_values(self):
        pending = self.PendingSignup.create_pending({
            'login': 'extra@example.com',
            'name': 'Extra User',
            'password': 'TestPass123!',
            'kw_partner_first_name': 'John',
            'kw_partner_last_name': 'Doe',
        }, ip_address='127.0.0.1')
        self.assertTrue(pending.signup_values)
        extra = json.loads(pending.signup_values)
        self.assertEqual(
            extra.get('kw_partner_first_name'), 'John')
        self.assertEqual(
            extra.get('kw_partner_last_name'), 'Doe')

    def test_cron_marks_expired(self):
        pending = self._create_pending(
            login='cron_test@example.com')
        pending.expiration = fields.Datetime.subtract(
            fields.Datetime.now(), hours=25)
        pending.flush_recordset()
        self.PendingSignup._cron_cleanup_expired()
        pending.invalidate_recordset()
        self.assertEqual(pending.state, 'expired')

    def test_token_generation_uniqueness(self):
        tokens = set()
        for _i in range(100):
            tokens.add(self.PendingSignup._generate_token())
        self.assertEqual(
            len(tokens), 100, 'Tokens should be unique')

    def test_verification_url(self):
        pending = self._create_pending()
        url = pending._get_verification_url()
        self.assertIn('/web/signup/verify?token=', url)
        self.assertIn(pending.token, url)
