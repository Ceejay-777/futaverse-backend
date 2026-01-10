from django.db import transaction
from django.db.models import F

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from .serializers import EventSerializer, CreateTicketSerializer, TicketPurchaseSerializer, UpdateEventSerializer
from .models import Event, VirtualMeeting, Ticket, TicketPurchase
from .services import EventRegistrationService, GoogleCalendarService, get_user_credentials, GoogleAuthRequired

from futaverse.utils.email_service import BrevoEmailService
from payments.requests import initialize_transaction

import uuid
import logging

mailer = BrevoEmailService()
logger = logging.getLogger(__name__)

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
            try:
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
            
@extend_schema(tags=['Events'], summary="Add ticket for an event")
class CreateTicketView(generics.CreateAPIView):
    serializer_class = CreateTicketSerializer
            
@extend_schema(tags=['Events'], summary="Register for an event")
class CreateTicketPurchaseView(generics.CreateAPIView):
    serializer_class = TicketPurchaseSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        create_response = self.perform_create(serializer)
        
        if create_response:
            return Response({
                "checkout_url": create_response,
                "message": "Payment required to complete registration"
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @transaction.atomic
    def perform_create(self, serializer):
        #TODO: Handle when action is not performed by user
        
        user = self.request.user
        validated_data = serializer.validated_data
        ticket: Ticket = validated_data.get("ticket")
        event = ticket.event
        
        ticket_uid = uuid.uuid4().hex 
        
        is_free = ticket.sales_price == 0 or ticket.type == Ticket.Type.DEFAULT
        
        ticket_purchase = TicketPurchase.objects.create(user=user, ticket=ticket, is_paid=is_free, ticket_uid=ticket_uid, email=user.email)
             
        if is_free:
            Ticket.objects.filter(id=ticket.id).update(quantity_sold=F('quantity_sold') + 1)
            
            if event.mode in [Event.Mode.VIRTUAL, Event.Mode.HYBRID]:
                EventRegistrationService.sync_to_calendar(event)
                
            EventRegistrationService.send_ticket_email(ticket_purchase)
            
            return None
            
        else:
            authorization_url = initialize_transaction({
                "amount": int(ticket.sales_price * 100), 
                "email": user.email,
                "reference": str(ticket_uid)
            })
            
            return authorization_url

@extend_schema(tags=['Events'], summary="Update an event")     
class UpdateEventView(generics.UpdateAPIView):
    serializer_class = UpdateEventSerializer
    queryset = Event.objects.all()
    lookup_field = 'sqid'
            
            