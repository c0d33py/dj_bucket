import base64
from os import PathLike, fspath

from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.views.generic import View
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import PostForm
from .metadata import CustomMetadata
from .minio import S3MinioStorage
from .models import Post
from .process import FileResource
from .response import SecureResponse


class PostView(View):
    template_name = 'tus.html'
    form_class = PostForm

    def get(self, request):
        post_query = Post.objects.all()
        form = self.form_class()

        client = S3MinioStorage()

        print(client.client)

        context = {'posts': post_query, 'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            form.save()

            return redirect('/')

        return render(request, self.template_name, {"form": form})


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
        file_name = fspath(metadata.get('filename'))
        print(isinstance(file_name, PathLike))

        file_size = int(request.META.get("HTTP_UPLOAD_LENGTH", "0"))
        file = FileResource.create_initial_file(metadata, file_size)
        client = default_storage.client
        object_url = client.get_presigned_url(
            'GET',
            settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
            file.resource_id,
        )

        return SecureResponse(
            status=status.HTTP_201_CREATED,
            headers={'Location': '{}'.format(object_url)},
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


class Chunk:
    def __init__(self, request):
        self.META = request.META
        self.chunk_number = int(request.META.get('HTTP_UPLOAD_OFFSET', 0))
        self.chunk_size = int(request.META.get("CONTENT_LENGTH", 102400))
        self.content = request.body
