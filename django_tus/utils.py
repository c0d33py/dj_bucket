import logging

from pathvalidate._filename import is_valid_filename

from django_tus.models import TusFileModel
from django_tus.tusfile import FilenameGenerator

logger = logging.getLogger(__name__)


def get_tus_media(data: list, obj: int):
    resource_ids = data.split(",")

    for resource_id in resource_ids:
        try:
            file = TusFileModel.objects.get(guid=str(resource_id))
            file.content_object = obj
            file.save()
            logger.info("File uploaded successfully")
        except TusFileModel.DoesNotExist:
            logger.error("File does not exist")


def validate_filename(metadata: dict):
    filename = metadata.get("filename", "")
    if not is_valid_filename(filename):
        filename = FilenameGenerator.random_string(16)
    return filename
