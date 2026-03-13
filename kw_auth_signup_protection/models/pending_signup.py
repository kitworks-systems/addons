import json
import logging
import secrets
import string

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

TOKEN_LENGTH = 20
TOKEN_ALPHABET = string.ascii_letters + string.digits


class KwPendingSignup(models.Model):
    _name = 'kw.pending.signup'
    _description = 'Pending Signup'
    _order = 'create_date desc'

    login = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    password = fields.Char(required=True)
    signup_values = fields.Text()
    lang = fields.Char()
    token = fields.Char(required=True, index=True)
    expiration = fields.Datetime(required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('expired', 'Expired'),
    ], default='pending', required=True, index=True)
    ip_address = fields.Char()
    last_sent = fields.Datetime()

    @api.model
    def create_pending(self, values, ip_address=None):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        hours = int(get_param(
            'kw_auth_signup_protection.token_expiration_hours', '24'))

        extra_values = {}
        base_keys = {'login', 'name', 'password', 'confirm_password',
                     'csrf_token', 'redirect', 'token', 'website_url',
                     'recaptcha_token_response'}
        for key, val in values.items():
            if key not in base_keys and val:
                extra_values[key] = val

        self.search([
            ('login', '=', values.get('login')),
            ('state', '=', 'pending'),
        ]).write({'state': 'expired'})

        return self.create({
            'login': values.get('login'),
            'name': values.get('name', ''),
            'password': values.get('password'),
            'signup_values': (
                json.dumps(extra_values) if extra_values else False),
            'lang': values.get('lang', ''),
            'token': self._generate_token(),
            'expiration': fields.Datetime.add(
                fields.Datetime.now(), hours=hours),
            'state': 'pending',
            'ip_address': ip_address or '',
            'last_sent': fields.Datetime.now(),
        })

    def verify(self):
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('This verification link has already been used.'))
        if self.expiration < fields.Datetime.now():
            self.state = 'expired'
            raise UserError(_(
                'This verification link has expired. '
                'Please sign up again.'))

        signup_vals = {
            'login': self.login,
            'name': self.name,
            'password': self.password,
        }
        if self.lang:
            signup_vals['lang'] = self.lang

        if self.signup_values:
            extra = json.loads(self.signup_values)
            signup_vals.update(extra)

        login, password = self.env['res.users'].sudo().signup(signup_vals)
        self.write({
            'state': 'verified',
            'password': '',
        })
        return login, password

    @api.model
    def _check_rate_limit(self, login, ip_address):
        one_hour_ago = fields.Datetime.subtract(
            fields.Datetime.now(), hours=1)

        email_count = self.search_count([
            ('login', '=', login),
            ('create_date', '>=', one_hour_ago),
        ])
        if email_count >= 3:
            raise UserError(_(
                'Too many signup attempts for this email. '
                'Please try again later.'))

        if ip_address:
            ip_count = self.search_count([
                ('ip_address', '=', ip_address),
                ('create_date', '>=', one_hour_ago),
            ])
            if ip_count >= 5:
                raise UserError(_(
                    'Too many signup attempts from your address. '
                    'Please try again later.'))

    @api.model
    def _generate_token(self):
        return ''.join(
            secrets.choice(TOKEN_ALPHABET) for _ in range(TOKEN_LENGTH))

    def _get_verification_url(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        return '%s/web/signup/verify?token=%s' % (base_url, self.token)

    @api.model
    def _cron_cleanup_expired(self):
        now = fields.Datetime.now()
        self.search([
            ('state', '=', 'pending'),
            ('expiration', '<', now),
        ]).write({'state': 'expired'})

        week_ago = fields.Datetime.subtract(now, days=7)
        self.search([
            ('state', 'in', ['expired', 'verified']),
            ('write_date', '<', week_ago),
        ]).unlink()
