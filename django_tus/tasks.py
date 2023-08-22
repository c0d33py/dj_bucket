import os
from pathlib import Path

from celery import Task, shared_task
from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404

# from django_tus.bucket import S3MultipartUploader
from django_tus.models import TusFileModel


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception, KeyError)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True


def extract_uuid(input_string):
    parts = input_string.split('/')
    if len(parts) == 2:
        return parts[1]
    else:
        return None


def final_path(filename):
    return os.path.join(settings.TUS_DESTINATION_DIR, filename)


@shared_task(base=BaseTaskWithRetry)
def file_load_to_bucket(temp_path, filename, file_size, upload_id, resource_id):
    # s3 = S3MultipartUploader()

    # parts = s3.parts_upload(temp_path, filename, file_size, upload_id)

    # complete = s3.complete_upload(parts, upload_id, filename)
    # location = complete.get('Location', '')

    # os.remove(temp_path)

    file_path = final_path(filename)

    store_file = get_object_or_404(TusFileModel, guid=resource_id)
    # store_file.uploaded_file = location
    # Save the uploaded file to the path specified in the FileField's upload_to argument
    print('uploading...')
    print(file_path)
    default_storage.save(store_file.uploaded_file, file_path)
    # store_file.save()
    print('Uploading Done!')
