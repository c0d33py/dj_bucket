import re
from email import header

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

tus_api_version = '1.0.0'
tus_api_version_supported = [
    '1.0.0',
]
tus_api_extensions = ['creation', 'termination', 'file-check']


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Not found.'
    default_code = 'not_found'


class SecureResponse(Response):
    def __init__(self, headers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.base_tus_headers = {
            'Tus-Resumable': tus_api_version,
            'Tus-Version': ",".join(tus_api_version_supported),
            'Tus-Extension': ",".join(tus_api_extensions),
            # 'Tus-Max-Size': settings.TUS_MAX_FILE_SIZE, TODO: Need to be checked the file size
            'Access-Control-Expose-Headers': "Tus-Resumable,upload-length,upload-metadata,Location,Upload-Offset",
            'Access-Control-Allow-Headers': "Tus-Resumable,upload-length,upload-metadata,Location,Upload-Offset,content-type",
            'Cache-Control': 'no-store',
        }

        self.sanitize_headers(self.base_tus_headers)
        if headers:
            self.sanitize_headers(headers)

    def sanitize_headers(self, headers: dict):
        for key, value in headers.items():
            if not re.match(r'^[a-zA-Z0-9_-]+$', key):
                raise ValueError(f'Invalid header name: {key}')

            if not value:
                raise ValueError(f'Invalid header value: {value}')

            self.__setitem__(key, value)


class Secure404(SecureResponse, NotFound):
    pass