from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    kw_signup_recaptcha_enabled = fields.Boolean(
        string='Enable reCAPTCHA on Signup',
        config_parameter='kw_auth_signup_protection.recaptcha_enabled',
    )
    kw_signup_email_verification = fields.Boolean(
        string='Enable Email Verification on Signup',
        config_parameter='kw_auth_signup_protection.email_verification',
    )
    kw_signup_honeypot_enabled = fields.Boolean(
        string='Enable Honeypot on Signup',
        config_parameter='kw_auth_signup_protection.honeypot_enabled',
    )
    kw_signup_disposable_email_block = fields.Boolean(
        string='Block Disposable Email Domains',
        config_parameter='kw_auth_signup_protection.disposable_email_block',
    )
    kw_signup_token_expiration_hours = fields.Integer(
        string='Verification Token Expiration (hours)',
        config_parameter='kw_auth_signup_protection.token_expiration_hours',
        default=24,
    )
