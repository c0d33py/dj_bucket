from django.urls import path

from .views import TusDownloadFile, TusFilesListAPI, TusUpload, TusUploadDelete

urlpatterns = [
    path('upload/', TusUpload.as_view(), name='tus_upload'),
    path('upload/<uuid:resource_id>', TusUpload.as_view(), name='tus_upload'),
    path(
        'upload/delete/<uuid:resource_id>',
        TusUploadDelete.as_view(),
        name='tus_upload_delete',
    ),
    path(
        'files/<str:content_type>/<int:object_id>/',
        TusFilesListAPI.as_view(),
        name='files_list_api',
    ),
    path(
        'download/<str:content_type>/<int:object_id>/',
        TusDownloadFile.as_view(),
        name='tus_download_file',
    ),
]
