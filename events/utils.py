from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException

import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings

from .models import Event
from core.models import User
from futaverse.utils.google.views import build_google_auth_url

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

logger = logging.getLogger(__name__)

class GoogleAuthRequired(Exception):
    def __init__(self, auth_url):
        self.auth_url = auth_url
        
class GoogleAuthRequiredException(APIException):
    status_code = 401
    default_detail = "Authenticate with Google"
        
class GoogleCalendarService:
    def __init__(self, credentials):
        self.service = build("calendar", "v3", credentials=credentials)

    def create_event(self, event: Event, attendees_emails, manual_join_url=None):
        
        body = {
            'summary': event.title,
            'description': f"Join Meeting: {manual_join_url}\n\n{event.description}" if manual_join_url else event.description,
            'start': {
                'dateTime': event.start_time.isoformat(),
                'timeZone': settings.TIME_ZONE,
            },
            'end': {
                'dateTime': event.end_time.isoformat(),
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
                    'requestId': f"req-{event.id}", # Must be unique
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
        
def get_user_credentials(user: User, redirect_after_auth=None):
    creds_data = user.google_credentials
    google_auth_url = build_google_auth_url(user.id, redirect_after_auth)
    
    if not creds_data or not creds_data.get('token'):
        print("no creds")
        raise GoogleAuthRequired(google_auth_url)
    
    credentials = Credentials.from_authorized_user_info(creds_data)

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        
        user.google_credentials = {
            **creds_data,
            'token': credentials.token,
            'refresh_token': credentials.refresh_token
        }
        user.save(update_fields=['google_credentials'])
        
        return credentials
            
    raise GoogleAuthRequired(google_auth_url)