import base64

from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.views.generic import View
from rest_framework import metadata, permissions, status
from rest_framework.metadata import BaseMetadata
from rest_framework.views import APIView

from .forms import PostForm
from .models import FileObject, Post
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

    def options(self, request, *args, **kwargs):
        return SecureResponse(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        custom_metadata = self.metadata_class()
        metadata = custom_metadata.determine_metadata(request, self)
        print(request.META)
        return SecureResponse(status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        return SecureResponse(status=status.HTTP_204_NO_CONTENT)
