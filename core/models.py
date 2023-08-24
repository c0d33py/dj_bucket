from django.db import models
from s3_file_field import S3FileField


class UploadedFile(models.Model):
    file = S3FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
