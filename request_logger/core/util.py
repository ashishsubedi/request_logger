
import base64
from typing import Any, Dict, Optional


class RequestUtil:
    @staticmethod
    def parse_request_kwargs(request_data: Dict[str, Any]) -> Dict[str, Any]:

        headers = request_data.get('headers')
        data = request_data.get('data')
        json_data = request_data.get('json')

        # Reconstruct data
        if data:
            if data.get('is_base64'):
                data_content = base64.b64decode(data['content'])
            else:
                data_content = data['content']
        else:
            data_content = None

        files = RequestUtil.reconstruct_files(request_data.get('files'))
        
        request_kwargs = {
            'headers': headers,
            'data': data_content,
            'json': json_data,
            'files': files,
        }
        request_kwargs = {k: v for k, v in request_kwargs.items() if v is not None}

        return request_kwargs

    @staticmethod
    def reconstruct_files( files_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not files_data:
            return None

        reconstructed_files = {}
        for key, file_info in files_data.items():
            filename = file_info.get('filename')
            encoded_content = file_info.get('content')
            content_type = file_info.get('content_type')

            # Decode the base64 content
            file_content = base64.b64decode(encoded_content)

            # Reconstruct the file tuple
            file_tuple = (filename, file_content)
            if content_type:
                file_tuple += (content_type,)
            reconstructed_files[key] = file_tuple
        return reconstructed_files
