from typing import Any, Dict, Optional
import requests
from request_logger.core.storage import AbstractStorage
from request_logger.core.util import RequestUtil

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
        # import pdb; pdb.set_trace()
        method = request_data['method']
        url = request_data['url']
        request_kwargs = RequestUtil.parse_request_kwargs(request_data)
        print(method, url, request_kwargs)
        response = requests.request(method=method, url=url, **request_kwargs)
        return response
