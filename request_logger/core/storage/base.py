from abc import ABC, abstractmethod
from typing import Any, Dict, List

class AbstractStorage(ABC):
    @abstractmethod
    def save_request(self, request_id: str, request_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def load_request(self, request_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_request(self, request_id: str) -> None:
        pass

    @abstractmethod
    def _delete_by_identifier(self, identifier: str) -> None:
        pass

    @abstractmethod
    def search_requests(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search requests based on given query parameters.
        """
        pass

    @abstractmethod
    def list_request_ids(self) -> List[str]:
        """
        Retrieve all stored request IDs.
        """
        pass

    @abstractmethod
    def list_filenames(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_sorted_identifiers(self) -> List[str]:
        # Return filenames sorted lexicographically, which sorts by timestamp
        pass
