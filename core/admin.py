from django.contrib import admin

from .models import FileObject, Post, S3Object

admin.site.register(Post)
admin.site.register(S3Object)
