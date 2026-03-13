from .common import TestSignupProtectionBase


class TestDisposableEmail(TestSignupProtectionBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._set_param(cls, 'disposable_email_block', 'True')
        cls.DisposableDomain = cls.env[
            'kw.disposable.email.domain'].sudo()

    def test_mailinator_in_list(self):
        domain = self.DisposableDomain.search(
            [('name', '=', 'mailinator.com')], limit=1)
        self.assertTrue(domain, 'mailinator.com should be in list')

    def test_guerrillamail_in_list(self):
        domain = self.DisposableDomain.search(
            [('name', '=', 'guerrillamail.com')], limit=1)
        self.assertTrue(
            domain, 'guerrillamail.com should be in list')

    def test_normal_domain_not_blocked(self):
        domain = self.DisposableDomain.search(
            [('name', '=', 'gmail.com')], limit=1)
        self.assertFalse(
            domain, 'gmail.com should not be in the list')

    def test_domain_create_and_search(self):
        self.DisposableDomain.create(
            {'name': 'custom-test-disposable.com'})
        found = self.DisposableDomain.search(
            [('name', '=', 'custom-test-disposable.com')],
            limit=1)
        self.assertTrue(found)

    def test_domain_archive(self):
        domain = self.DisposableDomain.search(
            [('name', '=', 'yopmail.com')], limit=1)
        self.assertTrue(domain)
        domain.active = False
        archived = self.DisposableDomain.search(
            [('name', '=', 'yopmail.com')], limit=1)
        self.assertFalse(
            archived,
            'Archived domain should not be found')
        domain.active = True
