from odoo.tests.common import TransactionCase


class TestSignupProtectionBase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ICP = cls.env['ir.config_parameter'].sudo()

    def _set_param(self, key, value):
        self.ICP.set_param(
            'kw_auth_signup_protection.%s' % key, value)
