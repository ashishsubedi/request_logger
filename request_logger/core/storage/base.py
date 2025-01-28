from abc import ABC, abstractmethod
from typing import Any, Dict, List

class AbstractStorage(ABC):
    @abstractmethod
    def save_request(self, request_id: str, request_data: Dict[str, Any]) -> None:
        """Save request data identified by request_id."""
        pass

    @abstractmethod
    def load_request(self, request_id: str) -> Dict[str, Any]:
        """Load request data by request_id."""
        pass

    @abstractmethod
    def list_requests(self) -> List[str]:
        """List all saved request IDs."""
        pass