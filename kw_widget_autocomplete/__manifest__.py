{
    'name': 'Widget Autocomplete',
    'summary': 'Universal autocomplete widget with multiple data sources.',
    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/addons',

    'category': 'Hidden/Tools',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',

    'depends': [
        'web',
    ],
    'assets': {
        'web.assets_backend': [
            (
                'kw_widget_autocomplete/static/src/js/sources/'
                'model_method_source.js'
            ),
            (
                'kw_widget_autocomplete/static/src/js/sources/'
                'domain_search_source.js'
            ),
            (
                'kw_widget_autocomplete/static/src/js/sources/'
                'json_endpoint_source.js'
            ),
            (
                'kw_widget_autocomplete/static/src/js/sources/'
                'rest_api_source.js'
            ),
            (
                'kw_widget_autocomplete/static/src/js/'
                'kw_autocomplete_field.js'
            ),
            (
                'kw_widget_autocomplete/static/src/xml/'
                'kw_autocomplete_templates.xml'
            ),
            'kw_widget_autocomplete/static/src/scss/kw_autocomplete.scss',
        ],
    },

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

}
