import base64
import uuid
import datetime
from typing import Any, Dict, Callable, List, Optional
from functools import wraps
import requests
from requests.models import Request
from request_logger.core.storage import AbstractStorage, FileStorage

class RequestLogger:
    def __init__(self, storage: AbstractStorage = None, max_logs: int = 100):
        if storage is None:
            storage = FileStorage(max_logs=max_logs)
        else:
            storage.max_logs = max_logs

        self.storage = storage

    def log_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Logs a request and returns a dictionary of request parameters.

        Parameters match those accepted by requests.request.
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')


        # Create a Request object to handle parameter processing
        req = Request(method=method.upper(), url=url, **kwargs)
        prepared = req.prepare()

        data = kwargs.get('data')
        json_data = kwargs.get('json')
        files = kwargs.get('files')

        processed_files = self._process_files(files) if files else None
        
        # Prepare the request data to be saved
        request_data = {
            'id': request_id,
            'timestamp': timestamp,
            'method': method.upper(),
            'url': prepared.url,
            'headers': dict(prepared.headers),
            'data': self._process_data(data),
            'json': json_data,
            'files': processed_files,
            'original_kwargs': self._sanitize_kwargs(kwargs),            
        }

        # Save request data
        self.storage.save_request(request_id, request_data)

        # Return request parameters for immediate use
        request_params = kwargs.copy()
        if files:
            request_params['files'] = files  # Keep the original file objects
        return request_id, {
            'method': method,
            'url': url,
            **request_params,
        }

    def _process_files(self, files):
        """
        Convert files to a serializable format, encoding file content with base64.
        """
        processed_files = {}
        for key, file_info in files.items():
            if isinstance(file_info, (tuple, list)):
                # Expected format: (filename, fileobj[, content_type])
                filename = file_info[0]
                file_obj = file_info[1]
                content_type = file_info[2] if len(file_info) > 2 else None

                # Read the file content and encode it with base64
                if hasattr(file_obj, 'read'):
                    file_content = file_obj.read()
                    file_obj.seek(0)  # Reset file pointer
                else:
                    file_content = file_obj  # Handle string or bytes directly

                encoded_content = base64.b64encode(file_content).decode('utf-8')

                processed_files[key] = {
                    'filename': filename,
                    'content': encoded_content,
                    'content_type': content_type,
                }
            else:
                # Handle the case where file_info is not a tuple/list
                processed_files[key] = str(file_info)
        return processed_files


    def _process_data(self, data):
        """
        Process data to make it serializable.
        """
        if data is None:
            return None
        if isinstance(data, bytes):
            # Encode bytes data with base64
            encoded_data = base64.b64encode(data).decode('utf-8')
            return {'content': encoded_data, 'is_base64': True}
        elif isinstance(data, str):
            return {'content': data, 'is_base64': False}
        elif isinstance(data, dict):
            return data  # Assume it's serializable
        else:
            # Handle other data types as needed
            return {'content': str(data), 'is_base64': False}

    def _sanitize_kwargs(self, kwargs):
        """
        Remove file objects from kwargs to prevent serialization issues.
        """
        sanitized = kwargs.copy()
        if 'files' in sanitized:
            sanitized['files'] = {k: v[0] for k, v in sanitized['files'].items()}  # Keep filenames only
        return sanitized

    def get_logged_method(self, method: Callable) -> Callable:
        """
        Returns a wrapped requests method that logs the request before executing it.
        """
        @wraps(method)
        def wrapper(url, *args, **kwargs):
            # Log the request
            self.log_request(method=method.__name__.upper(), url=url, **kwargs)
            # Call the original requests method
            return method(url, *args, **kwargs)
        return wrapper

    def get_logged_session(self) -> requests.Session:
        """
        Returns a logged session where all requests are logged automatically.
        """
        logger = self

        class LoggedSession(requests.Session):
            def request(self_inner, method, url, **kwargs):
                # Log the request
                logger.log_request(method=method, url=url, **kwargs)
                # Call the original request method
                return super(LoggedSession, self_inner).request(method, url, **kwargs)

        return LoggedSession()

    def load_request(self, request_id: str) -> Dict[str, Any]:
        return self.storage.load_request(request_id)

    def search_requests(self, query: Dict[str, str],  start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.storage.search_requests(query, start_time=start_time, end_time=end_time)
    def list_request_ids(self):
        return self.storage.list_request_ids()