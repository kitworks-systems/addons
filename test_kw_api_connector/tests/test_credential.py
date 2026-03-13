import json
from contextlib import contextmanager
from unittest.mock import patch, MagicMock
import requests
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestApiCredential(TransactionCase):

    def setUp(self):
        super().setUp()
        self.api_connector = self.env.ref(
            'test_kw_api_connector.test_kw_api_connector_demo')
        self.http_request_log_source = self.env.ref(
            'test_kw_api_connector.kw_http_request_log_source_demo')
        self.api_credential = self.env.ref(
            'test_kw_api_connector.test_kw_api_credential_demo')
        self.api_credential_xml = self.env.ref(
            'test_kw_api_connector.test_kw_api_credential_xml_demo')
        self.log_ids_to_unlink = []

    def tearDown(self):
        if self.log_ids_to_unlink:
            with self.env.registry.cursor() as new_cr:
                new_env = self.env(cr=new_cr)
                log_model = self.env['kw.http.request.log'].with_env(new_env)
                logs = log_model.browse(self.log_ids_to_unlink)
                logs.unlink()
                new_cr.commit()
        super().tearDown()

    @contextmanager
    def get_logs(self, domain):
        """Context manager for fetching logs in a new environment
        and deleting them after the test."""
        with self.env.registry.cursor() as new_cr:
            new_env = self.env(cr=new_cr)
            logs = new_env['kw.http.request.log'].search(domain)
            self.log_ids_to_unlink.extend(logs.ids)
            yield logs

    @patch('requests.request')
    def test_api_request_with_xml_type_and_real_data(self, mock_request):
        """Test api_request with type 'xml' and XML data."""
        data = '''<request>
 <item>
  Test element
 </item>
</request>
'''

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''<response>
 <status>
  Success
 </status>
