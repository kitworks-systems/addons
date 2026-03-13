from odoo import fields, models


class KwDisposableEmailDomain(models.Model):
    _name = 'kw.disposable.email.domain'
    _description = 'Disposable Email Domain'
    _order = 'name'

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)',
         'This domain already exists in the list.'),
    ]
