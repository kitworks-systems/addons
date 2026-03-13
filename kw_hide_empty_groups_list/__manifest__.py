{
    'name': 'Hide Empty Groups in Grouped Lists',
    'summary': 'Hide empty groups in grouped list views '
               'using js_class kw_filtered_grouped_list',
    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',
    'depends': ['web', 'base'],
    'data': [
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kw_hide_empty_groups_list/static/src/js/filtered_groups_patch.js',
        ],
    },
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
