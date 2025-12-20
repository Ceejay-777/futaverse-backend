from django.db import transaction

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from drf_spectacular.utils import extend_schema

from .serializers import EventSerializer
from .models import Event, VirtualMeeting
from .utils import GoogleCalendarService, get_user_credentials, GoogleAuthRequired, GoogleAuthRequiredException

import uuid

@extend_schema(tags=['Events'], summary="Create an event")
class CreateEventView(generics.CreateAPIView):
    serializer_class = EventSerializer
    # permission_classes = []
    # queryset = Event.objects.all()
    
    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        
        validated_data = serializer.validated_data
        
        mode = validated_data.get("mode")
        redirect_after_auth = validated_data.pop("redirect_after_auth", None)
        platform = validated_data.pop("platform", None)
        
        event: Event = serializer.save(creator=user, **validated_data)
        
        if mode in [Event.Mode.VIRTUAL, Event.Mode.HYBRID]:
            print(f"Creating virtual meeting for {event.title} with mode {mode} and platform {platform}")
            try:
                print("Getting credentials")
                credentials = get_user_credentials(user, redirect_after_auth)
                print(credentials)
                
            except GoogleAuthRequired as e:
                raise PermissionDenied({
                    "detail": "Authenticate with Google",
                    "error": "AUTH_REQUIRED",
                    "auth_url": e.auth_url
                })
                            
            service = GoogleCalendarService(credentials)
            
            if platform == VirtualMeeting.Platform.GOOGLE_MEET:
                room_name = None
                google_event = service.create_event(event, [user.email])
                join_url = google_event.get('hangoutLink')
                external_calendar_event_id = google_event.get('id')
                
            if platform == VirtualMeeting.Platform.JITSI:
                room_name = f"App-{uuid.uuid4().hex}"
                join_url = f"https://meet.jit.si/{room_name}"
                google_event = service.create_event(event, [user.email], manual_join_url=join_url)
                external_calendar_event_id = google_event.get('id')
                
            VirtualMeeting.objects.create(event=event, platform=platform, join_url=join_url, external_calendar_event_id=external_calendar_event_id, room_name=room_name)
                
            