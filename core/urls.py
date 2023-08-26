from django.urls import include, path
from rest_framework import routers

from . import rest
from .views import home

router = routers.DefaultRouter()
router.register('resources', rest.UploadedFileViewSet, basename='api')

urlpatterns = [
    path('', home, name='home'),
    path('api/', include(router.urls)),
]
