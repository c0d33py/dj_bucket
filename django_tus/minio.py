import os

from django.conf import settings
from django.core.files.storage import default_storage

from django_tus.connection import get_schema_name
from django_tus.models import TusFileModel


class MinioUploader:
    def __init__(self, tus_file):
        self.client = default_storage.client
        self.bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        self.tus_file = tus_file
        self.filename = self.tus_file.filename
        self.resource_id = self.tus_file.resource_id

    def upload_file(self, file_path):
        with open(file_path, 'rb') as file:
            self._upload_to_minio(file)

        self._save_uploaded_file_data()
        self._delete_local_file(file_path)

    def _upload_to_minio(self, file):
        object_key = f'{get_schema_name()}/{self.filename}'
        self.client.put_object(
            self.bucket_name,
            object_key,
            file,
            length=-1,
            part_size=10 * 1024 * 1024,
        )

    def _save_uploaded_file_data(self):
        file_obj = TusFileModel.objects.get(guid=self.resource_id)
        uploaded_file_path = f'{get_schema_name()}/{self.filename}'
        file_obj.uploaded_file = uploaded_file_path
        file_obj.save()

        print(f"Uploaded file data saved: {self.filename}")

    def _delete_local_file(self, file_path):
        os.remove(file_path)
