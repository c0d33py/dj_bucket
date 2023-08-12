from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.views.generic import View
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import PostForm
from .models import FileObject, Post
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


class FileUploaderApi(APIView):
    """Create file API View"""

    permission_classes = [permissions.AllowAny]

    def get(self, requset, *args, **kwargs):
        return Response({'data': True})

    def post(self, request, *args, **kwargs):
        print(request)
        return Response(status=status.HTTP_201_CREATED)
