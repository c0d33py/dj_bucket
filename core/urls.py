from re import I

from django.urls import path
from django.views.generic import TemplateView

from .views import FileUploaderApi, PostView

urlpatterns = [
    path('', PostView.as_view(), name='post_view'),
    path('files/', FileUploaderApi.as_view(), name='file_upload_api'),
    path('uppy/', TemplateView.as_view(template_name='uppy.html'), name="uppy"),
]
