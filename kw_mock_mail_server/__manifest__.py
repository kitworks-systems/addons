{
    'name': 'Mock Mail Server',
    'summary': """
        This module provides tools to test incoming email processing in Odoo.
        It can emulate receiving emails and create test scenarios for:
        - Lead creation from emails
        - User assignment based on email recipients
        - Email routing and processing
    """,

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'version': '16.0.1.0.1',

    'depends': [
        'mail',
    ],

    'data': [
        'security/ir.model.access.csv',

        'data/data.xml',

        'views/fetchmail_views.xml',
        'views/mock_email_views.xml',
    ],

    'demo': [
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

}
