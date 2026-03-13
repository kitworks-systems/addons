import logging

from odoo import _, http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class KwAuthSignupProtection(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public',
                website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if 'error' not in qcontext \
                and request.httprequest.method == 'POST':
            error = self._kw_check_signup_protection(qcontext)
            if error:
                qcontext['error'] = error
                return self._kw_render_signup(qcontext)

            if self._kw_is_email_verification_enabled() \
                    and not qcontext.get('token'):
                return self._kw_handle_email_verification(
                    qcontext)

        return super().web_auth_signup(*args, **kw)

    @http.route('/web/signup/verify', type='http', auth='public',
                website=True, sitemap=False)
    def web_auth_signup_verify(self, token=None, **kw):
        if not token:
            return request.redirect('/web/login')

        pending = request.env['kw.pending.signup'].sudo().search([
            ('token', '=', token),
            ('state', '=', 'pending'),
        ], limit=1)

        if not pending:
            return request.render(
                'kw_auth_signup_protection.verify_result', {
                    'error': _(
                        'Invalid or expired verification link. '
                        'Please sign up again.'),
                })

        try:
            login, password = pending.verify()
            request.env.cr.commit()
            pre_uid = request.session.authenticate(
                request.db, login, password)
            if not pre_uid:
                return request.render(
                    'kw_auth_signup_protection.verify_result', {
                        'error': _(
                            'Authentication failed '
                            'after verification.'),
                    })
            return request.redirect('/web')
        except UserError as exc:
            return request.render(
                'kw_auth_signup_protection.verify_result',
                {'error': exc.args[0]})
        except Exception:
            _logger.exception('Error during signup verification')
            return request.render(
                'kw_auth_signup_protection.verify_result', {
                    'error': _(
                        'An error occurred during verification.'
                        ' Please try again.'),
                })

    @staticmethod
    def _kw_render_signup(qcontext):
        response = request.render(
            'auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = \
            "frame-ancestors 'self'"
        return response

    def _kw_check_signup_protection(self, qcontext):
        get_param = request.env[
            'ir.config_parameter'].sudo().get_param

        if get_param(
                'kw_auth_signup_protection.honeypot_enabled'
        ) == 'True':
            if request.params.get('website_url'):
                _logger.info(
                    'Honeypot triggered from IP %s',
                    request.httprequest.remote_addr)
                return _('Signup failed. Please try again.')

        if get_param(
                'kw_auth_signup_protection.recaptcha_enabled'
        ) == 'True':
            try:
                ir_http = request.env['ir.http']
                result = ir_http \
                    ._verify_request_recaptcha_token('signup')
                if not result:
                    return _(
                        'reCAPTCHA verification failed. '
                        'Please try again.')
            except UserError as exc:
                return exc.args[0]
            except Exception:
                _logger.exception(
                    'reCAPTCHA verification error')
                return _(
                    'reCAPTCHA verification error. '
                    'Please try again.')

        if get_param(
                'kw_auth_signup_protection.'
                'disposable_email_block') == 'True':
            login = qcontext.get('login', '')
            if '@' in login:
                domain = login.split('@')[-1].lower()
                DisposableDomain = request.env[
                    'kw.disposable.email.domain'].sudo()
                if DisposableDomain.search(
                        [('name', '=', domain)], limit=1):
                    return _(
                        'Registration with disposable email '
                        'addresses is not allowed.')

        return None

    @staticmethod
    def _kw_is_email_verification_enabled():
        return request.env[
            'ir.config_parameter'].sudo().get_param(
            'kw_auth_signup_protection.email_verification'
        ) == 'True'

    def _kw_handle_email_verification(self, qcontext):
        login = qcontext.get('login', '')
        password = qcontext.get('password', '')
        name = qcontext.get('name', '')

        if not login or not password or not name:
            qcontext['error'] = _(
                'The form was not properly filled in.')
            return self._kw_render_signup(qcontext)

        if password != qcontext.get('confirm_password', ''):
            qcontext['error'] = _(
                'Passwords do not match; please retype them.')
            return self._kw_render_signup(qcontext)

        if request.env['res.users'].sudo().search(
                [('login', '=', login)], limit=1):
            qcontext['error'] = _(
                'Another user is already registered '
                'using this email address.')
            return self._kw_render_signup(qcontext)

        PendingSignup = request.env['kw.pending.signup'].sudo()
        ip_address = request.httprequest.remote_addr
        try:
            PendingSignup._check_rate_limit(
                login, ip_address)
        except UserError as exc:
            qcontext['error'] = exc.args[0]
            return self._kw_render_signup(qcontext)

        all_values = dict(request.params)
        lang_codes = [
            code for code, _ in
            request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in lang_codes:
            all_values['lang'] = lang

        pending = PendingSignup.create_pending(
            all_values, ip_address)

        template = request.env.ref(
            'kw_auth_signup_protection.'
            'mail_template_signup_verification',
            raise_if_not_found=False)
        if template:
            template.sudo().send_mail(
                pending.id, force_send=True)

        msg_qcontext = {
            'message': _(
                'A verification email has been sent to %s. '
                'Please check your inbox and click the link '
                'to complete your registration.', login),
        }
        response = request.render(
            'kw_auth_signup_protection.signup_verify_sent',
            msg_qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = \
            "frame-ancestors 'self'"
        return response
