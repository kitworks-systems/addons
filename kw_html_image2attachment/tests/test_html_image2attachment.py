from unittest.mock import patch

import requests
from requests.exceptions import HTTPError

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestHtmlImage2Attachment(TransactionCase):
    """Test HTML Image to Attachment functionality."""

    @staticmethod
    def fake_get(url, *args, **kwargs):
        """Fake function to simulate an external HTTP request."""
        if url == "http://example.com/image.png":
            raise HTTPError("404 Client Error: Not Found for url: " + url)
        # Get timeout from kwargs or default to 5 seconds
        timeout = kwargs.pop('timeout', 5)
        return requests.get(url, *args, timeout=timeout, **kwargs)

    def setUp(self):
        """Set up test data."""
        super().setUp()

        # Create test task
        self.test_task = self.env['kw.html_image2attachment.task'].create({
            'name': 'Test Task',
            'model_id': self.env.ref('base.model_res_partner').id,
            'field_id': self.env.ref('base.field_res_partner__comment').id,
        })

        # Create test partner with base64 image
        self.test_partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'comment': (
                '<p>Test content with image: '
                '<img src="data:image/png;base64,'
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8'
                'z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="/></p>'
            ),
        })

    def test_01_create_lines(self):
        """Test creating task lines."""
        self.test_task.action_create_lines()
        line = self.test_task.line_ids.filtered(
            lambda line: line.res_id == self.test_partner.id)
        self.assertEqual(len(line), 1)

    def test_02_process_lines(self):
        """Test processing task lines."""
        self.test_task.action_clear_lines()
        self.test_task.action_create_lines()
        line = self.env['kw.html_image2attachment.task.line'].search([
            ('res_id', '=', self.test_partner.id)], limit=1)
        line.action_process()
        self.assertEqual(line.state, 'success')
        self.assertIn('Processed images:', line.result)

    def test_03_clear_lines(self):
        """Test clearing task lines."""
        self.test_task.action_create_lines()
        self.test_task.action_clear_lines()
        self.assertEqual(len(self.test_task.line_ids), 0)

    def test_04_external_image(self):
        """Test processing external image."""
        # Create test partner with external image
        partner = self.env['res.partner'].create({
            'name': 'Test Partner External',
            'comment': (
                '<p>Test content with external image: '
                '<img src="http://example.com/image.png"/></p>'
            ),
        })

        with patch(
            'requests.get',
            side_effect=TestHtmlImage2Attachment.fake_get
        ):
            self.test_task.action_create_lines()
            line = self.test_task.line_ids.filtered(
                lambda line: line.res_id == partner.id)
            line.action_process()
            self.assertEqual(line.state, 'error')
            self.assertIn('404 Client Error: Not Found for url:', line.result)

    def test_05_invalid_base64(self):
        """Test processing invalid base64 image."""
        # Create test partner with invalid base64 image
        partner = self.env['res.partner'].create({
            'name': 'Test Partner Invalid',
            'comment': (
                '<p>Test content with invalid base64 image: '
                '<img src="data:image/png;base64,invalid"/></p>'
            ),
        })

        self.test_task.action_clear_lines()
        self.test_task.action_create_lines()
        line = self.test_task.line_ids.filtered(
            lambda line: line.res_id == partner.id)
        line.action_process()
        self.assertEqual(line.state, 'error')
        self.assertIn('Incorrect padding', line.result)

    def test_06_no_images(self):
        """Test processing content without images."""
        # Create test partner without images
        partner = self.env['res.partner'].create({
            'name': 'Test Partner No Images',
            'comment': '<p>Test content without images</p>',
        })

        self.test_task.action_clear_lines()
        self.test_task.action_create_lines()
        line = self.test_task.line_ids.filtered(
            lambda line: line.res_id == partner.id)
        line.action_process()
        self.assertEqual(line.state, 'success')
        self.assertEqual(line.result, 'No image for process')
