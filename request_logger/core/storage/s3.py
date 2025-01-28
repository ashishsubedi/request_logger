
import json
import boto3
from typing import Any, Dict, List
from request_logger.core.storage import AbstractStorage

class S3Storage(AbstractStorage):
    def __init__(
        self,
        bucket_name: str,
        prefix: str = '',
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        region_name: str = None
    ):
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip('/') + '/' if prefix else ''
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def _get_object_key(self, request_id: str) -> str:
        return f"{self.prefix}{request_id}.json"

    def save_request(self, request_id: str, request_data: Dict[str, Any]) -> None:
        object_key = self._get_object_key(request_id)
        json_data = json.dumps(request_data, indent=2)
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=json_data.encode('utf-8')
        )

    def load_request(self, request_id: str) -> Dict[str, Any]:
        object_key = self._get_object_key(request_id)
        response = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=object_key
        )
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)

    def list_requests(self) -> List[str]:
        paginator = self.s3_client.get_paginator('list_objects_v2')
        operation_parameters = {'Bucket': self.bucket_name, 'Prefix': self.prefix}
        page_iterator = paginator.paginate(**operation_parameters)

        request_ids = []
        for page in page_iterator:
            for obj in page.get('Contents', []):
                key = obj['Key']
                if key.endswith('.json'):
                    request_id = key[len(self.prefix):-5]  # Remove prefix and '.json'
                    request_ids.append(request_id)
        return request_ids
