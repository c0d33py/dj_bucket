from ast import mod

from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=100, blank=True)
    file = models.FileField()

    def __str__(self):
        return self.title
