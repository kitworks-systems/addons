{
    'name': 'Test KW Widget Autocomplete',
    'summary': 'Test module for kw_widget_autocomplete widget.',
    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',
    'category': 'Hidden/Tests',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',
    'depends': [
        'base',
        'contacts',
        'product',
        'kw_widget_autocomplete',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/autocomplete_test_views.xml',
        'views/res_partner_views.xml',
        'views/menu.xml',
        'views/simple_test_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_tests': [
            'test_kw_widget_autocomplete/static/tests/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
