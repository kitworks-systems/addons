from unittest.mock import patch
from odoo.tests.common import TransactionCase


class TestHtmlImage2AttachmentMixin(TransactionCase):

    def test_100_create_with_external_image(self):
        test_url = 'https://example.com/test.jpg'
        test_content = b'test_image_content'
        html_content = f'<p>Test with image: <img src="{test_url}"></p>'

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = test_content

            record = self.env['test.html_image2attachment'].create({
                'name': 'Test Record',
                'description': html_content,
            })
            record.env.cr.flush()
            record.env.invalidate_all()

            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
                ('kw_is_html2attachment_image', '=', True),
            ])

            self.assertTrue(attachment)
            self.assertEqual(attachment.name, 'test.jpg')
            self.assertIn(f'/web/image/{attachment.id}', record.description)

    def test_110_create_with_base64_image(self):
        test_image = (
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8'
            'z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==')
        html_content = f'''
            <p>Test with base64 image:</p>
            <img src="data:image/png;base64,{test_image}">
        '''

        record = self.env['test.html_image2attachment'].create({
            'name': 'Test Record',
            'description': html_content,
        })
        record.env.cr.flush()
        record.env.invalidate_all()

        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', record._name),
            ('res_id', '=', record.id),
            ('kw_is_html2attachment_image', '=', True),
        ])

        self.assertTrue(attachment)
        self.assertEqual(attachment.mimetype, 'image/png')
        self.assertIn(f'/web/image/{attachment.id}', record.description)

    def test_200_write_with_external_image(self):
        record = self.env['test.html_image2attachment'].create({
            'name': 'Test Record',
            'description': '<p>Initial content</p>',
        })

        test_url = 'https://example.com/test.jpg'
        test_content = b'test_image_content'
        html_content = f'<p>Updated with image: <img src="{test_url}"></p>'

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = test_content

            record.write({'description': html_content})
            record.env.cr.flush()
            record.env.invalidate_all()

            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
                ('kw_is_html2attachment_image', '=', True),
            ])

            self.assertTrue(attachment)
            self.assertEqual(attachment.name, 'test.jpg')
            self.assertIn(f'/web/image/{attachment.id}', record.description)

    def test_210_write_multiple_fields(self):
        record = self.env['test.html_image2attachment'].create({
            'name': 'Test Record',
            'description': '<p>Initial description</p>',
            'note': '<p>Initial note</p>',
        })

        test_url1 = 'https://example.com/test1.jpg'
        test_url2 = 'https://example.com/test2.jpg'
        test_content = b'test_image_content'

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = test_content

            record.write({
                'description': f'<p><img src="{test_url1}"></p>',
                'note': f'<p><img src="{test_url2}"></p>',
            })
            record.env.cr.flush()
            record.env.invalidate_all()

            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
                ('kw_is_html2attachment_image', '=', True),
            ])

            self.assertEqual(len(attachments), 2)
            self.assertEqual(
                len([a for a in attachments if a.name == 'test1.jpg']), 1)
            self.assertEqual(
                len([a for a in attachments if a.name == 'test2.jpg']), 1)

    def test_300_clean_unused_images(self):
        record = self.env['test.html_image2attachment'].create({
            'name': 'Test Record',
            'description': '<p>Initial content</p>',
        })

        # Create unused attachment
        unused_attachment = self.env['ir.attachment'].create({
            'name': 'unused.jpg',
            'type': 'binary',
            'datas': 'test',
            'res_model': record._name,
            'res_id': record.id,
            'kw_is_html2attachment_image': True,
        })

        # Create and use another attachment
        test_url = 'https://example.com/test.jpg'
        test_content = b'test_image_content'
        html_content = f'<p>Updated with image: <img src="{test_url}"></p>'

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = test_content

            record.write({'description': html_content})
            record.env.cr.flush()
            record.env.invalidate_all()
            tool = self.env['kw.html_image2attachment.tool']
            tool.clean_unused_images(record)

            # Check that unused attachment was deleted
            self.assertFalse(unused_attachment.exists())

            # Check that used attachment still exists
            used_attachment = self.env['ir.attachment'].search([
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
                ('kw_is_html2attachment_image', '=', True),
            ])
            self.assertTrue(used_attachment)

    def test_400_mark_attachments(self):
        record = self.env['test.html_image2attachment'].create({
            'name': 'Test Record',
            'description': '<p>Initial content</p>',
        })

        # Create attachment without mark
        attachment = self.env['ir.attachment'].create({
            'name': 'test.jpg',
            'type': 'binary',
            'datas': 'test',
            'res_model': record._name,
            'res_id': record.id,
        })

        # Update content to use attachment
        html_content = f'<p>With image: <img src="/web/image/' \
                       f'{attachment.id}"></p>'
        record.write({'description': html_content})
        record.env.cr.flush()
        record.env.invalidate_all()
        tool = self.env['kw.html_image2attachment.tool']
        tool.mark_attachments(record)
        # Check that attachment was marked
        self.assertTrue(attachment.kw_is_html2attachment_image)
