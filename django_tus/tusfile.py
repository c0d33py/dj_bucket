import logging
import os
import random
import shutil
import string
import uuid
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from rest_framework import status

from django_tus.bucket import S3MultipartUploader
from django_tus.connection import get_schema_name
from django_tus.response import Tus404, TusResponse
from django_tus.tasks import file_load_to_bucket

logger = logging.getLogger(__name__)


class FilenameGenerator:
    COMPANY_NAME = 'CbMedia'

    def __init__(self, filename: str = None):
        self.filename = filename or self.random_string()

    def get_name_and_extension(self):
        return os.path.splitext(self.filename)

    def create_random_suffix_name(self) -> str:
        name, extension = self.get_name_and_extension()
        random_string = self.random_string()
        return f'{self.COMPANY_NAME}_{random_string}{extension}'

    @classmethod
    def random_string(cls, length: int = 11) -> str:
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))


class TusFile:
    s3 = S3MultipartUploader()

    def __init__(self, resource_id: str):
        self.resource_id = resource_id
        self._load_data_from_cache()

    def _load_data_from_cache(self):
        self.filename = cache.get(f'tus-uploads/{self.resource_id}/filename')
        self.file_size = self._get_cache_value_as_int('file_size')
        self.metadata = cache.get(f'tus-uploads/{self.resource_id}/metadata')
        self.offset = cache.get(f'tus-uploads/{self.resource_id}/offset')
        self.upload_id = cache.get(f'tus-uploads/{self.resource_id}/upload_id')

    def _get_cache_value_as_int(self, key):
        value = cache.get(f'tus-uploads/{self.resource_id}/{key}')
        return int(value) if value else 0

    @classmethod
    def get_tusfile_or_404(cls, resource_id: str):
        if cls.resource_exists(resource_id):
            return cls(resource_id)
        raise Tus404()

    @staticmethod
    def resource_exists(resource_id: str):
        return cache.get(f'tus-uploads/{resource_id}/filename') is not None

    @staticmethod
    def create_initial_file(metadata, file_size: int):
        resource_id = str(uuid.uuid4())
        filename = metadata.get('filename')
        file_name = FilenameGenerator(filename).create_random_suffix_name()

        content_type = metadata.get('filetype')
        upload_id = TusFile.s3.generate_multipart_upload(
            file_name, content_type, metadata
        )

        cache_data = {
            'filename': file_name,
            'file_size': file_size,
            'offset': 0,
            'metadata': metadata,
            'upload_id': upload_id,
        }

        for key, value in cache_data.items():
            cache.add(f'tus-uploads/{resource_id}/{key}', value)

        tus_file = TusFile(resource_id)
        tus_file.write_init_file()

        return tus_file

    def is_valid(self):
        return self.filename and os.path.lexists(self.file_path())

    def file_path(self):
        return str(Path(settings.TUS_UPLOAD_DIR) / self.resource_id)

    def rename(self):
        """If Not used bucket storage"""  # TODO
        self.filename = FilenameGenerator(self.filename).create_random_suffix_name()
        destination = Path(settings.TUS_DESTINATION_DIR) / self.filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(self.file_path()), str(destination))

    def s3_object_upload(self):
        file_load_to_bucket.delay(
            self.file_path(), self.filename, self.file_size, self.upload_id
        )
        # parts = self.s3.parts_upload(
        #     self.file_path(), self.filename, self.file_size, self.upload_id
        # )
        # print(parts)

        # self.s3.complete_upload(parts, self.upload_id, self.filename)
        # print('remove temp file...')
        # os.remove(self.file_path())

    def clean(self):
        cache_keys = [
            'file_size',
            'filename',
            'offset',
            'metadata',
            'upload_id',
        ]
        cache.delete_many(
            [f'tus-uploads/{self.resource_id}/{key}' for key in cache_keys]
        )

    @staticmethod
    def check_existing_file(filename: str):
        return os.path.lexists(os.path.join(get_schema_name(), filename))

    def write_init_file(self):
        try:
            with open(self.file_path(), 'wb') as f:
                if self.file_size > 0:
                    f.seek(self.file_size - 1)
                    f.write(b'\0')
        except IOError as e:
            error_message = f'Unable to create file: {e}'
            logger.error(error_message, exc_info=True)
            return TusResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, reason=error_message
            )

    def write_chunk(self, chunk):
        try:
            with open(self.file_path(), 'r+b') as f:
                f.seek(chunk.offset)
                f.write(chunk.content)

            new_offset = cache.incr(
                f'tus-uploads/{self.resource_id}/offset',
                chunk.chunk_size,
            )
            self.offset = new_offset  # Update offset only if cache.incr succeeds
        except IOError as e:
            logger.error(
                'patch',
                extra={
                    'request': chunk.META,
                    'tus': {
                        'resource_id': self.resource_id,
                        'filename': self.filename,
                        'file_size': self.file_size,
                        'metadata': self.metadata,
                        'offset': self.offset,
                        'upload_file_path': self.file_path(),
                    },
                },
            )
            return TusResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                reason=f'Unable to write chunk: {e}',
            )

    def is_complete(self):
        return self.offset == self.file_size

    def __str__(self):
        return f'{self.filename} ({self.resource_id})'


class TusChunk:
    def __init__(self, request):
        self.META = request.META
        self.offset = int(request.META.get('HTTP_UPLOAD_OFFSET', 0))
        self.chunk_size = int(request.META.get('CONTENT_LENGTH', 102400))
        self.content = request.body
