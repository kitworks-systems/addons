# pylint: disable=E8102
from datetime import timedelta
from odoo.exceptions import MissingError
from odoo import fields
from .common import TestCommon


class TestHTTPRequestLog(TestCommon):

    def test_prepare_value_valid_json(self):
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        }
        log_model = self.env['kw.http.request.log']
        prep_log_vals = log_model.prepare_value(log_values)

        self.assertEqual(
            prep_log_vals['request_body'], '{\n  "key": "value"\n}'
        )
        self.assertEqual(
            prep_log_vals['response_body'], '{\n  "status": "success"\n}'
        )
        self.assertEqual(
            prep_log_vals['error'], '{\n  "error": "Some error occurred"\n}'
        )

    def test_prepare_value_xml(self):
        xml_request_body = '''<root>
 <data>
  Hello, XML!
 </data>
</root>
'''
        xml_response_body = '''<root>
 <result>
  Success
 </result>
</root>
'''
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': xml_request_body,
            'response_body': xml_response_body,
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        }
        log_model = self.env['kw.http.request.log']
        prep_log_vals = log_model.prepare_value(log_values)

        self.assertEqual(prep_log_vals['request_body'], xml_request_body)
        self.assertEqual(prep_log_vals['response_body'], xml_response_body)

    def test_prepare_value_array(self):
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': {"key": "value"},
            'response_body': {"status": "success"},
            'error': {"error": "Some error occurred"},
            'log_source_id': self.source.id,
        }
        log_model = self.env['kw.http.request.log']
        prep_log_vals = log_model.prepare_value(log_values)

        self.assertEqual(
            prep_log_vals['request_body'], log_values['request_body'])
        self.assertEqual(
            prep_log_vals['response_body'], log_values['response_body'])
        self.assertEqual(
            prep_log_vals['error'], log_values['error'])

    def test_prepare_value_empty_input(self):
        log_values = {}
        log_model = self.env['kw.http.request.log']
        prep_log_vals = log_model.prepare_value(log_values)

        self.assertEqual(prep_log_vals, {})

    def test_prepare_value_invalid_json(self):
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': '{"key": "value"',  # Contains invalid json
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        }
        log_model = self.env['kw.http.request.log']
        prep_log_vals = log_model.prepare_value(log_values)

        self.assertEqual(
            prep_log_vals['request_body'], log_values['request_body'])

    def test_prepare_value_special_characters(self):
        request_body = '{"key": "<script>alert(1)</script>"}'
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': request_body,  # Contains special characters
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        }
        log_model = self.env['kw.http.request.log']
        prep_log_vals = log_model.prepare_value(log_values)

        self.assertEqual(
            prep_log_vals['request_body'], log_values['request_body'])

    def test_prepare_value_long_body_to_file(self):
        long_body = 'a' * (self.source.body_text_log_limit * 1024 + 1)
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': long_body,
            'response_body': long_body,
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        }
        log_model = self.env['kw.http.request.log']
        prep_log_vals = log_model.prepare_value(log_values)

        self.assertTrue(
            prep_log_vals['request_body_file'],
            "Long body should be converted to file")
        self.assertTrue(
            prep_log_vals['response_body_file'],
            "Long body should be converted to file")
        self.assertEqual(prep_log_vals['request_body'], '')
        self.assertEqual(prep_log_vals['response_body'], '')

    def test_prepare_value_short_body_no_file(self):
        short_body = 'a'
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': short_body,
            'response_body': short_body,
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        }
        log_model = self.env['kw.http.request.log']
        prep_log_vals = log_model.prepare_value(log_values)

        self.assertFalse(
            prep_log_vals.get('request_body_file', False),
            "Short body should not be converted to file")
        self.assertFalse(
            prep_log_vals.get('response_body_file', False),
            "Short body should not be converted to file")
        self.assertEqual(prep_log_vals['request_body'], 'a')
        self.assertEqual(prep_log_vals['response_body'], 'a')

    def test_create_single_log(self):
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        }
        created_log = self.env['kw.http.request.log'].create(log_values)

        # Make sure the log was created
        self.assertTrue(created_log)

        # Make sure the delete_by_date field value is set correctly
        expected_delete_by_date = self.source.get_deletion_date()
        self.assertEqual(created_log.delete_by_date, expected_delete_by_date,
                         "Delete by date should be set correctly")

        # Check if the data in the created log matches the input data
        for key, value in log_values.items():
            if key != 'log_source_id':
                self.assertEqual(
                    created_log[key], value,
                    f"Value of {key} should match the input value")

    def test_create_multiple_logs(self):
        vals_list = [
            {
                'method': 'POST',
                'name': 'https://example.com/test1',
                'request_body': '{"key": "value1"}',
                'response_body': '{"status": "success1"}',
                'error': '{"error": "Some error occurred1"}',
                'log_source_id': self.source.id,
            },
            {
                'method': 'POST',
                'name': 'https://example.com/test2',
                'request_body': '{"key": "value2"}',
                'response_body': '{"status": "success2"}',
                'error': '{"error": "Some error occurred2"}',
                'log_source_id': self.source.id,
            }
        ]
        created_logs = self.env['kw.http.request.log'].create(vals_list)

        # Check the number of created logs
        self.assertEqual(len(created_logs), 2,
                         "Two Logs should be created")

        for index, vals in enumerate(vals_list):
            # Check each created log
            self.assertTrue(created_logs[index],
                            "Log should be created")

            # Make sure the delete_by_date field value is set correctly
            expected_delete_by_date = self.source.get_deletion_date()
            self.assertEqual(
                created_logs[index].delete_by_date, expected_delete_by_date,
                "Delete by date should be set correctly")

            # Check properties of the created log
            for key, value in vals.items():
                if key != 'log_source_id':
                    self.assertEqual(
                        created_logs[index][key], value,
                        f"Value of {key} should match the input value")

        # Check uniqueness of the logs
        unique_ids = set(created_logs.ids)
        self.assertEqual(len(unique_ids), 2,
                         "All Logs should have unique IDs")

        # Check data persistence in the database
        for log in created_logs:
            saved_log = self.env['kw.http.request.log'].browse(log.id)
            self.assertEqual(
                log, saved_log,
                "Log data should be saved in the database")

    def test_create_with_invalid_source_id(self):
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': 99999,
        }
        with self.assertRaises(MissingError) as cm:
            self.env['kw.http.request.log'].create(log_values)

        self.assertIn(
            "Record does not exist or has been deleted.", str(cm.exception))

    def test_write_with_valid_values(self):
        log_values = {
            'name': 'https://example.com/test',
            'method': 'GET',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        }
        created_log = self.env['kw.http.request.log'].create(log_values)

        # Update the log with new valid values
        updated_vals = {
            'name': 'https://example.com/updated',
            'method': 'POST',
            'request_body': '{"updated_key": "updated_value"}',
            'response_body': '{"status": "updated"}',
            'error': '{"error": "Updated error occurred"}'
        }
        created_log.write(updated_vals)

        # Check if the changes were made
        for key, value in updated_vals.items():
            self.assertEqual(
                getattr(created_log, key), value, f"{key} should be updated")

    def test_create_in_new_transaction(self):
        log_values = {
            'name': 'https://example.com/test',
            'method': 'POST',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id
        }
        self.env.cr.commit()
        log_model = self.env['kw.http.request.log']
        created_log = log_model.create_in_new_transaction(log_values)
        self.env.cr.commit()

        self.assertTrue(
            created_log, "Failed to create Log in a new transaction")
        searched_log = self.env['kw.http.request.log'].browse(created_log)
        self.assertTrue(searched_log, "Log object does not exist.")

    def test_create_in_new_transaction_disabled_source(self):
        self.source.write({'is_log_enabled': False})
        log_values = {
            'method': 'POST',
            'name': 'https://example.com/test',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_name': 'Test Source',
        }
        self.env.cr.commit()
        log_model = self.env['kw.http.request.log']
        created_log = log_model.create_in_new_transaction(log_values)

        self.assertFalse(created_log,
                         "Created Log despite log source being disabled")

    def test_create_in_new_transaction_log_source_id_not_found(self):
        log_values = {
            'name': 'https://example.com/test',
            'method': 'POST',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': 9999  # Nonexistent log source ID
        }
        self.env.cr.commit()

        with self.assertRaises(MissingError) as cm:
            log_model = self.env['kw.http.request.log']
            log_model.create_in_new_transaction(log_values)
        self.assertIn(
            "Record does not exist or has been deleted.", str(cm.exception))

    def test_write_in_new_transaction_with_valid_data(self):
        created_log = self.env['kw.http.request.log'].create({
            'name': 'https://example.com',
            'method': 'POST',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        })
        self.env.cr.commit()

        new_name = 'https://example.com/updated'
        log_id = created_log.id
        log_model = self.env['kw.http.request.log']
        log_model.write_in_new_transaction(log_id, {'name': new_name})
        self.env.cr.commit()
        searched_log = self.env['kw.http.request.log'].browse(log_id)

        self.assertEqual(searched_log.name, new_name)

    # def test_write_in_new_transaction_with_invalid_log_id(self):
    #     self.env.cr.commit()
    #
    #     log_model = self.env['kw.http.request.log']
    #     result = log_model.write_in_new_transaction(2222, {'name': 'Name'})
    #
    #     self.assertFalse(result)

    def test_cron_delete_outdated_logs(self):
        outdated_log = self.env['kw.http.request.log'].create({
            'method': 'POST',
            'name': 'https://example.com/outdated',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        })
        outdated_log.write({
            'delete_by_date': fields.Date.today() - timedelta(days=1)
        })

        self.assertTrue(outdated_log.exists(),
                        "Outdated log doesn't exist before cron execution")

        self.env['kw.http.request.log'].cron_delete_outdated_logs()

        self.assertFalse(outdated_log.exists(),
                         "Outdated log still exists after cron execution")

    def test_non_outdated_logs_not_deleted(self):
        not_outdated_log = self.env['kw.http.request.log'].create({
            'method': 'POST',
            'name': 'https://example.com/outdated',
            'request_body': '{"key": "value"}',
            'response_body': '{"status": "success"}',
            'error': '{"error": "Some error occurred"}',
            'log_source_id': self.source.id,
        })
        not_outdated_log.write({
            'delete_by_date': fields.Date.today() + timedelta(days=1)
        })

        self.assertTrue(not_outdated_log.exists(),
                        "Non-outdated log exists before cron execution")

        self.env['kw.http.request.log'].cron_delete_outdated_logs()

        self.assertTrue(not_outdated_log.exists(),
                        "Non-outdated log still exists after cron execution")
