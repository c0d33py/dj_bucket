import logging

from django_tus.models import TusFileModel

logger = logging.getLogger(__name__)


def get_tus_media(data, obj):
    resource_ids = data.split(",")

    for resource_id in resource_ids:
        try:
            file = TusFileModel.objects.get(guid=str(resource_id))
            file.content_object = obj
            file.save()
            logger.info("File uploaded successfully")
        except TusFileModel.DoesNotExist:
            logger.error("File does not exist")
