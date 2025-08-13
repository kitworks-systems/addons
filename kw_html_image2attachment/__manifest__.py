{
    'name': 'HTML Image to Attachment',
    'summary': 'Convert images from HTML fields to attachments',
    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '18.0.1.2.1',

    'depends': [
        'base',
    ],

    'external_dependencies': {
        'python': [
            'requests',
        ],
    },

    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/task_views.xml',
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

    'price': 0,
    'currency': 'EUR',
}
