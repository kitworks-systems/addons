from odoo import http
from odoo.tests.common import (
    get_db_name, HOST, HttpCase, Opener, tagged,
)


@tagged('-at_install', 'post_install')
class TestHoneypot(HttpCase):

    def setUp(self):
        super().setUp()
        self.ICP = self.env['ir.config_parameter'].sudo()
        self.ICP.set_param(
            'auth_signup.invitation_scope', 'b2c')
        self.ICP.set_param(
            'kw_auth_signup_protection.honeypot_enabled',
            'True')
        self.ICP.set_param(
            'kw_auth_signup_protection.email_verification',
            'False')
        self.ICP.set_param(
            'kw_auth_signup_protection.recaptcha_enabled',
            'False')
        self.ICP.set_param(
            'kw_auth_signup_protection.disposable_email_block',
            'False')

    def _setup_session(self):
        self.session = http.root.session_store.new()
        self.session.update(
            http.get_default_session(), db=get_db_name())
        self.opener = Opener(self.env.cr)
        self.opener.cookies.set(
            'session_id', self.session.sid,
            domain=HOST, path='/')

    def _post_signup(self, data):
        self._setup_session()
        data['csrf_token'] = http.Request.csrf_token(self)
        return self.url_open('/web/signup', data=data)

    def test_honeypot_empty_passes(self):
        res = self._post_signup({
            'login': 'honeypot_pass@example.com',
            'name': 'Test User',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'website_url': '',
        })
        self.assertNotIn(
            'Signup failed', res.text,
            'Empty honeypot should not trigger rejection')

    def test_honeypot_filled_rejected(self):
        res = self._post_signup({
            'login': 'honeypot_bot@example.com',
            'name': 'Bot User',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'website_url': 'http://spam.example.com',
        })
        self.assertIn(
            'Signup failed', res.text,
            'Filled honeypot should trigger rejection')
        user = self.env['res.users'].sudo().search(
            [('login', '=', 'honeypot_bot@example.com')])
        self.assertFalse(
            user, 'User should not be created for bot')

    def test_honeypot_disabled_skips(self):
        self.ICP.set_param(
            'kw_auth_signup_protection.honeypot_enabled',
            'False')
        res = self._post_signup({
            'login': 'honeypot_disabled@example.com',
            'name': 'Test User',
            'password': 'TestPass123!',
            'confirm_password': 'TestPass123!',
            'website_url': 'http://spam.example.com',
        })
        self.assertNotIn(
            'Signup failed', res.text,
            'Disabled honeypot should not reject')
