import base64

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage, default_storage
from django.shortcuts import redirect, render
from django.views.generic import View
from minio_storage.storage import MinioMediaStorage
from pathvalidate._filename import is_valid_filename
from rest_framework import metadata, permissions, status
from rest_framework.metadata import BaseMetadata
from rest_framework.views import APIView

from .forms import PostForm
from .models import FileObject, Post
from .process import FileResource
from .response import SecureResponse
from .serializers import FileObjectSerializer


class PostView(View):
    template_name = 'tus.html'
    form_class = PostForm

    def get(self, request):
        post_query = Post.objects.all()
        form = self.form_class()

        context = {'posts': post_query, 'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            form.save()

            return redirect('/')

        return render(request, self.template_name, {"form": form})


class CustomMetadata(BaseMetadata):
    def determine_metadata(self, request, view):
        metadata = {}

        upload_metadata = request.META.get("HTTP_UPLOAD_METADATA")

        if upload_metadata:
            for kv in upload_metadata.split(","):
                key, value = kv.split(" ", 1) if " " in kv else (kv, "")
                decoded_value = base64.b64decode(value).decode()
                metadata[key] = decoded_value

        return metadata


class FileUploaderApi(APIView):
    """Create file API View"""

    permission_classes = [permissions.AllowAny]
    metadata_class = CustomMetadata

    def get_metadata(self, request):
        meta = self.metadata_class()
        return meta.determine_metadata(request, self)

    def options(self, request, *args, **kwargs):
        return SecureResponse(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        metadata = self.get_metadata(request)

        file_size = int(request.META.get("HTTP_UPLOAD_LENGTH", "0"))
        file = FileResource.create_initial_file(metadata, file_size)
        client = default_storage.client

        object_url = client.presigned_get_object(
            settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
            file.resource_id,
        )

        return SecureResponse(
            status=status.HTTP_201_CREATED,
            # headers={'Location': '{}'.format(object_url)},
            headers={
                'Location': '{}{}'.format(
                    request.build_absolute_uri(), file.resource_id
                )
            },
        )

    def head(self, request, resource_id):
        file = FileResource.get_file_or_404(str(resource_id))
        print('Head: ', file)
        return SecureResponse(
            status=status.HTTP_200_OK,
            headers={
                'Upload-Offset': file.offset,
                'Upload-Length': file.file_size,
            },
        )

    def patch(self, request, resource_id, *args, **kwargs):
        file = FileResource.get_file_or_404(str(resource_id))
        print(file)
        return SecureResponse(status=status.HTTP_204_NO_CONTENT)
