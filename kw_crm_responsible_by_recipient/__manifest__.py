{
    'name': 'CRM Auto Assign Responsible by Email',
    'summary': """
        Automatically assign responsible user based on email recipient.
        This module automatically assigns a responsible user to CRM leads
        created from incoming emails based on the email recipient.
    """,

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'CRM',
    'license': 'LGPL-3',
    'version': '15.0.1.0.1',

    'depends': [
        'crm',
    ],

    'data': [],

    'demo': [],

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
}
