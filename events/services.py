from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from .models import TicketPurchase, Event
from core.models import User

from logging import getLogger
from datetime import timedelta, datetime

from futaverse.utils.email_service import BrevoEmailService
from futaverse.utils.google.views import build_google_auth_url

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

logger = getLogger(__name__)
mailer = BrevoEmailService()

class EventRegistrationService:
    @staticmethod
    def sync_to_calendar(event):
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

    @staticmethod
    def send_ticket_email(ticket_purchase):
        event: Event = ticket_purchase.ticket.event
        user_name = ticket_purchase.user.get_full_name() if ticket_purchase.user else ticket_purchase.email 
        join_url = getattr(event, 'virtual_meeting', None).join_url if hasattr(event, 'virtual_meeting') else None
        start_datetime = timezone.make_aware(datetime.combine(event.date, event.start_time))
        
        context = {
            'user_name': user_name,
            'event_title': event.title,
            'event_date': start_datetime.strftime('%B %d, %Y at %H:%M %p'),
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
        
class GoogleAuthRequired(Exception):
    def __init__(self, auth_url):
        self.auth_url = auth_url
        
class GoogleCalendarService:
    def __init__(self, credentials):
        self.service = build("calendar", "v3", credentials=credentials)

    def create_event(self, event: Event, attendees_emails, manual_join_url=None):
        
        start_datetime = timezone.make_aware(datetime.combine(event.date, event.start_time))
        end_datetime = start_datetime + timedelta(minutes=event.duration_mins)
        
        body = {
            'summary': event.title,
            'description': f"Join Meeting: {manual_join_url}\n\n{event.description}" if manual_join_url else event.description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'attendees': [{'email': email} for email in attendees_emails],
            
            # Tag the event with our database ID for easy searching later
            'extendedProperties': {
                'private': {
                    'app_event_id': str(event.id),
                }
            },
            "conferenceData": {
                'createRequest': {
                    'requestId': f"req-{event.id}", 
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }

        try:
            return self.service.events().insert(
                calendarId='primary',
                body=body,
                conferenceDataVersion=1 if not manual_join_url else 0,
                sendUpdates='all'        
            ).execute()
            
        except HttpError as e:
            logger.error(f"Google Calendar Create Error: {e}")
            raise 
        
    def add_attendee_to_event(self, event_id, new_attendee_emails):
        """
        event_id: The external_calendar_event_id
        new_attendee_emails: List of current + new attendee emails
        """
        try:
            body = {
                'attendees': [{'email': email} for email in new_attendee_emails]
            }

            return self.service.events().patch(
                calendarId='primary',
                eventId=event_id,
                body=body,
                sendUpdates='all'  
            ).execute()
            
        except HttpError as e:
            logger.error(f"Error patching calendar attendees: {e}")
            return None
        
def get_user_credentials(user: User, redirect_after_auth=None):
    creds_data = user.google_credentials
    google_auth_url = build_google_auth_url(user.sqid, redirect_after_auth)
    
    if not creds_data or not creds_data.get('token'):
        print("no creds")
        raise GoogleAuthRequired(google_auth_url)
    
    credentials = Credentials.from_authorized_user_info(creds_data)
    
    if not credentials.expired:
        return credentials

    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            
            user.google_credentials = {
                **creds_data,
                'token': credentials.token,
                'refresh_token': credentials.refresh_token
            }
            user.save(update_fields=['google_credentials'])
            
            return credentials
        
        except Exception as e:
            logger.error(f"Refresh token failed for {user.email}: {e}")
            raise GoogleAuthRequired(google_auth_url)
            
    raise GoogleAuthRequired(google_auth_url)