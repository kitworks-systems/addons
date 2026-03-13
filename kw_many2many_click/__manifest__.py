{
    'name': 'Many2many Clickable Records',
    'author': 'Kitworks Systems',
    'license': 'OPL-1',
    'website': 'https://kitworks.systems/',
    'images': [],
    'version': '18.0.1.1.0',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'kw_many2many_click/static/src/views/**/*.js',
            'kw_many2many_click/static/src/views/**/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
}
