from rest_framework import serializers

from .models import FileObject


class FileObjectSerializer(serializers.ModelSerializer):
    """File Serializer"""

    class Meta:
        model = FileObject
        fields = '__all__'
