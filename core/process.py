import io
import logging
import os
import uuid
from unittest import result

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage, default_storage
from django.shortcuts import get_object_or_404
from rest_framework import status

from .response import Secure404, SecureResponse

logger = logging.getLogger(__name__)


class FileResource:
    def __init__(self, resource_id):
        self.resource_id = resource_id
        self.client = default_storage.client
        self.bucket = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        self._load_file_info()

    def _load_file_info(self):
        self.filename = cache.get(f"uploads/{self.resource_id}/filename")
        self.file_size = int(cache.get(f"uploads/{self.resource_id}/file_size"))
        self.metadata = cache.get(f"uploads/{self.resource_id}/metadata")
        self.offset = cache.get(f"uploads/{self.resource_id}/offset")

    @staticmethod
    def get_file_or_404(resource_id):
        print('resource get or 404: ', resource_id)

        if FileResource.resource_exists(str(resource_id)):
            return FileResource(resource_id)
        else:
            raise Secure404()

    @staticmethod
    def resource_exists(resource_id: str):
        print('Resource Exist: ', resource_id)
        return cache.get(f"uploads/{resource_id}/filename", None) is not None

    @staticmethod
    def create_initial_file(metadata, file_size: int):
        resource_id = str(uuid.uuid4())

        filename_key = f"uploads/{resource_id}/filename"
        cache.add(filename_key, f"{metadata.get('filename')}")

        file_size_key = f"uploads/{resource_id}/file_size"
        cache.add(file_size_key, file_size)

        offset_key = f"uploads/{resource_id}/offset"
        cache.add(offset_key, 0)

        metadata_key = f"uploads/{resource_id}/metadata"
        cache.add(metadata_key, metadata)

        file = FileResource(resource_id)
        file.write_init_file()

        return file

    def get_path(self):
        return os.path.join(settings.TUS_UPLOAD_DIR, self.resource_id)

    def write_init_file(self):
        try:
            # with open(self.get_path(), 'wb') as f:
            #     f.seek(self.file_size - 1)
            #     f.write(b'\0')
            self.client.put_object(
                self.bucket,
                self.resource_id,
                io.BytesIO(b'\0'),
                1,
            )
        except IOError as e:
            error_message = f"Unable to create file: {e}"
            logger.error(error_message, exc_info=True)
            return SecureResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def write_chunk(self, chunk):
        try:
            # with open(self.get_path(), 'r+b') as f:
            #     f.seek(chunk.offset)
            #     f.write(chunk.content)
            # Upload the chunk to MinIO
            self.client.put_object(
                self.bucket,
                self.resource_id,
                io.BytesIO(chunk.content),
                chunk.chunk_size,
                part_number=chunk.chunk_number,
            )

            offset_key = f"uploads/{self.resource_id}/offset"

            self.offset = cache.incr(offset_key, chunk.chunk_size)

        except IOError:
            logger.error(
                "patch",
                extra={
                    'request': chunk.META,
                    'tus': {
                        "resource_id": self.resource_id,
                        "filename": self.filename,
                        "file_size": self.file_size,
                        "metadata": self.metadata,
                        "offset": self.offset,
                        "upload_file_path": self.get_path(),
                    },
                },
            )
            return SecureResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                reason="Unable to write chunk",
            )
