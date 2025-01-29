
import datetime
from typing import Any, Dict, List

class LogManagementMixin:
    max_logs: int = 100 

    def save_request_with_log_management(self, identifier: str, request_data: Dict[str, Any]) -> None:
        # Save the request data using the storage's save_request method
        self._save_request(identifier, request_data)

        # Enforce the maximum logs limit
        if self.max_logs is not None:
            self._enforce_max_logs()

    def _enforce_max_logs(self):
        identifiers = self.get_sorted_identifiers()
        if len(identifiers) <= self.max_logs:
            return  # No action needed

        # Calculate how many logs to delete
        num_to_delete = len(identifiers) - self.max_logs
        identifiers_to_delete = identifiers[:num_to_delete]

        # Delete old logs
        for identifier in identifiers_to_delete:
            self._delete_by_identifier(identifier)
