from django.contrib import admin

from django_tus.models import TusFileModel


@admin.register(TusFileModel)
class UploadAdmin(admin.ModelAdmin):
    list_display = [
        'guid',
        'filename',
        'length',
        'offset',
        'created_at',
    ]
    list_filter = ['created_at', 'expires_at']
    search_fields = ['guid', 'filename']
    readonly_fields = ['guid', 'filename', 'length', 'tmp_path', 'created_at', 'expires_at']
    ordering = ['-created_at']
    list_per_page = 20
