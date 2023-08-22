import base64
import logging
import zipfile

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from django_tus.conf import settings
from django_tus.metadata import TusMetadata
from django_tus.models import TusFileModel
from django_tus.response import TusResponse
from django_tus.serializers import TusFileSerializer
from django_tus.tusfile import TusChunk, TusFile
from django_tus.utils import validate_filename

logger = logging.getLogger(__name__)

TUS_SETTINGS = {}


class TusUpload(views.APIView):
    """Upload file to server"""

    permission_classes = [permissions.IsAuthenticated]
    metadata_class = TusMetadata

    on_finish = None

    # @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        if not self.request.META.get("HTTP_TUS_RESUMABLE"):
            return TusResponse(
                status=status.HTTP_405_METHOD_NOT_ALLOWED, content="Method Not Allowed"
            )

        override_method = self.request.META.get('HTTP_X_HTTP_METHOD_OVERRIDE')
        if override_method:
            self.request.method = override_method
        return super(TusUpload, self).dispatch(*args, **kwargs)

    def finished(self):
        if self.on_finish is not None:
            self.on_finish()

    def get_metadata(self, request):
        meta = self.metadata_class()
        return meta.determine_metadata(request, self)

    def options(self, request, *args, **kwargs):
        return TusResponse(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        metadata = self.get_metadata(request)
        metadata["filename"] = validate_filename(metadata)

        message_id = request.META.get("HTTP_MESSAGE_ID")
        if message_id:
            metadata["message_id"] = base64.b64decode(message_id)

        if (
            settings.TUS_EXISTING_FILE == 'error'
            and settings.TUS_FILE_NAME_FORMAT == 'keep'
            and TusFile.check_existing_file(metadata.get("filename"))
        ):
            return TusResponse(
                status=status.HTTP_409_CONFLICT,
                reason="File with same name already exists",
            )

        file_size = int(request.META.get("HTTP_UPLOAD_LENGTH", "0"))
        tus_file = TusFile.create_initial_file(metadata, file_size)

        return TusResponse(
            status=status.HTTP_201_CREATED,
            extra_headers={
                'Location': '{}{}'.format(
                    request.build_absolute_uri(), tus_file.resource_id
                )
            },
        )

    def head(self, request, resource_id):
        tus_file = TusFile.get_tusfile_or_404(str(resource_id))
        return TusResponse(
            status=status.HTTP_200_OK,
            extra_headers={
                'Upload-Offset': tus_file.offset,
                'Upload-Length': tus_file.file_size,
            },
        )

    def patch(self, request, resource_id, *args, **kwargs):
        tus_file = TusFile.get_tusfile_or_404(str(resource_id))
        chunk = TusChunk(request)

        if not tus_file.is_valid():
            return TusResponse(status=status.HTTP_410_GONE)

        if chunk.offset != tus_file.offset:
            return TusResponse(status=status.HTTP_409_CONFLICT)

        if chunk.offset > tus_file.file_size:
            return TusResponse(status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        tus_file.write_chunk(chunk=chunk)

        if tus_file.is_complete():
            # file transfer complete, rename from resource id to actual filename
            tus_file.rename()
            tus_file.s3_object_upload()
            tus_file.clean()

            self.finished()

        return TusResponse(
            status=status.HTTP_204_NO_CONTENT,
            extra_headers={'Upload-Offset': tus_file.offset},
        )

    def delete(self, request, resource_id, *args, **kwargs):
        try:
            tus_file = TusFile.get_tusfile_or_404(str(resource_id))
            tus_file.get_existing_object(resource_id).delete()
            tus_file.clean()
        except Exception as e:
            TusFileModel.objects.filter(guid=resource_id).delete()
        return TusResponse(status=status.HTTP_204_NO_CONTENT)


class TusUploadDelete(views.APIView):
    """Delete file and remove from database"""

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, resource_id=None, format=None):
        objects = get_object_or_404(TusFileModel, guid=resource_id)
        objects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TusDownloadFile(views.APIView):
    """Download file from server"""

    permission_classes = [permissions.AllowAny]

    def get(self, request, content_type=None, object_id=None, format=None):
        file_name = request.GET.get('filename')
        queryset = TusFileModel.objects.filter(
            content_type__model=content_type, object_id=object_id
        )

        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{file_name}.zip"'

        with zipfile.ZipFile(response, 'w') as zip_file:
            for objects in queryset:
                if objects.uploaded_file is None:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                file = objects.uploaded_file
                zip_file.writestr(objects.filename, file.read())

        return response


class TusFilesListAPI(generics.ListAPIView):
    """Files list api view"""

    serializer_class = TusFileSerializer

    def get_queryset(self):
        content_type = self.kwargs.get('content_type')
        object_id = self.kwargs.get('object_id')
        if content_type and object_id:
            queryset = TusFileModel.objects.filter(
                content_type__model=content_type,
                object_id=object_id,
            )
        return queryset
