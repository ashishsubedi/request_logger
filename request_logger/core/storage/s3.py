
import datetime
import json
import boto3
from typing import Any, Dict, List
from request_logger.core.storage import AbstractStorage
from request_logger.core.storage.mixins import LogManagementMixin

class S3Storage(AbstractStorage, LogManagementMixin):
    def __init__(self, bucket_name: str, max_logs: int = 100):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        self.max_logs = max_logs

    def save_request(self, request_id: str, request_data: Dict[str, Any]) -> None:
        # Generate the key with the timestamp
        timestamp = request_data.get('timestamp')
        if not timestamp:
            timestamp = datetime.datetime.now(datetime.timezone.utc)
            request_data["timestamp"] = timestamp
            
        key = self._generate_key(request_id, timestamp)
        # Save the request using the mixin method
        self.save_request_with_log_management(key, request_data)

    def _generate_key(self, request_id: str, timestamp: str) -> str:
        safe_timestamp = timestamp.replace(':', '').replace('-', '').replace('.', '')
        return f"{safe_timestamp}_{request_id}.json"

    def _save_request(self, key: str, request_data: Dict[str, Any]) -> None:
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=json.dumps(request_data)
        )

    def load_request(self, request_id: str) -> Dict[str, Any]:
        key = self._find_key_by_request_id(request_id)
        if not key:
            raise FileNotFoundError(f"Request with ID {request_id} not found.")
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)

    def delete_request(self, request_id: str) -> None:
        key = self._find_key_by_request_id(request_id)
        if key:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)

    def list_request_ids(self) -> List[str]:
        return [self._extract_request_id(obj['Key']) for obj in self._list_objects()]

    def list_keys(self) -> List[str]:
        return [obj['Key'] for obj in self._list_objects()]

    def search_requests(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        for key in self.list_keys():
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response['Body'].read().decode('utf-8')
            request_data = json.loads(content)
            match = all(
                str(request_data.get(k, '')).lower() == str(v).lower()
                for k, v in query.items()
            )
            if match:
                results.append(request_data)
        return results

    def _find_key_by_request_id(self, request_id: str) -> str:
        for key in self.list_keys():
            if key.endswith(f"_{request_id}.json"):
                return key
        return None

    def _extract_request_id(self, key: str) -> str:
        parts = key[:-5].split('_')
        return parts[-1] if len(parts) > 1 else key[:-5]

    def _list_objects(self) -> List[Dict[str, Any]]:
        paginator = self.s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket_name)
        objects = []
        for page in page_iterator:
            objects.extend(page.get('Contents', []))
        return objects

    # Methods used by LogManagementMixin
    def get_sorted_identifiers(self) -> List[str]:
        # Return keys sorted lexicographically
        return sorted(self.list_keys())
