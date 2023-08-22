from datetime import timedelta

import requests
from django.conf import settings
from django.core.files.storage import default_storage

from django_tus.models import TusFileModel  # Import your TusFileModel


class MinioUploader:
    def __init__(self, tus_file):
        self.client = default_storage.client
        self.bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        self.tus_file = tus_file
        self.put_presigned_url = self._get_put_presigned_url()

    def _get_put_presigned_url(self):
        return self.client.presigned_put_object(
            self.bucket_name,
            self.tus_file.filename,
            expires=timedelta(minutes=2),
        )

    def upload_file(self, file_path):
        file_data = self._read_file_data(file_path)
        response = self._upload_to_presigned_url(file_data)

        if response.status_code == 200:
            self._save_uploaded_file_data(file_data)

        return response

    def _read_file_data(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()
        return file_data

    def _upload_to_presigned_url(self, file_data):
        headers = {
            'Cache-Control': settings.MINIO_STORAGE_MEDIA_OBJECT_METADATA.get(
                'Cache-Control'
            ),
        }

        response = requests.put(
            self.put_presigned_url,
            data=file_data,
            headers=headers,
        )
        return response

    def _save_uploaded_file_data(self, file_data):
        uploaded_file_name = self.tus_file.filename
        uploaded_file_path = f"{settings.MEDIA_URL}{uploaded_file_name}"

        # Save the uploaded file data to a local file
        with default_storage.open(uploaded_file_path, 'wb') as file:
            file.write(file_data)

        print(f"Uploaded file data saved: {uploaded_file_path}")
