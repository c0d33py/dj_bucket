import os
import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes import models as ctype_models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from django_tus.connection import get_schema_name

User = get_user_model()


class AbstractUpload(models.Model):
    '''The model for a tus file metadata.'''

    guid = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='GUID')
    filename = models.CharField(max_length=255, blank=True)
    length = models.BigIntegerField(default=-1)
    offset = models.BigIntegerField(default=0)
    metadata = models.JSONField(default=dict)
    tmp_path = models.CharField(max_length=4096, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class TusFileModel(AbstractUpload):
    '''Default model for a tus file upload.'''

    uploaded_file = models.FileField(
        upload_to=get_schema_name, blank=True, null=True, max_length=255
    )
    content_type = models.ForeignKey(
        ctype_models.ContentType,
        related_name='tusfilemodel',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(
        User,
        verbose_name='user that uploads the file',
        related_name='tusfilemodel',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = 'Tus File'
        verbose_name_plural = 'Tus Files'
        ordering = ['-id']

    def __str__(self):
        return str(self.guid)

    def delete(self, *args, **kwargs):
        try:
            os.remove(self.tmp_path)
        except FileNotFoundError:
            os.remove(self.uploaded_file.path)
        super().delete(*args, **kwargs)
