import base64

from rest_framework.metadata import BaseMetadata


class TusMetadata(BaseMetadata):
    def determine_metadata(self, request, view):
        metadata = {}

        upload_metadata = request.META.get("HTTP_UPLOAD_METADATA")

        if upload_metadata:
            for kv in upload_metadata.split(","):
                key, value = kv.split(" ", 1) if " " in kv else (kv, "")
                decoded_value = base64.b64decode(value).decode()
                metadata[key] = decoded_value

        return metadata
