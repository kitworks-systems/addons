import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Task(models.Model):
    _name = 'kw.html_image2attachment.task'
    _description = 'HTML Image to Attachment Task'

    name = fields.Char(
        required=True,
        help='Task name for identification',
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        help='Model containing HTML fields with images to process',
    )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='HTML Field',
        required=True,
        domain="[('model_id', '=', model_id), ('ttype', '=', 'html')]",
        ondelete='cascade',
        help='HTML field containing images that need to be '
             'converted to attachments',
    )
    line_ids = fields.One2many(
        comodel_name='kw.html_image2attachment.task.line',
        inverse_name='task_id',
        string='Lines',
        help='List of records to process',
    )

    def action_create_lines(self):
        """Create lines for all records in the model."""
        self.env['kw.html_image2attachment.task.line'].create([
            {'res_id': x, 'task_id': self.id} for x in self.env[
                self.model_id.model].search([]).mapped('id')])

    def action_clear_lines(self):
        """Clear all lines."""
        self.line_ids.unlink()
