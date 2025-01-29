# examples/example1.py

from request_logger.core.request_logger import RequestLogger
from request_logger.core.replayer import Replayer
from request_logger.core.storage.file import FileStorage

import requests
import io

# Initialize the logger and storage
storage = FileStorage(storage_dir='request_logs')
logger = RequestLogger(storage=storage, max_logs=10)
replayer = Replayer(storage=storage)

# Prepare request details
url = 'https://httpbin.org/post'
headers = {'Content-Type': 'application/json'}
json_data = {'key': 'value'}
files = {
    'file': ('test.txt', io.BytesIO(b'This is a test file'), 'text/plain')
}

# Log the request and get the request ID and parameters
request_id, request_params = logger.log_request(
    method='POST',
    url=url,
    headers=headers,
    json=json_data,
    files=files
)

# Make the actual request using the returned parameters
response = requests.request(**request_params)
print(f"Status code: {response.status_code}")
print(f"Response body: {response.text}")

# Now, replay the request using the request ID
replay_response = replayer.replay_request(request_id)
print(f"Replayed request status code: {replay_response.status_code}")
print(f"Replayed response body: {replay_response.text}")


# Log some requests
for i in range(5):
    logger.log_request('GET', f'https://example.com/api/{i}')

print(f"Total logs: {len(logger.storage.list_request_ids())}") 