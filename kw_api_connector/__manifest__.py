{
    'name': 'API connector',
    'summary': 'Technical module, that may help to create API connector',

    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/addons',

    'category': 'Hidden/Tools',
    'license': 'LGPL-3',
    'version': '18.0.0.6.2',

    'depends': [
        'kw_http_request_log',
    ],

    'external_dependencies': {
        'python': [],
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
