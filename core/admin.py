from django.contrib import admin

from .models import FileObject, Post

admin.site.register(Post)
admin.site.register(FileObject)
