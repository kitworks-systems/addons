from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        info = super().session_info()
        info["kw_hide_empty_groups"] = bool(
            request.env.user.kw_hide_empty_groups)
        return info
