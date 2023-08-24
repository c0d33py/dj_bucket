from django.shortcuts import redirect, render

from .forms import UploadedFileForm


def home(request):
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UploadedFileForm()
    return render(request, 'post.html', {'form': form})
