import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from django_tus.response import Tus404, TusResponse

logger = logging.getLogger(__name__)


class S3MultipartUploader:
    def __init__(self, *args, **kwargs):
        self.bucket_name = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
        self.access_key = settings.MINIO_STORAGE_ACCESS_KEY
        self.secret_key = settings.MINIO_STORAGE_SECRET_KEY
        self.endpoint_url = f'https://{settings.MINIO_STORAGE_ENDPOINT}'
        self.region_name = ''
        self.s3 = self._create_s3_client()

    def _create_s3_client(self):
        return boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
        )

    def generate_multipart_upload(self, filename, content_type, metadata):
        # Initialize a multipart upload
        response = self.s3.create_multipart_upload(
            Bucket=self.bucket_name,
            Key=filename,
            ACL="public-read-write",
            ContentType=content_type,
            CacheControl="max-age=1000",
            Metadata=metadata,
        )
        upload_id = response['UploadId']

        return upload_id

    def parts_upload(
        self, tmp_path: str, file_name: str, file_size: int, upload_id: str
    ):
        try:
            # Determine part size and number of parts
            part_size = 5 * 1024 * 1024  # 5MB
            file_size = file_size
            num_parts = (file_size + part_size - 1) // part_size

            # Upload parts
            parts = []
            with open(tmp_path, 'r+b') as f:
                for part_number in range(1, num_parts + 1):
                    data = f.read(part_size)

                    response = self.s3.upload_part(
                        Bucket=self.bucket_name,
                        Key=file_name,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=data,
                    )
                    parts.append({'PartNumber': part_number, 'ETag': response['ETag']})

            return parts
        except (BotoCoreError, ClientError) as e:
            # Handle the exception here
            print("Error uploading parts:", e)
            return None

    def complete_upload(self, parts: list, upload_id: str, file_name: str):
        try:
            completeResult = self.s3.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=file_name,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts},
            )

            return completeResult
        except (BotoCoreError, ClientError) as e:
            # Handle the exception here
            print("Error completing multipart upload:", e)
            return None
