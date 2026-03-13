from unittest.mock import patch
from odoo.tests import TransactionCase


class TestHtmlImage2AttachmentTool(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tool = cls.env['kw.html_image2attachment.tool']
        cls.test_model = cls.env['res.partner']
        cls.test_record = cls.test_model.create({'name': 'Test Partner'})
        cls.test_record._kw_html_image2attachment_fields = ['comment']

    def test_download_and_save_image(self):
        test_url = 'https://example.com/test.jpg'
        test_content = b'test_image_content'

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = test_content

            result = self.tool.download_and_save_image(
                test_url, self.test_record)

            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', self.test_record._name),
                ('res_id', '=', self.test_record.id),
                ('kw_is_html2attachment_image', '=', True),
            ])

            self.assertTrue(attachment)
            self.assertEqual(attachment.name, 'test.jpg')
            self.assertTrue(result.startswith('/web/image/'))

    def test_download_and_save_image_invalid_url(self):
        test_urls = [
            'https://nonexistent.example.com/image.jpg',
            'invalid_url',
            'http://example.com/not_image.txt',
        ]

        with patch('requests.get') as mock_get:
            # Test 404 error
            mock_get.return_value.status_code = 404
            result = self.tool.download_and_save_image(
                test_urls[0], self.test_record)
            self.assertFalse(result)

            # Test network error
            mock_get.side_effect = Exception('Network error')
            result = self.tool.download_and_save_image(
                test_urls[1], self.test_record)
            self.assertFalse(result)

            # Test non-image content
            mock_get.side_effect = None
            mock_get.return_value.status_code = 200
            mock_get.return_value.headers = {'content-type': 'text/plain'}
            mock_get.return_value.content = b'not an image'
            result = self.tool.download_and_save_image(
                test_urls[2], self.test_record)
            self.assertFalse(result)

    def test_save_base_64_image(self):
        test_image = (
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8'
            'z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
        )

        result = self.tool.save_base_64_image(test_image, self.test_record)

        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', self.test_record._name),
            ('res_id', '=', self.test_record.id),
            ('kw_is_html2attachment_image', '=', True),
        ])

        self.assertTrue(attachment)
        self.assertEqual(attachment.mimetype, 'image/png')
        self.assertTrue(result.startswith('/web/image/'))

    def test_save_base64_image_invalid_data(self):
        test_cases = [
            '',  # Empty string
            'invalid base64',  # Invalid base64
            (
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42'
                'mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
                'invalid'),  # Corrupted base64
            'dGVzdA==',  # Valid base64 but not an image
        ]

        for test_data in test_cases:
            result = self.tool.save_base_64_image(test_data, self.test_record)
            self.assertFalse(result)

    def test_process_images_in_html(self):
        html_content = '''
            <p>Test content with images:</p>
            <img src="https://example.com/test1.jpg">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA'
            'BCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJg'
            'gg==">
        '''

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b'test_image_content'

            result = self.tool.process_images_in_html(
                html_content, self.test_record)

            self.assertNotIn('https://example.com/test1.jpg', result)
            self.assertNotIn('data:image/png;base64,', result)
            self.assertIn('/web/image/', result)

    def test_process_images_in_html_invalid_data(self):
        test_cases = [
            '',  # Empty HTML
            '<p>No images</p>',  # HTML without images
            '<img>',  # Image without src
            '<img src="">',  # Empty src
            '<img src="invalid_url">',  # Invalid URL
            '<img src="data:image/png;base64,invalid">',  # Invalid base64
            '<img src="data:text/plain;base64,dGVzdA==">',  # Non-image base64
            '<not_valid_html',  # Invalid HTML
        ]

        for html_content in test_cases:
            result = self.tool.process_images_in_html(
                html_content, self.test_record)
            if not html_content:
                self.assertEqual(result, '')
            else:
                self.assertEqual(result, html_content)

    def test_clean_unused_images(self):
        # Create test attachments
        attachment1 = self.env['ir.attachment'].create({
            'name': 'test1.jpg',
            'type': 'binary',
            'datas': 'test',
            'res_model': self.test_record._name,
            'res_id': self.test_record.id,
            'kw_is_html2attachment_image': True,
        })
        attachment2 = self.env['ir.attachment'].create({
            'name': 'test2.jpg',
            'type': 'binary',
            'datas': 'test',
            'res_model': self.test_record._name,
            'res_id': self.test_record.id,
            'kw_is_html2attachment_image': True,
        })

        # Set HTML content that references only one attachment
        self.test_record.comment = f'<img src="/web/image/{attachment1.id}">'

        self.tool.clean_unused_images(self.test_record)

        # Check that only referenced attachment exists
        self.assertTrue(attachment1.exists())
        self.assertFalse(attachment2.exists())

    def test_mark_attachments(self):
        # Create test attachments
        attachment = self.env['ir.attachment'].create({
            'name': 'test.jpg',
            'type': 'binary',
            'datas': 'test',
            'res_model': self.test_record._name,
            'res_id': self.test_record.id,
        })

        # Set HTML content with attachment reference
        self.test_record.comment = f'<img src="/web/image/{attachment.id}">'

        self.tool.mark_attachments(self.test_record)

        self.assertTrue(attachment.kw_is_html2attachment_image)
