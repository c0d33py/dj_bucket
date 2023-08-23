from django.shortcuts import redirect, render
from django.views.generic import View
from rest_framework import permissions, status
from rest_framework.views import APIView

from django_tus.models import TusFileModel

from .forms import PostForm
from .metadata import CustomMetadata
from .models import Post
from .process import FileResource
from .response import TusResponse


class PostView(View):
    template_name = 'tus.html'
    form_class = PostForm

    def get(self, request):
        post_query = TusFileModel.objects.all()
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


class FileUploaderApi(APIView):
    """Create file API View"""

    permission_classes = [permissions.AllowAny]
    metadata_class = CustomMetadata

    def get_metadata(self, request):
        meta = self.metadata_class()
        return meta.determine_metadata(request, self)

    def options(self, request, *args, **kwargs):
        return TusResponse(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        metadata = self.get_metadata(request)

        content_type = metadata.get('filetype', None)
        file_size = int(request.META.get("HTTP_UPLOAD_LENGTH", "0"))

        file = FileResource.create_initial_file(metadata, file_size)

        return TusResponse(
            status=status.HTTP_201_CREATED,
            # headers={'Location': '{}'.format(object_url)},
        )

    def head(self, request, resource_id):
        file = FileResource.get_file_or_404(str(resource_id))
        print('Head: ', file)
        return TusResponse(
            status=status.HTTP_200_OK,
            headers={
                'Upload-Offset': file.offset,
                'Upload-Length': file.file_size,
            },
        )

    def patch(self, request, resource_id, *args, **kwargs):
        file = FileResource.get_file_or_404(str(resource_id))

        return TusResponse(status=status.HTTP_204_NO_CONTENT)


class Chunk:
    def __init__(self, request):
        self.META = request.META
        self.chunk_number = int(request.META.get('HTTP_UPLOAD_OFFSET', 0))
        self.chunk_size = int(request.META.get("CONTENT_LENGTH", 102400))
        self.content = request.body
