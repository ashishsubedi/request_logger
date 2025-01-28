import unittest
from unittest.mock import MagicMock, patch, mock_open
import tempfile
import uuid
import json
import base64
import requests

# Import your RequestLogger and related classes
from request_logger.core.request_logger import RequestLogger
from request_logger.core.storage import AbstractStorage, FileStorage

class TestRequestLogger(unittest.TestCase):
    def setUp(self):
        # Create a mock storage
        self.mock_storage = MagicMock(spec=AbstractStorage)
        self.logger = RequestLogger(storage=self.mock_storage)
    
    def test_log_request_basic(self):
        # Test logging a basic GET request
        method = 'GET'
        url = 'https://example.com/api'
        kwargs = {}

        request_id, logged_params = self.logger.log_request(method, url, **kwargs)

        # Assert that a UUID is generated
        uuid_obj = uuid.UUID(request_id)
        self.assertIsInstance(uuid_obj, uuid.UUID)

        # Assert that save_request was called with correct parameters
        self.mock_storage.save_request.assert_called_once()
        saved_request_id, saved_request_data = self.mock_storage.save_request.call_args[0]

        # Verify saved request data
        self.assertEqual(saved_request_id, request_id)
        self.assertEqual(saved_request_data['method'], method)
        self.assertEqual(saved_request_data['url'], url)
        self.assertFalse(saved_request_data['body'])  # Should be empty
        self.assertFalse(saved_request_data['body_is_encoded'])
        self.assertIsNone(saved_request_data['files'])
        self.assertEqual(saved_request_data['original_kwargs'], {})

        # Verify returned logged_params
        self.assertEqual(logged_params['method'], method)
        self.assertEqual(logged_params['url'], url)
    
    def test_log_request_with_body(self):
        # Test logging a POST request with a JSON body
        method = 'POST'
        url = 'https://example.com/api'
        kwargs = {
            'json': {'key': 'value'}
        }

        request_id, logged_params = self.logger.log_request(method, url, **kwargs)

        # Extract saved request data
        saved_request_data = self.mock_storage.save_request.call_args[0][1]

        # Verify the body is correctly saved as a JSON string
        self.assertEqual(saved_request_data['body'], json.dumps({'key': 'value'}))
        self.assertFalse(saved_request_data['body_is_encoded'])

        # Verify original_kwargs
        self.assertEqual(saved_request_data['original_kwargs'], kwargs)
    
    def test_log_request_with_files(self):
        # Test logging a POST request with files
        method = 'POST'
        url = 'https://example.com/upload'
        file_content = b'This is test file content.'
        file_tuple = ('test.txt', file_content, 'text/plain')
        kwargs = {
            'files': {
                'file': file_tuple
            }
        }

        with patch('builtins.open', mock_open(read_data=file_content)) as mocked_file:
            request_id, logged_params = self.logger.log_request(method, url, **kwargs)

            # Extract saved request data
            saved_request_data = self.mock_storage.save_request.call_args[0][1]

            # Verify that files are processed correctly
            processed_files = saved_request_data['files']
            self.assertIn('file', processed_files)
            self.assertEqual(processed_files['file']['filename'], 'test.txt')
            self.assertEqual(processed_files['file']['content_type'], 'text/plain')
            self.assertEqual(
                base64.b64decode(processed_files['file']['content']),
                file_content
            )

            # Verify that original_kwargs files are sanitized
            self.assertEqual(saved_request_data['original_kwargs']['files'], {'file': 'test.txt'})

    def test_log_request_with_binary_body(self):
        # Test logging a request with binary body content
        method = 'POST'
        url = 'https://example.com/api'
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00'
        kwargs = {
            'data': binary_content
        }

        request_id, logged_params = self.logger.log_request(method, url, **kwargs)

        # Extract saved request data
        saved_request_data = self.mock_storage.save_request.call_args[0][1]

        # Body should be base64 encoded
        self.assertTrue(saved_request_data['body_is_encoded'])
        decoded_body = base64.b64decode(saved_request_data['body'])
        self.assertEqual(decoded_body, binary_content)
    
    @patch('requests.get')
    def test_get_logged_method(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Get the logged get method
        logged_get = self.logger.get_logged_method(requests.get)
        response = logged_get('https://example.com/api')

        # Assert that the request was logged
        self.mock_storage.save_request.assert_called_once()

        # Assert that the original requests.get was called
        mock_get.assert_called_once_with('https://example.com/api')

        # Assert that response is returned correctly
        self.assertEqual(response.status_code, 200)
    
    @patch('requests.Session')
    def test_get_logged_session(self, mock_session_class):
        # Setup mock session and response
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Get the logged session
        logged_session = self.logger.get_logged_session()
        response = logged_session.request('POST', 'https://example.com/api', json={'data': 'value'})

        # Assert that the request was logged
        self.mock_storage.save_request.assert_called_once()

        # Assert that the session's request method was called
        mock_session.request.assert_called_once_with('POST', 'https://example.com/api', json={'data': 'value'})

        # Assert that response is returned correctly
        self.assertEqual(response.status_code, 201)
    
    def test_process_files(self):
        # Test the private _process_files method
        files = {
            'file1': ('test1.txt', b'Content of file 1', 'text/plain'),
            'file2': ('test2.txt', b'Content of file 2', 'text/plain'),
        }

        processed_files = self.logger._process_files(files)

        # Verify that files are processed correctly
        for key, file_info in files.items():
            processed_file = processed_files[key]
            filename, content, content_type = file_info
            self.assertEqual(processed_file['filename'], filename)
            self.assertEqual(processed_file['content_type'], content_type)
            self.assertEqual(
                base64.b64decode(processed_file['content']),
                content
            )
    
    def test_sanitize_kwargs(self):
        # Test the private _sanitize_kwargs method
        kwargs = {
            'params': {'key': 'value'},
            'files': {
                'file': ('test.txt', b'File content', 'text/plain')
            }
        }

        sanitized_kwargs = self.logger._sanitize_kwargs(kwargs)

        # Verify that files are sanitized
        self.assertEqual(sanitized_kwargs['params'], {'key': 'value'})
        self.assertEqual(sanitized_kwargs['files'], {'file': 'test.txt'})
    
    def test_log_request_with_non_utf8_body(self):
        # Test logging a request with non-UTF-8 body
        method = 'POST'
        url = 'https://example.com/api'
        binary_content = 'こんにちは'.encode('shift_jis')  # Japanese text encoded in Shift-JIS
        kwargs = {
            'data': binary_content
        }

        request_id, logged_params = self.logger.log_request(method, url, **kwargs)

        # Extract saved request data
        saved_request_data = self.mock_storage.save_request.call_args[0][1]

        # Body should be base64 encoded
        self.assertTrue(saved_request_data['body_is_encoded'])
        decoded_body = base64.b64decode(saved_request_data['body'])
        self.assertEqual(decoded_body, binary_content)

    def tearDown(self):
        pass  # Clean up resources if needed

if __name__ == '__main__':
    unittest.main()
