from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    kw_hide_empty_groups = fields.Boolean(
        string="Hide empty groups in grouped lists",
        default=False,
    )
