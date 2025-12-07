from django.shortcuts import render
from rest_framework import generics

from drf_spectacular.utils import extend_schema

from .serializers import EventSerializer
from .models import Event

# Create your views here.

@extend_schema(tags=['Events'], summary="Create an event")
class CreateEventView(generics.CreateAPIView):
    serializer_class = EventSerializer
    # queryset = Event.objects.all()
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(creator=user)
    