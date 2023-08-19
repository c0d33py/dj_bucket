from minio_storage.storage import MinioMediaStorage


class S3MinioStorage(MinioMediaStorage):
    """Custom storage using multpart upload"""
