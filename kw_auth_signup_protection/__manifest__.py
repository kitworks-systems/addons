{
    'name': 'Auth Signup Protection',
    'summary': 'Multi-layer signup protection: honeypot, reCAPTCHA, '
               'email verification, disposable email blocking',

    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/addons',

    'category': 'Hidden/Tools',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',

    'depends': [
        'auth_signup',
        'google_recaptcha',
    ],

    'external_dependencies': {'python': [], },

    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'data/mail_template_data.xml',
        'data/disposable_email_domains.xml',
        'views/auth_signup_templates.xml',
        'views/pending_signup_views.xml',
        'views/disposable_email_views.xml',
        'views/res_config_settings_views.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'kw_auth_signup_protection/static/src/scss/honeypot.scss',
            'kw_auth_signup_protection/static/src/js/signup.js',
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

    'price': 0,
    'currency': 'EUR',
}
