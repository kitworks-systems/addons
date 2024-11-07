{
    'name': 'API connector',
    'summary': 'Technical module, that may help to create API connector',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Extra Tools',
    'license': 'LGPL-3',

    'version': '18.0.0.4.2',

    'depends': [
        'kw_http_request_log',
    ],

    'external_dependencies': {
        'python': ['html2text', ],
    },

    'data': [
        'security/ir.model.access.csv',
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
