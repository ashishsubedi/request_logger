import base64
from typing import Any, Dict, Optional
import requests
from request_logger.storage import AbstractStorage

class Replayer:
    def __init__(self, storage: AbstractStorage):
        self.storage = storage

    def replay_request(
        self,
        request_id: str,
        modifications: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Replays a request based on its ID.

        Args:
            request_id (str): The ID of the request to replay.
            modifications (Optional[Dict[str, Any]]): Optional modifications to apply to the request.

        Returns:
            requests.Response: The response from the server.
        """

        request_data = self.storage.load_request(request_id)
        if modifications:
            # Apply modifications to the request data
            request_data.update(modifications)

        method = request_data['method']
        url = request_data['url']
        headers = request_data.get('headers')
        body = request_data.get('body')
        body_is_encoded = request_data.get('body_is_encoded', False)
        files = self._reconstruct_files(request_data.get('files'))
        original_kwargs = request_data.get('original_kwargs', {})

        # Decode the body if it was encoded
        if body_is_encoded and body is not None:
            body = base64.b64decode(body)


        # Reconstruct the kwargs for the request
        request_kwargs = original_kwargs.copy()
        if files:
            request_kwargs['files'] = files
        if headers:
            request_kwargs['headers'] = headers
        if body and 'data' not in request_kwargs and 'json' not in request_kwargs:
            request_kwargs['data'] = body

        # Make the request
        response = requests.request(method=method, url=url, **request_kwargs)
        return response

    def _reconstruct_files(self, files_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not files_data:
            return None

        reconstructed_files = {}
        for key, file_info in files_data.items():
            filename = file_info.get('filename')
            encoded_content = file_info.get('content')
            content_type = file_info.get('content_type')

            # Decode the base64 content
            file_content = base64.b64decode(encoded_content)

            # Reconstruct the file tuple
            file_tuple = (filename, file_content)
            if content_type:
                file_tuple += (content_type,)
            reconstructed_files[key] = file_tuple
        return reconstructed_files
