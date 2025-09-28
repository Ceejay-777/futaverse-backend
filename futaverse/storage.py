# your_app/storage.py
from django.core.files.storage import Storage
from supabase import create_client
from django.conf import settings
import uuid
import os
import io

class SupabaseStorage(Storage):
    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        self.bucket_name = settings.SUPABASE_BUCKET_NAME

    def _save(self, name, content):
        file_extension = os.path.splitext(name)[1]
        unique_name = f"resumes/{uuid.uuid4()}{file_extension}"
        
        content.seek(0)
        self.client.storage.from_(self.bucket_name).upload(
            path=unique_name,
            file=content.read(),
            file_options={"content-type": getattr(content, 'content_type', 'application/octet-stream')}
        )
        
        return unique_name

    def url(self, name):
        return self.client.storage.from_(self.bucket_name).get_public_url(name)

    def exists(self, name):
        return False  # Always generate new files

    def delete(self, name):
        try:
            self.client.storage.from_(self.bucket_name).remove([name])
        except:
            pass

    def size(self, name):
        return 0