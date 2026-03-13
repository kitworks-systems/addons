# pylint: disable=E8102
from datetime import timedelta
from odoo import fields
from .common import TestCommon


class TestHTTPRequestLogSource(TestCommon):

    def test_get_deletion_date(self):
        deletion_date = self.source.get_deletion_date()
        expected_date = fields.Date.today() + timedelta(days=30)
        self.assertEqual(deletion_date, expected_date,
                         "Incorrect deletion date")

    # def test_create_log(self):
    #     """Test the creation of an HTTP Request Log."""
    #     # Prepare input data for the create_log method
    #     log_values = {
    #         'method': 'POST',
    #         'name': 'https://example.com/test',
    #         'request_body': '{"key": "value"}',
    #         'response_body': '{"status": "success"}',
    #         'error': '{"error": "Some error occurred"}',
    #     }
    #     # Видалено self.env.cr.commit() - у тестах Odoo 15.0 транзакції
    #     # управляються автоматично
    #
    #     # Call the create_log method with prepared data
    #     log_id = self.source.create_log(log_values)
    #     # Видалено self.env.cr.commit() - у тестах Odoo 15.0 транзакції
    #     # управляються автоматично
    #
    #     # Check if the HTTP Request Log was created
    #     self.assertTrue(log_id, "Failed to create HTTP Request Log")
    #
    #     # Check if the log record exists with the required values
    #     log = self.env['kw.http.request.log'].browse(log_id)
    #     self.assertTrue(log, "Log record does not exist")
    #     self.assertEqual(log.method, 'POST')
    #     self.assertEqual(log.name, 'https://example.com/test')
    #     self.assertEqual(log.request_body, '{\n  "key": "value"\n}')
    #     self.assertEqual(log.response_body, '{\n  "status": "success"\n}')
    #     self.assertEqual(log.error, '{\n  "error": "Some error occurred"\n}')

    # def test_update_log(self):
    #     """Test updating an existing HTTP Request Log."""
    #     log_model = self.env['kw.http.request.log']
    #     log = log_model.create({
    #         'method': 'POST',
    #         'name': 'https://example.com/test',
    #         'request_body': '{"key": "value"}',
    #         'response_body': '{"status": "success"}',
    #         'error': '{"error": "Some error occurred"}',
    #         'log_source_id': self.source.id,
    #     })
    #
    #     # Видалено self.env.cr.commit() - у тестах Odoo 15.0 транзакції
    #     # управляються автоматично
    #
    #     # Update the value of 'method' to 'GET'
    #     updated_method = 'GET'
    #     self.assertTrue(
    #         self.source.update_log(log.id, {'method': updated_method})
    #     )
    #     # Видалено self.env.cr.commit() - у тестах Odoo 15.0 транзакції
    #     # управляються автоматично
    #
    #     # Check that the value of 'method' has been changed
    #     self.assertEqual(log.method, updated_method)