</response>
'''
        mock_request.return_value = mock_response

        self.api_credential_xml.api_request(
            method='POST',
            url='/api/xml-endpoint',
            data=data
        )

        expected_data = data.encode('utf-8')
        mock_request.assert_called_with(
            method='POST',
            url='https://api.test.com/api/xml-endpoint',
            data=expected_data,
            allow_redirects=True,
            headers=self.api_credential_xml.get_api_headers(),
            timeout=60
        )

        domain = [
            ('name', '=', 'https://api.test.com/api/xml-endpoint'),
            ('method', '=', 'POST')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertEqual(log.code, '200')
            self.assertEqual(log.request_body, data)
            self.assertEqual(log.response_body, mock_response.text)
            self.assertFalse(log.error)

    @patch('requests.request')
    def test_api_request_successful_get(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        response_data = {'status': 'ok', 'data': {'id': 1, 'name': 'Test'}}
        mock_response.json.return_value = response_data
        mock_response.text = json.dumps(response_data)
        mock_request.return_value = mock_response

        result = self.api_credential.api_request(
            method='GET',
            url='/items/1',
            params={'expand': 'details'}
        )

        expected_result = {'status': 'ok', 'data': {'id': 1, 'name': 'Test'}}
        self.assertEqual(result, expected_result)

        mock_request.assert_called_once_with(
            method='GET',
            url='https://api.test.com/items/1',
            allow_redirects=True,
            params={'expand': 'details'},
            headers=self.api_credential.get_api_headers(),
            timeout=60
        )

        domain = [
            ('name', '=', 'https://api.test.com/items/1'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]
            self.assertEqual(log.code, '200')
            self.assertFalse(log.request_body)
            log_response_body = json.loads(log.response_body)
            self.assertEqual(log_response_body, expected_result)

            expected_headers = (
                '{\n  "Content-Type": "application/json",'
                '\n  "Accept": "application/json"\n}'
            )
            self.assertEqual(log.headers, expected_headers)

            log_params = json.loads(log.params)
            self.assertEqual(log_params, {'expand': 'details'})
            self.assertFalse(log.error)

    @patch('requests.request')
    def test_api_request_successful_post(self, mock_request):
        """Test successful execution of a POST request with data."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        response_data = {'status': 'ok', 'data': {'id': 2, 'name': 'New Item'}}
        mock_response.json.return_value = response_data
        mock_response.text = json.dumps(response_data)
        mock_request.return_value = mock_response

        request_data = {'name': 'New Item'}

        result = self.api_credential.api_request(
            method='POST',
            url='/items',
            json=request_data
        )

        expected_result = response_data
        self.assertEqual(result, expected_result)

        mock_request.assert_called_once_with(
            method='POST',
            url='https://api.test.com/items',
            json=request_data,
            allow_redirects=True,
            headers=self.api_credential.get_api_headers(),
            timeout=60
        )

        domain = [
            ('name', '=', 'https://api.test.com/items'),
            ('method', '=', 'POST')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertEqual(log.code, '201')

            log_request_body = json.loads(log.request_body)
            self.assertEqual(log_request_body, request_data)

            log_response_body = json.loads(log.response_body)
            self.assertEqual(log_response_body, expected_result)
            self.assertFalse(log.error)

    @patch('requests.request')
    def test_api_request_error_response_400_silent_true(self, mock_request):
        """Test without error handling for 400 Bad Request response."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        response_text = 'Bad Request\n'
        mock_response.text = response_text
        mock_response.json.side_effect = ValueError('No JSON object')
        mock_request.return_value = mock_response

        self.api_credential.api_request(
            method='GET',
            url='/items/invalid',
            silent=True
        )

        mock_request.assert_called_once_with(
            method='GET',
            url='https://api.test.com/items/invalid',
            allow_redirects=True,
            headers=self.api_credential.get_api_headers(),
            timeout=60
        )

        domain = [
            ('name', '=', 'https://api.test.com/items/invalid'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertEqual(log.code, '400')
            self.assertEqual(log.error, 'Bad Request\n')
            self.assertEqual(log.response_body, response_text)
            self.assertFalse(log.request_body)

    @patch('requests.request')
    def test_api_request_server_error_500_silent_false(self, mock_request):
        """Test error handling for a 500 Bad Request."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        response_text = 'Internal Server Error\n'
        mock_response.text = response_text
        mock_response.json.side_effect = ValueError('No JSON object')
        mock_request.return_value = mock_response

        with self.assertRaises(ValidationError) as cm:
            self.api_credential.api_request(
                method='GET',
                url='/server-error',
                silent=False
            )

        exception = cm.exception
        self.assertIn('"Test Credential" connection error', str(exception))
        self.assertIn('Internal Server Error', str(exception))

        domain = [
            ('name', '=', 'https://api.test.com/server-error'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertEqual(log.code, '500')
            self.assertEqual(log.error, 'Internal Server Error\n')
            self.assertEqual(log.response_body, response_text)
            self.assertFalse(log.request_body)

    @patch('requests.request')
    def test_api_request_exception_timeout_silent_true(self, mock_request):
        mock_request.side_effect = requests.exceptions.Timeout('Timed out')

        self.api_credential.api_request(
            method='GET',
            url='/timeout',
            silent=True
        )

        mock_request.assert_called_once_with(
            method='GET',
            url='https://api.test.com/timeout',
            allow_redirects=True,
            headers=self.api_credential.get_api_headers(),
            timeout=60
        )

        domain = [
            ('name', '=', 'https://api.test.com/timeout'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertFalse(log.code)
            self.assertEqual(log.error, 'Timed out')
            self.assertFalse(log.response_body)
            self.assertFalse(log.request_body)

    @patch('requests.request')
    def test_api_request_connection_error_silent_false(self, mock_request):
        """Test for ValidationError on connection issue."""
        mock_request.side_effect = requests.exceptions.ConnectionError('Fail')

        with self.assertRaises(ValidationError) as cm:
            self.api_credential.api_request(
                method='GET',
                url='/test-connection-error',
                silent=False
            )

        exception = cm.exception
        self.assertIn('"Test Credential" connection error', str(exception))
        self.assertIn('Fail', str(exception))

        domain = [
            ('name', '=', 'https://api.test.com/test-connection-error'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertFalse(log.code)
            self.assertEqual(log.error, 'Fail')
            self.assertFalse(log.response_body)
            self.assertFalse(log.request_body)

    @patch('requests.request')
    def test_api_request_invalid_json_response(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'Invalid JSON'
        mock_response.json.side_effect = ValueError('No JSON object')
        mock_request.return_value = mock_response

        result = self.api_credential.api_request(
            method='GET',
            url='/invalid-json',
            silent=True
        )

        self.assertFalse(result)

        domain = [
            ('name', '=', 'https://api.test.com/invalid-json'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertEqual(log.code, '200')
            self.assertIn('No JSON object', str(log.error))
            self.assertEqual(log.response_body, 'Invalid JSON')
            self.assertFalse(log.request_body)

    @patch(
        'odoo.addons.kw_api_connector.models.credential.ApiCredential'
        '.action_refresh_api_token', return_value=True
    )
    @patch(
        'odoo.addons.kw_api_connector.models.credential.ApiCredential'
        '.parse_api_error', return_value={  # nosec
            'is_refresh_api_token_needed': True,
            'message': 'Unauthorized'}
    )
    @patch('requests.request')
    def test_api_request_token_refresh(
        self, mock_request, mock_parse_api_error, mock_refresh_token
    ):
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401
        response_text_401 = 'Internal Server Error\n'
        mock_response_401.text = response_text_401

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        response_data_200 = {'status': 'success'}
        mock_response_200.json.return_value = response_data_200
        mock_response_200.text = json.dumps(response_data_200)

        mock_request.side_effect = [mock_response_401, mock_response_200]

        result = self.api_credential.api_request(
            method='GET',
            url='/needs-token-refresh'
        )

        self.assertEqual(result, {'status': 'success'})
        self.assertEqual(mock_request.call_count, 2)
        mock_refresh_token.assert_called_once()

        domain = [
            ('name', '=', 'https://api.test.com/needs-token-refresh'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 2)

            log_401 = logs.filtered(lambda log_entry: log_entry.code == '401')
            self.assertEqual(len(log_401), 1)
            log_401 = log_401[0]
            self.assertEqual(log_401.error, 'Unauthorized')
            self.assertEqual(log_401.response_body, response_text_401)

            log_200 = logs.filtered(lambda log_entry: log_entry.code == '200')
            self.assertEqual(len(log_200), 1)
            log_200 = log_200[0]
            self.assertEqual(log_200.error, False)
            log_response_body = json.loads(log_200.response_body)
            self.assertEqual(log_response_body, response_data_200)
            self.assertEqual(log_200.code, '200')

    @patch(
        'odoo.addons.kw_api_connector.models.credential.ApiCredential'
        '.action_refresh_api_token', return_value=False
    )
    @patch('requests.request')
    def test_api_request_token_refresh_failure_silent_true(
        self, mock_request, mock_refresh_token
    ):
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401
        mock_response_401.text = 'Unauthorized'
        mock_request.return_value = mock_response_401

        self.api_credential.api_request(
            method='GET',
            url='/token-refresh-failure',
            silent=True
        )

        domain = [
            ('name', '=', 'https://api.test.com/token-refresh-failure'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertEqual(log.code, '401')
            self.assertEqual(log.error, 'Unauthorized')
            self.assertEqual(log.response_body, 'Unauthorized')

    @patch(
        'odoo.addons.kw_api_connector.models.credential.ApiCredential'
        '.action_refresh_api_token', return_value=False
    )
    @patch('requests.request')
    def test_api_request_token_refresh_failure_silent_false(
        self, mock_request, mock_refresh_token
    ):
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401
        mock_response_401.text = 'Unauthorized'
        mock_request.return_value = mock_response_401

        with self.assertRaises(ValidationError) as context:
            self.api_credential.api_request(
                method='GET',
                url='/token-refresh-failure',
                silent=False
            )

        self.assertIn(
            'Connector "Test Credential" connection error',
            str(context.exception)
        )
        self.assertIn('Unauthorized', str(context.exception))

        domain = [
            ('name', '=', 'https://api.test.com/token-refresh-failure'),
            ('method', '=', 'GET')
        ]
        with self.get_logs(domain) as logs:
            self.assertEqual(len(logs), 1)
            log = logs[0]

            self.assertEqual(log.code, '401')
            self.assertEqual(log.error, 'Unauthorized')
            self.assertEqual(log.response_body, 'Unauthorized')

    def test_api_request_dynamic_method(self):
        def api_request_test_connector(
                self, method, url, data=None, params=None,
                headers=None, silent=True, renew_token=False):
            return 'Dynamic Method Called'

        setattr(
            self.api_credential.__class__,
            'api_request_test_connector',
            api_request_test_connector
        )

        self.api_credential.code = 'test_connector'

        result = self.api_credential.api_request(
            method='GET',
            url='/dynamic-method'
        )

        self.assertEqual(result, 'Dynamic Method Called')
