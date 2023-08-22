import os

from celery import Task, shared_task

from django_tus.bucket import S3MultipartUploader


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception, KeyError)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True


@shared_task(base=BaseTaskWithRetry)
def file_load_to_bucket(temp_path, filename, file_size, upload_id):
    s3 = S3MultipartUploader()

    parts = s3.parts_upload(temp_path, filename, file_size, upload_id)

    complete = s3.complete_upload(parts, upload_id, filename)

    location = complete.get('Location')
    print(location)
    os.remove(temp_path)
