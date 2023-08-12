import random

from django.db import models
from django.utils import timezone


def generate_random_string(length=16):
    """Generate a random string of given length."""
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(characters) for _ in range(length))


class Post(models.Model):
    title = models.CharField(max_length=100, blank=True)
    file = models.FileField()

    def __str__(self):
        return self.title


class FileObject(models.Model):
    """Default model for a tus file upload."""

    id = models.CharField(
        max_length=16,
        default=generate_random_string,
        unique=True,
        primary_key=True,
        db_index=True,
        verbose_name="File ID",
        editable=False,
    )
    filename = models.CharField(max_length=255, blank=True, verbose_name="File Name")
    length = models.BigIntegerField(default=-1, verbose_name="File Length")
    offset = models.BigIntegerField(default=0, verbose_name="Offset")
    metadata = models.JSONField(default=dict, verbose_name="Metadata")
    tmp_path = models.CharField(
        max_length=4096, null=True, verbose_name="Temporary Path"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Expiration Date"
    )
    file = models.FileField(upload_to='uploads/', verbose_name="File")

    def __str__(self):
        return self.filename or self.id

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"

    def is_expired(self):
        """Check if the file has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    is_expired.boolean = True
    is_expired.short_description = "Expired"

    @property
    def url(self):
        return self.file.url

    @property
    def size_in_kb(self):
        """Return the size of the file in kilobytes."""
        return round(self.length / 1024, 2)
