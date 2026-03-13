import base64
import logging
import re

import requests

from odoo import models, api

_logger = logging.getLogger(__name__)


class HtmlImage2AttachmentTool(models.AbstractModel):
    _name = 'kw.html_image2attachment.tool'
    _description = 'Html Image to Attachment Tool'

    def download_and_save_image(self, url, record):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise error for non-200 status codes
            if response.status_code == 200:
                image_data = response.content
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                image_name = url.split('/')[-1]
                if not image_name or image_name.count('.') == 0:
                    image_name = 'image.png'
                attachment = self.env['ir.attachment'].create({
                    'name': image_name,
                    'type': 'binary',
                    'datas': image_base64,
                    'res_model': record._name,
                    'res_id': record.id,
                    'kw_is_html2attachment_image': True,
                })
                return f'/web/image/{attachment.id}'
        except requests.exceptions.RequestException as e:
            _logger.debug(e)
            raise ValueError(str(e))
        return url

    def save_base_64_image(self, image_data, record):
        try:
            # Validate base64
            base64.b64decode(image_data)
            mimetype = self.env['ir.attachment']._compute_mimetype(
                {'datas': image_data})
            extension = mimetype.split('/')[-1]
            attachment = self.env['ir.attachment'].create({
                'name': f'pasted_image.{extension}',
                'type': 'binary',
                'datas': image_data,
                'res_model': record._name,
                'res_id': record.id,
                'kw_is_html2attachment_image': True,
                'mimetype': mimetype,
            })
            return f'/web/image/{attachment.id}'
        except Exception as e:
            _logger.debug(e)
            raise ValueError(f'Invalid base64 image: {str(e)}')

    def process_images_in_html(self, html_content, record):
        if not html_content:
            return html_content

        external_image_urls = re.findall(
            r'<img.*?src="(https?://.*?)"', html_content)

        for url in external_image_urls:
            local_url = self.download_and_save_image(url, record)
            if local_url != url:
                html_content = html_content.replace(
                    f'src="{url}"', f'src="{local_url}"')

        base64_images = re.findall(
            r'src="data:image/[^;]+;base64,([^"]+)"', html_content)

        for image_data in base64_images:
            local_url = self.save_base_64_image(image_data, record)
            pattern = rf'src="data:image/[^;]+;base64,{re.escape(image_data)}"'
            html_content = re.sub(pattern, f'src="{local_url}"', html_content)

        return html_content

    def clean_unused_images(self, record, fields=None):
        if not fields and hasattr(record, '_kw_html_image2attachment_fields'):
            fields = record._kw_html_image2attachment_fields

        if not fields:
            return

        used_image_ids = set()
        for field in fields:
            if not hasattr(record, field):
                continue

            html_content = getattr(record, field)
            if not html_content:
                continue

            used_image_ids.update(re.findall(
                r'/web/image/(\d+)', html_content))

        if not used_image_ids:
            return

        image_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', record._name),
            ('res_id', '=', record.id),
            ('kw_is_html2attachment_image', '=', True),
            ('id', 'not in', list(map(int, used_image_ids))),
        ])

        if image_attachments:
            image_attachments.unlink()

    def mark_attachments(self, record, fields=None):
        if not fields and hasattr(record, '_kw_html_image2attachment_fields'):
            fields = record._kw_html_image2attachment_fields

        if not fields:
            return False

        attachment_ids = set()
        for field in fields:
            if not hasattr(record, field):
                continue

            html_content = getattr(record, field)
            if not html_content:
                continue

            attachment_ids.update(re.findall(
                r'/web/image/(\d+)', html_content))

        if attachment_ids:
            self.env['ir.attachment'].browse(
                map(int, attachment_ids)).write({
                    'kw_is_html2attachment_image': True,
                })

        return True


class HtmlImage2AttachmentMixin(models.AbstractModel):
    _name = 'kw.html_image2attachment.mixin'
    _description = 'Html Image to Attachment Mixin'

    _kw_html_image2attachment_fields = []

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        tool = self.env['kw.html_image2attachment.tool']

        for record, vals in zip(records, vals_list):
            for field in self._kw_html_image2attachment_fields:
                if field not in vals:
                    continue

                processed_html = tool.process_images_in_html(
                    vals[field], record)
                if processed_html != vals[field]:
                    record.write({field: processed_html})
                tool.mark_attachments(record)
                tool.clean_unused_images(record)

        return records

    def write(self, vals):
        fields_to_process = set(vals.keys()) & set(
            self._kw_html_image2attachment_fields)

        if fields_to_process:
            tool = self.env['kw.html_image2attachment.tool']
            for record in self:
                for field in fields_to_process:
                    vals[field] = tool.process_images_in_html(
                        vals[field], record)
                tool.mark_attachments(record)
                tool.clean_unused_images(record)

        return super().write(vals)
