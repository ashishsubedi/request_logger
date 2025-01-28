# Request Logger

A Python package for logging and replaying HTTP requests made using the `requests` library. This package allows you to seamlessly integrate request logging into your existing workflows, store the logged requests using various backends, and replay them at any time.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Logging Requests](#logging-requests)
  - [Replaying Requests](#replaying-requests)
  - [Using Different Storage Backends](#using-different-storage-backends)
- [Project Structure](#project-structure)
- [Components Checklist](#components-checklist)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Request Logging**: Log HTTP requests made using the `requests` library with minimal changes to your code.
- **Request Replaying**: Replay logged requests exactly as they were made or with modifications.
- **Multiple Storage Backends**: Support for different storage backends, including file system, AWS S3, and PostgreSQL.
- **Seamless Integration**: Designed to integrate smoothly with the `requests` library and your existing codebase.
- **Extensible Architecture**: Easy to extend with additional storage backends or custom functionality.

## Installation

### Requirements

- Python 3.6 or higher
- `requests` library
- Additional dependencies for specific storage backends (e.g., `boto3` for S3, `psycopg2` for PostgreSQL)

### Install via pip

```bash
pip install request-logger
```
Note: The package is not yet published on PyPI. You can install it locally by cloning the repository and running:
```
git clone https://github.com/yourusername/request-logger.git
cd request-logger
pip install -e .
```
## Usage 

### Logging Requests
```python
from request_logger.request_logger import RequestLogger
from request_logger.storage.file import FileStorage

# Initialize the logger and storage
storage = FileStorage(directory='request_logs')
logger = RequestLogger(storage=storage)

# Prepare request details
url = 'https://httpbin.org/post'
headers = {'Content-Type': 'application/json'}
json_data = {'key': 'value'}

# Log the request and get the request ID and parameters
request_id, request_params = logger.log_request(
    method='POST',
    url=url,
    headers=headers,
    json=json_data,
)

# Make the actual request using the returned parameters
import requests
response = requests.request(**request_params)
print(f"Status code: {response.status_code}")
```

### Replaying Requests
```python
from request_logger.replayer import Replayer

# Initialize the replayer with the same storage used for logging
replayer = Replayer(storage=storage)

# Replay the request using the request ID
replay_response = replayer.replay_request(request_id)
print(f"Replayed request status code: {replay_response.status_code}")
```

### Using Different Storage Backends

File Storage (Default)
```python
from request_logger.storage.file import FileStorage

storage = FileStorage(directory='request_logs')
```

S3 Storage
```python
from request_logger.storage.s3 import S3Storage

storage = S3Storage(
    bucket_name='your-bucket-name',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='YOUR_REGION'
)
```
PostgreSQL Storage
```python
from request_logger.storage.postgres import PostgresStorage

storage = PostgresStorage(
    database_url='postgresql://user:password@localhost:5432/your_database'
)
```
Note: Replace the placeholders with your actual credentials and information.
Project Structure
```bash
your_project_root/
├── request_logger/
│   ├── __init__.py
│   ├── request_logger.py
│   ├── replayer.py
│   └── storage/
│       ├── __init__.py
│       ├── base.py
│       ├── file.py
│       ├── s3.py
│       └── postgres.py
├── examples/
│   ├── example1.py
│   └── example2.py
├── tests/
│   ├── __init__.py
│   ├── test_logger.py
│   ├── test_replayer.py
│   └── test_storage.py
├── README.md
├── CONTRIBUTING.md
├── pyproject.toml
├── uv.lock
└── other files...
```
## Components Checklist

Completed Components

    Core Functionality
        RequestLogger class (request_logger.py)
        Replayer class (replayer.py)

    File Storage Backend
        FileStorage class (storage/file.py)

    Project Structure and Imports
        Standardized project structure
        Seamless imports in example scripts

    Configuration
        pyproject.toml with project metadata and dependencies

    Example Script
        examples/example1.py demonstrating basic usage

Components to Implement

    Additional Storage Backends
        S3Storage class (storage/s3.py)
        PostgresStorage class (storage/postgres.py)

    Testing Suite
        Unit tests for core functionalities
        Integration tests

    Documentation
        Expand README.md with detailed instructions
        API documentation using docstrings

    Error Handling and Validation
        Improve error handling throughout the code
        Validate inputs and provide helpful error messages

    Packaging for Distribution
        Prepare package for distribution via PyPI

    Additional Examples
        examples/example2.py demonstrating advanced usage

    Optional Enhancements
        Request filtering and modification capabilities
        Asynchronous request support
        Logging configuration options

Roadmap

See the Components Checklist for planned features and improvements. Priorities for development:

    Implement Additional Storage Backends
    Develop a Comprehensive Testing Suite
    Enhance Documentation
    Improve Error Handling and Validation
    Prepare for Distribution
    Develop Additional Examples
    Implement Optional Enhancements

Contributing

Contributions are welcome! Please see the CONTRIBUTING.md file for guidelines on how to contribute to this project.
License

This project is licensed under the MIT License - see the LICENSE file for details.

---
