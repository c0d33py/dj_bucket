from datetime import timedelta
from unittest import result

import requests
from django.conf import settings
from django.core.files.storage import default_storage

from django_tus.models import TusFileModel  # Import your TusFileModel
from minio import Minio


class MinioUploader:
    def __init__(self, tus_file):
        self.client = default_storage.client
        self.bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        self.tus_file = tus_file
        self.put_presigned_url = self.get_put_presigned_url()

    def get_put_presigned_url(self):
        return self.client.presigned_put_object(
            self.bucket_name,
            self.tus_file.filename,
            expires=timedelta(minutes=2),
        )

    def upload_file(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()

        response = requests.put(
            self.put_presigned_url,
            data=file_data,
            headers={
                'Cache-Control': settings.MINIO_STORAGE_MEDIA_OBJECT_METADATA.get(
                    'Cache-Control'
                ),
            },
        )
        print(response)
        return response
