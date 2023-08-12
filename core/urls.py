from django.urls import path

from .views import FileUploaderApi, PostView

urlpatterns = [
    path('', PostView.as_view(), name='post_view'),
    path('files/', FileUploaderApi.as_view(), name='file_upload_api'),
]
