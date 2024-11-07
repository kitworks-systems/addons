{
    'name': 'Test API connector',
    'summary': 'Technical module that have to be used to test'
               ' API connector module',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Extra Tools',
    'license': 'LGPL-3',

    'version': '18.0.0.2.3',

    'depends': [
        'kw_api_connector',
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [
        'security/ir.model.access.csv',

        'views/test_kw_api_credential_views.xml',

        'data/test_kw_api_connector.xml',
    ],
    'demo': [
        'demo/test_kw_api_connector_demo.xml',
        'demo/kw_http_request_log_source_demo.xml',
        'demo/test_kw_api_credential_demo.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],


}
