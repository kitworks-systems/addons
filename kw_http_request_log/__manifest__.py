{
    'name': 'HTTP Request Log',
    'summary': 'Technical module, that may help to store and manage '
               'HTTP request logs',

    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/addons',

    'category': 'Hidden/Tools',
    'license': 'LGPL-3',
    'version': '19.0.0.5.1',

    'depends': [
        'generic_mixin',
        'kw_mixin',
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [
        'security/ir.model.access.csv',

        'data/ir_cron.xml',

        'views/http_request_log_views.xml',
        'views/http_request_log_source_views.xml',
    ],
    'demo': [
        'demo/http_request_source_demo.xml',
        'demo/http_request_log_demo.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/icon.png',
    ],


}
