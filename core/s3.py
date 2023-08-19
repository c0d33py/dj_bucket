import os
import uuid

import boto3


class S3Client:
    def __init__(self, *args, **kwargs):
        self.key = uuid.uuid4()
        self.bucket_name = 'cbs0'
        self.access_key = os.getenv('AWS_ACCESS_KEY')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.endpoint_url = os.getenv('AWS_DOMAIN')
        self.region_name = ''
        self.s3 = self._create_s3_client()

    def _create_s3_client(self):
        return boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
        )

    def get_multipart(self, file_name, file_type):
        # Initialize a multipart upload
        response = self.s3.create_multipart_upload(
            Bucket=self.bucket_name,
            Key=file_name,
            ACL="public-read-write",
            ContentType=file_type,
            CacheControl="max-age=1000",
        )
        upload_id = response['UploadId']

        return upload_id

    def upload_file(self, tmp_path, file_name, file_size, upload_id):
        try:
            # Determine part size and number of parts
            part_size = 5 * 1024 * 1024  # 5MB
            file_size = file_size
            num_parts = (file_size + part_size - 1) // part_size

            # Upload parts
            parts = []
            with open(str(tmp_path), 'r+b') as f:
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
        except Exception as e:
            return False, str(e)

    def get_complete_upload(self, parts, upload_id, file_name):
        completeResult = self.s3.complete_multipart_upload(
            Bucket=self.bucket_name,
            Key=file_name,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts},
        )
        return completeResult
