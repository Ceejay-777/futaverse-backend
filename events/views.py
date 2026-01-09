from django.db import transaction
from django.db.models import F
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from drf_spectacular.utils import extend_schema

from .serializers import EventSerializer, TicketSerializer, CreateTicketSerializer, TicketPurchaseSerializer
from .models import Event, VirtualMeeting, Ticket, TicketPurchase
from .utils import GoogleCalendarService, get_user_credentials, GoogleAuthRequired

from futaverse.utils.email_service import BrevoEmailService

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
    
    @transaction.atomic
    def perform_create(self, serializer):
        #TODO: Handle when action is not performed by user
        
        user = self.request.user
        validated_data = serializer.validated_data
        ticket: Ticket = validated_data.get("ticket")
        event = ticket.event
        
        ticket_uid = uuid.uuid4().hex 
        
        is_free = ticket.sales_price == 0 or ticket.type == Ticket.Type.DEFAULT
        is_virtual = event.mode == Event.Mode.VIRTUAL 
        is_hybrid = event.mode == Event.Mode.HYBRID
        
        ticket_purchase = TicketPurchase.objects.create(user=user, ticket=ticket, is_paid=is_free, ticket_uid=ticket_uid, email=user.email)
             
        if is_free:
            Ticket.objects.filter(id=ticket.id).update(quantity_sold=F('quantity_sold') + 1)
            
            if event.mode in [Event.Mode.VIRTUAL, Event.Mode.HYBRID]:
                self.sync_to_calendar(event, user.email)
                
            self.send_ticket_confirmation(ticket_purchase)
            
        else:
            pass
            # TODO: Generate QR code from uid  
            # TODO: Generate Paystack reference and wait for payment. 
            # TODO: Payment Verification (Paid Only): Confirm is_paid via Paystack Webhook.
            
    def sync_to_calendar(self, event, new_user_email):
        try:
            virtual_meeting = getattr(event, 'virtual_meeting', None)
            if not virtual_meeting:
                return

            credentials = get_user_credentials(event.creator)
            service = GoogleCalendarService(credentials)

            all_emails = list(TicketPurchase.objects.filter(
                ticket__event=event, 
                is_paid=True
            ).values_list('email', flat=True))
            
            if event.creator.email not in all_emails:
                all_emails.append(event.creator.email)

            service.add_attendee_to_event(
                event_id=virtual_meeting.external_calendar_event_id,
                new_attendee_emails=all_emails
            )
            
        except Exception as e:
            logger.error(f"Calendar sync failed: {e}")
            
    def send_ticket_confirmation(self, ticket_purchase):
        event: Event = ticket_purchase.ticket.event
        user_name = ticket_purchase.user.get_full_name() if ticket_purchase.user else ticket_purchase.email 
        join_url = getattr(event, 'virtual_meeting', None).join_url if hasattr(event, 'virtual_meeting') else None
        
        context = {
            'user_name': user_name,
            'event_title': event.title,
            'event_date': event.date.strftime('%B %d, %Y at %H:%M %p'),
            'event_location': "Virtual Meeting" if event.mode == "VIRTUAL" else event.venue, # TODO: Add location to event
            'ticket_uid': str(ticket_purchase.ticket_uid),
            'join_url': join_url
        }
        
        html_body = render_to_string('emails/ticket_confirmation.html', context)
        
        mailer.send(
            subject=f"Confirmation: Your Ticket for {event.title}",
            body=html_body,
            recipient=ticket_purchase.email,
            is_html=True
        )
        