from attr import field
from rest_framework import serializers

from .models import TusFileModel


class TusFileSerializer(serializers.ModelSerializer):
    """
    Tus serializer.
    """

    class Meta:
        model = TusFileModel
        fields = '__all__'
