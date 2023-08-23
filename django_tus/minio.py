import os

from django.conf import settings
from django.core.files.storage import default_storage
from tqdm import tqdm

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
            self.client.put_object(
                self.bucket_name,
                f'{get_schema_name()}/{self.filename}',
                file,
                length=-1,
                part_size=10 * 1024 * 1024,
            )

        self._save_uploaded_file_data()
        # Delete the file from the local file system
        os.remove(file_path)

    def _save_uploaded_file_data(self):
        # # Save the uploaded file data to a local file
        file_obj = TusFileModel.objects.get(guid=self.resource_id)
        file_obj.uploaded_file = f'{get_schema_name()}/{self.filename}'
        file_obj.save()

        print(f"Uploaded file data saved: {self.tus_file.filename}")
