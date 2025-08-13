import logging
import re
# pylint: disable=missing-manifest-dependency
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class TaskLine(models.Model):
    _name = 'kw.html_image2attachment.task.line'
    _description = 'HTML Image to Attachment Task Line'

    task_id = fields.Many2one(
        comodel_name='kw.html_image2attachment.task',
        string='Task',
        required=True,
        ondelete='cascade',
        help='Reference to the parent task',
    )
    res_name = fields.Char(
        string='Resource Name',
        compute='_compute_res_name',
        help='Display name of the record being processed',
    )
    res_model = fields.Char(
        string='Resource Model',
        related='task_id.model_id.model',
        help='Technical name of the model being processed',
    )
    res_field = fields.Char(
        string='Resource Field',
        related='task_id.field_id.name',
        help='Technical name of the HTML field being processed',
    )
    res_id = fields.Many2oneReference(
        string='Resource ID',
        model_field='res_model',
        readonly=True,
        help='ID of the record being processed',
    )
    state = fields.Selection(
        selection=[('new', 'New'), ('success', 'Success'), ('error', 'Error')],
        default='new',
        readonly=True,
        help='Processing status: New (not processed), '
             'Success (processed successfully), '
             'Error (processing failed)',
    )
    result = fields.Text(
        readonly=True,
        help='Processing result: list of processed images or error message',
    )

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for obj in self:
            if obj.res_model and obj.res_id:
                record = self.env[obj.res_model].browse(obj.res_id)
                obj.res_name = record.display_name
            else:
                obj.res_name = False

    def action_process(self):
        for obj in self:
            obj.process_line()

    def process_line(self):
        self.ensure_one()
        if not self.res_id:
            self.write({'state': 'error', 'result': 'No res_id'})
            return

        record = self.env[self.res_model].browse(self.res_id)
        if not record.exists():
            self.write({'state': 'error', 'result': 'Record not found'})
            return

        if not self.res_field or not hasattr(record, self.res_field):
            self.write({'state': 'error', 'result': 'Field not found'})
            return

        html = getattr(record, self.res_field)
        if not html:
            self.write({'state': 'success', 'result': '[]'})
            return

        if not re.search(r'<img.*?src=', html):
            self.write({'state': 'success', 'result': 'No image for process'})
            return

        tool = self.env['kw.html_image2attachment.tool']
        try:
            tool.mark_attachments(record, [self.res_field])
            processed_html = tool.process_images_in_html(html, record)
            if processed_html != html:
                record.write({self.res_field: processed_html})
                tool.clean_unused_images(record, [self.res_field])
                processed_images = [
                    img_id for img_id in re.findall(
                        r'/web/image/(\d+)', processed_html)
                ]
                self.write({
                    'state': 'success',
                    'result': 'Processed images:\n{}'.format(
                        '\n'.join(processed_images)),
                })
            else:
                self.write({
                    'state': 'success',
                    'result': 'No changes needed',
                })
        except Exception as e:
            self.write({
                'state': 'error',
                'result': str(e),
            })
