{
    'name': 'HTTP Request Log',
    'summary': 'Technical module, that may help to store and manage '
               'HTTP request logs',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'version': '18.0.0.4.8',

    'depends': [
        'generic_mixin',
        'kw_mixin',
    ],

    'external_dependencies': {
        'python': ['html2text', ],
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

    # wait for generic_mixin on 18.0
    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],


}
