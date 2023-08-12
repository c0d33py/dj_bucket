from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.views.generic import View
from rest_framework.generics import ListCreateAPIView

from .forms import PostForm
from .models import FileObject, Post
from .serializers import FileObjectSerializer


class PostView(View):
    template_name = 'post.html'
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


class FileUploaderApi(ListCreateAPIView):
    """Create file API View"""

    serializer_class = FileObjectSerializer
    queryset = FileObject.objects.all()

    def get(self, request, *args, **kwargs):
        client = default_storage.client

        print('Client: ', client)
        return super().get(request, *args, **kwargs)
