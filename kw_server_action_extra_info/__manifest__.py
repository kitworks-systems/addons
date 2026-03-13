{
    'name': 'Server Action Extra Info',
    'summary': 'Restore Server Action field mapping and security features '
               'removed in Odoo 17\n'
               'This module add`s page \'Data to Write\', '
               'to the step \'Run Server Action\' how it was in version 16',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Technical',
    'license': 'LGPL-3',
    'version': '17.0.1.0.0',

    'depends': [
        'base',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/ir_action_view.xml',
    ],

    'installable': True,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

}
