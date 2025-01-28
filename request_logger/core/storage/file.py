import os
import json
from typing import Any, Dict, List
from request_logger.core.storage import AbstractStorage

class FileStorage(AbstractStorage):
    def __init__(self, directory: str = "request_logs"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def _get_file_path(self, request_id: str) -> str:
        filename = f"{request_id}.json"
        return os.path.join(self.directory, filename)

    def save_request(self, request_id: str, request_data: Dict[str, Any]) -> None:
        file_path = self._get_file_path(request_id)
        with open(file_path, 'w') as f:
            json.dump(request_data, f, indent=2)

    def load_request(self, request_id: str) -> Dict[str, Any]:
        file_path = self._get_file_path(request_id)
        with open(file_path, 'r') as f:
            request_data = json.load(f)
        return request_data

    def list_requests(self) -> List[str]:
        files = os.listdir(self.directory)
        request_ids = [os.path.splitext(f)[0] for f in files if f.endswith('.json')]
        return request_ids
