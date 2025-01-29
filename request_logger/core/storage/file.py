import datetime
import os
import json
from typing import Any, Dict, List, Optional
from request_logger.core.metadata_store import MetadataStore
from request_logger.core.storage import AbstractStorage
from request_logger.core.storage.mixins import LogManagementMixin

class FileStorage(AbstractStorage, LogManagementMixin):
    def __init__(self, storage_dir: str = "request_logs", max_logs: int = 100, metadata_store: MetadataStore | None = None):
        self.storage_dir = storage_dir
        self.max_logs = max_logs
        
        os.makedirs(self.storage_dir, exist_ok=True)
        self.metadata_store = metadata_store or MetadataStore()
    
    def _generate_filename(self, request_id: str, timestamp: str) -> str:
        # Sanitize timestamp to remove special characters
        safe_timestamp = timestamp.replace(':', '').replace('-', '')
        return f"{safe_timestamp}_{request_id}.json"

    def save_request(self, request_id: str, request_data: Dict[str, Any]) -> None:
        timestamp = request_data.get('timestamp')
        if not timestamp:
            timestamp = datetime.datetime.now(datetime.timezone.utc)
            request_data["timestamp"] = timestamp

        filename = self._generate_filename(request_id, timestamp)
        self.save_request_with_log_management(filename, request_data)

    def _save_request(self, filename: str, request_data: Dict[str, Any]) -> None:
        file_path = os.path.join(self.storage_dir, filename)

        with open(file_path, 'w') as f:
            json.dump(request_data, f, indent=2)

        self.metadata_store.add_request_metadata(request_data)

    def _find_filename_by_request_id(self, request_id: str) -> str:
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json') and filename.endswith(f"_{request_id}.json"):
                return filename
        return None

    def load_request(self, request_id: str) -> Dict[str, Any]:
        filename = self._find_filename_by_request_id(request_id)
        if not filename:
            raise FileNotFoundError(f"Request with ID {request_id} not found.")

        file_path = os.path.join(self.storage_dir, filename)
        with open(file_path, 'r') as f:
            request_data = json.load(f)
        return request_data

    def list_request_ids(self) -> List[str]:
        return [self._extract_request_id(filename) for filename in os.listdir(self.storage_dir) if filename.endswith('.json')]
    
    def list_filenames(self) -> List[str]:
        return [filename for filename in os.listdir(self.storage_dir) if filename.endswith('.json')]
    
    def _extract_request_id(self, filename: str) -> str:
        parts = filename[:-5].split('_')  # Remove '.json' and split
        return parts[-1] if len(parts) > 1 else filename[:-5]

    def get_sorted_identifiers(self) -> List[str]:
        # Return filenames sorted lexicographically, which sorts by timestamp
        return sorted(self.list_filenames())

    def search_requests(self, query: Dict[str, str], start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        # Convert start_time and end_time to timestamp strings matching the format in the database
        if start_time:
            start_time_formatted = self._convert_to_timestamp(start_time)
        else:
            start_time_formatted = None

        if end_time:
            end_time_formatted = self._convert_to_timestamp(end_time)
        else:
            end_time_formatted = None

        # Use the metadata store to search
        matching_request_ids = self.metadata_store.search(query, start_time=start_time_formatted, end_time=end_time_formatted)
        results = []
        for request_id in matching_request_ids:
            try:
                request_data = self.load_request(request_id)
                results.append(request_data)
            except FileNotFoundError:
                # Handle the case where the metadata exists but the file does not
                continue
        return results

    def _convert_to_timestamp(self, time_str: str) -> str:
        # Assuming the input time_str is in 'YYYY-MM-DD HH:MM:SS' format
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            # Convert to the timestamp format used in the database
            timestamp = dt.strftime('%Y%m%d%H%M%S%f')
            return timestamp
        except ValueError:
            raise ValueError("Invalid time format. Expected format: YYYY-MM-DD HH:MM:SS")

    def delete_request(self, request_id: str) -> None:
        filename = self._find_filename_by_request_id(request_id)
        if filename:
            os.remove(os.path.join(self.storage_dir, filename))
        self.metadata_store.delete_request_metadata(request_id)

    def _delete_by_identifier(self, identifier: str) -> None:
        
        # here, identifier is assumed to be filename
        file_path = os.path.join(self.storage_dir, identifier)
        if os.path.exists(file_path):
            os.remove(file_path)
        request_id = self._extract_request_id(identifier)
        self.metadata_store.delete_request_metadata(request_id)
    
    def close(self):
        self.metadata_store.close()