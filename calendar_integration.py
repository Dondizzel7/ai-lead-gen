"""
Calendar Integration Service for Automated Interview Scheduling System

This module handles integration with various calendar providers to manage availability
and schedule interviews. It supports Google Calendar, Microsoft Outlook, and other providers.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import requests
from dateutil import parser as date_parser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CalendarIntegrationService:
    """
    Base class for calendar integration services.
    """
    
    def __init__(self):
        """Initialize the calendar integration service."""
        logger.info("Calendar Integration Service initialized")
    
    def get_availability(self, 
                        user_id: str, 
                        start_time: datetime, 
                        end_time: datetime,
                        timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get user availability within a time range.
        
        Args:
            user_id: User identifier
            start_time: Start of time range
            end_time: End of time range
            timezone: Timezone for availability data
            
        Returns:
            List of available time slots
        """
        raise NotImplementedError("Subclasses must implement get_availability")
    
    def create_event(self, 
                    user_id: str, 
                    event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event.
        
        Args:
            user_id: User identifier
            event_details: Event details dictionary
            
        Returns:
            Created event data
        """
        raise NotImplementedError("Subclasses must implement create_event")
    
    def update_event(self, 
                    user_id: str, 
                    event_id: str, 
                    event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a calendar event.
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            event_details: Updated event details
            
        Returns:
            Updated event data
        """
        raise NotImplementedError("Subclasses must implement update_event")
    
    def delete_event(self, 
                    user_id: str, 
                    event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            
        Returns:
            True if deletion was successful
        """
        raise NotImplementedError("Subclasses must implement delete_event")
    
    def get_events(self, 
                  user_id: str, 
                  start_time: datetime, 
                  end_time: datetime,
                  timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get user events within a time range.
        
        Args:
            user_id: User identifier
            start_time: Start of time range
            end_time: End of time range
            timezone: Timezone for event data
            
        Returns:
            List of events
        """
        raise NotImplementedError("Subclasses must implement get_events")


class GoogleCalendarIntegration(CalendarIntegrationService):
    """
    Google Calendar integration service.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize the Google Calendar integration service.
        
        Args:
            credentials_path: Path to Google API credentials JSON file
            token_path: Path to token storage JSON file
        """
        super().__init__()
        
        self.credentials_path = credentials_path or os.path.join(os.getcwd(), 'credentials.json')
        self.token_path = token_path or os.path.join(os.getcwd(), 'token.json')
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        
        # Store services by user_id
        self.services = {}
        
        logger.info("Google Calendar Integration initialized")
    
    def _get_service(self, user_id: str):
        """
        Get or create a Google Calendar API service for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Google Calendar API service
        """
        # Check if service already exists for this user
        if user_id in self.services:
            return self.services[user_id]
        
        # Load credentials
        creds = None
        token_file = f"{os.path.splitext(self.token_path)[0]}_{user_id}.json"
        
        # Check if token file exists
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as token:
                    creds = Credentials.from_authorized_user_info(json.load(token), self.scopes)
            except Exception as e:
                logger.error(f"Error loading token: {str(e)}")
        
        # If credentials don't exist or are invalid, create new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing token: {str(e)}")
                    creds = None
            
            # If still no valid credentials, need to authenticate
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                    creds = flow.run_local_server(port=0)
                    
                    # Save the credentials for future use
                    with open(token_file, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    logger.error(f"Error authenticating: {str(e)}")
                    raise ValueError(f"Unable to authenticate with Google Calendar: {str(e)}")
        
        # Create and store the service
        service = build('calendar', 'v3', credentials=creds)
        self.services[user_id] = service
        
        return service
    
    def get_availability(self, 
                        user_id: str, 
                        start_time: datetime, 
                        end_time: datetime,
                        timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get user availability within a time range.
        
        Args:
            user_id: User identifier
            start_time: Start of time range
            end_time: End of time range
            timezone: Timezone for availability data
            
        Returns:
            List of available time slots
        """
        logger.info(f"Getting availability for user {user_id} from {start_time} to {end_time}")
        
        try:
            # Get the calendar service
            service = self._get_service(user_id)
            
            # Convert times to RFC3339 format
            start_rfc = start_time.astimezone(pytz.timezone(timezone)).isoformat()
            end_rfc = end_time.astimezone(pytz.timezone(timezone)).isoformat()
            
            # Get busy periods
            body = {
                "timeMin": start_rfc,
                "timeMax": end_rfc,
                "timeZone": timezone,
                "items": [{"id": "primary"}]
            }
            
            freebusy = service.freebusy().query(body=body).execute()
            busy_periods = freebusy['calendars']['primary']['busy']
            
            # Convert busy periods to datetime objects
            busy_ranges = []
            for period in busy_periods:
                busy_start = date_parser.parse(period['start'])
                busy_end = date_parser.parse(period['end'])
                busy_ranges.append((busy_start, busy_end))
            
            # Find available slots (simplified approach)
            available_slots = []
            current_time = start_time
            
            # Define slot duration (e.g., 30 minutes)
            slot_duration = timedelta(minutes=30)
            
            while current_time + slot_duration <= end_time:
                slot_end = current_time + slot_duration
                
                # Check if slot overlaps with any busy period
                is_available = True
                for busy_start, busy_end in busy_ranges:
                    if (current_time < busy_end and slot_end > busy_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        "start_time": current_time.isoformat(),
                        "end_time": slot_end.isoformat(),
                        "duration_minutes": int(slot_duration.total_seconds() / 60)
                    })
                
                # Move to next slot
                current_time += slot_duration
            
            logger.info(f"Found {len(available_slots)} available slots for user {user_id}")
            return available_slots
        
        except Exception as e:
            logger.error(f"Error getting availability: {str(e)}")
            return []
    
    def create_event(self, 
                    user_id: str, 
                    event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event.
        
        Args:
            user_id: User identifier
            event_details: Event details dictionary
            
        Returns:
            Created event data
        """
        logger.info(f"Creating event for user {user_id}")
        
        try:
            # Get the calendar service
            service = self._get_service(user_id)
            
            # Extract event details
            title = event_details.get('title', 'Interview')
            location = event_details.get('location', '')
            description = event_details.get('description', '')
            start_time = event_details.get('start_time')
            end_time = event_details.get('end_time')
            timezone = event_details.get('timezone', 'UTC')
            attendees = event_details.get('attendees', [])
            
            # Validate required fields
            if not start_time or not end_time:
                raise ValueError("Start time and end time are required")
            
            # Parse times if they are strings
            if isinstance(start_time, str):
                start_time = date_parser.parse(start_time)
            if isinstance(end_time, str):
                end_time = date_parser.parse(end_time)
            
            # Convert times to RFC3339 format
            start_rfc = start_time.astimezone(pytz.timezone(timezone)).isoformat()
            end_rfc = end_time.astimezone(pytz.timezone(timezone)).isoformat()
            
            # Create event body
            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_rfc,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_rfc,
                    'timeZone': timezone,
                },
                'attendees': [{'email': email} for email in attendees],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            # Add conference details if provided
            if 'conference_data' in event_details:
                event['conferenceData'] = event_details['conference_data']
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1 if 'conference_data' in event_details else 0,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Event created: {created_event['id']}")
            
            # Format response
            return {
                'id': created_event['id'],
                'title': created_event['summary'],
                'location': created_event.get('location', ''),
                'description': created_event.get('description', ''),
                'start_time': created_event['start']['dateTime'],
                'end_time': created_event['end']['dateTime'],
                'timezone': created_event['start']['timeZone'],
                'attendees': [attendee['email'] for attendee in created_event.get('attendees', [])],
                'html_link': created_event['htmlLink'],
                'conference_link': created_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')
            }
        
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            raise
    
    def update_event(self, 
                    user_id: str, 
                    event_id: str, 
                    event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a calendar event.
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            event_details: Updated event details
            
        Returns:
            Updated event data
        """
        logger.info(f"Updating event {event_id} for user {user_id}")
        
        try:
            # Get the calendar service
            service = self._get_service(user_id)
            
            # Get the existing event
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Update fields
            if 'title' in event_details:
                event['summary'] = event_details['title']
            
            if 'location' in event_details:
                event['location'] = event_details['location']
            
            if 'description' in event_details:
                event['description'] = event_details['description']
            
            if 'start_time' in event_details or 'end_time' in event_details:
                timezone = event_details.get('timezone', event['start']['timeZone'])
                
                if 'start_time' in event_details:
                    start_time = event_details['start_time']
                    if isinstance(start_time, str):
                        start_time = date_parser.parse(start_time)
                    start_rfc = start_time.astimezone(pytz.timezone(timezone)).isoformat()
                    event['start'] = {'dateTime': start_rfc, 'timeZone': timezone}
                
                if 'end_time' in event_details:
                    end_time = event_details['end_time']
                    if isinstance(end_time, str):
                        end_time = date_parser.parse(end_time)
                    end_rfc = end_time.astimezone(pytz.timezone(timezone)).isoformat()
                    event['end'] = {'dateTime': end_rfc, 'timeZone': timezone}
            
            if 'attendees' in event_details:
                event['attendees'] = [{'email': email} for email in event_details['attendees']]
            
            # Update the event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Event updated: {updated_event['id']}")
            
            # Format response
            return {
                'id': updated_event['id'],
                'title': updated_event['summary'],
                'location': updated_event.get('location', ''),
                'description': updated_event.get('description', ''),
                'start_time': updated_event['start']['dateTime'],
                'end_time': updated_event['end']['dateTime'],
                'timezone': updated_event['start']['timeZone'],
                'attendees': [attendee['email'] for attendee in updated_event.get('attendees', [])],
                'html_link': updated_event['htmlLink'],
                'conference_link': updated_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')
            }
        
        except Exception as e:
            logger.error(f"Error updating event: {str(e)}")
            raise
    
    def delete_event(self, 
                    user_id: str, 
                    event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            
        Returns:
            True if deletion was successful
        """
        logger.info(f"Deleting event {event_id} for user {user_id}")
        
        try:
            # Get the calendar service
            service = self._get_service(user_id)
            
            # Delete the event
            service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Event deleted: {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting event: {str(e)}")
            return False
    
    def get_events(self, 
                  user_id: str, 
                  start_time: datetime, 
                  end_time: datetime,
                  timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get user events within a time range.
        
        Args:
            user_id: User identifier
            start_time: Start of time range
            end_time: End of time range
            timezone: Timezone for event data
            
        Returns:
            List of events
        """
        logger.info(f"Getting events for user {user_id} from {start_time} to {end_time}")
        
        try:
            # Get the calendar service
            service = self._get_service(user_id)
            
            # Convert times to RFC3339 format
            start_rfc = start_time.astimezone(pytz.timezone(timezone)).isoformat()
            end_rfc = end_time.astimezone(pytz.timezone(timezone)).isoformat()
            
            # Get events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_rfc,
                timeMax=end_rfc,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format response
            formatted_events = []
            for event in events:
                # Skip events without start/end times
                if 'dateTime' not in event.get('start', {}) or 'dateTime' not in event.get('end', {}):
                    continue
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'Untitled Event'),
                    'location': event.get('location', ''),
                    'description': event.get('description', ''),
                    'start_time': event['start']['dateTime'],
                    'end_time': event['end']['dateTime'],
                    'timezone': event['start']['timeZone'],
                    'attendees': [attendee['email'] for attendee in event.get('attendees', [])],
                    'html_link': event['htmlLink'],
                    'conference_link': event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')
                })
            
            logger.info(f"Found {len(formatted_events)} events for user {user_id}")
            return formatted_events
        
        except Exception as e:
            logger.error(f"Error getting events: {str(e)}")
            return []


class MicrosoftCalendarIntegration(CalendarIntegrationService):
    """
    Microsoft Calendar integration service.
    """
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, tenant_id: Optional[str] = None):
        """
        Initialize the Microsoft Calendar integration service.
        
        Args:
            client_id: Microsoft application client ID
            client_secret: Microsoft application client secret
            tenant_id: Microsoft tenant ID
        """
        super().__init__()
        
        self.client_id = client_id or os.environ.get('MS_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('MS_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.environ.get('MS_TENANT_ID')
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        
        # Store tokens by user_id
        self.tokens = {}
        
        logger.info("Microsoft Calendar Integration initialized")
    
    def _get_token(self, user_id: str) -> str:
        """
        Get an access token for Microsoft Graph API.
        
        Args:
            user_id: User identifier
            
        Returns:
            Access token
        """
        # Check if token exists and is not expired
        if user_id in self.tokens:
            token_data = self.tokens[user_id]
            expiry = token_data.get('expiry', 0)
            
            # If token is still valid, return it
            if expiry > datetime.now().timestamp():
                return token_data['access_token']
        
        # Get new token
        token_url = f"{self.authority}/oauth2/v2.0/token"
        
        data = {
            'client_id': self.client_id,
            'scope': ' '.join(self.scope),
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store token with expiry
            self.tokens[user_id] = {
                'access_token': token_data['access_token'],
                'expiry': datetime.now().timestamp() + token_data['expires_in'] - 300  # 5 minutes buffer
            }
            
            return token_data['access_token']
        
        except Exception as e:
            logger.error(f"Error getting Microsoft token: {str(e)}")
            raise
    
    def get_availability(self, 
                        user_id: str, 
                        start_time: datetime, 
                        end_time: datetime,
                        timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get user availability within a time range.
        
        Args:
            user_id: User identifier (email address for Microsoft)
            start_time: Start of time range
            end_time: End of time range
            timezone: Timezone for availability data
            
        Returns:
            List of available time slots
        """
        logger.info(f"Getting availability for user {user_id} from {start_time} to {end_time}")
        
        try:
            # Get access token
            token = self._get_token(user_id)
            
            # Convert times to ISO format
            start_iso = start_time.astimezone(pytz.timezone(timezone)).isoformat()
            end_iso = end_time.astimezone(pytz.timezone(timezone)).isoformat()
            
            # Get free/busy information
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendar/getSchedule"
            
            headers = {
                'Authorization': f"Bearer {token}",
                'Content-Type': 'application/json'
            }
            
            data = {
                "schedules": [user_id],
                "startTime": {
                    "dateTime": start_iso,
                    "timeZone": timezone
                },
                "endTime": {
                    "dateTime": end_iso,
                    "timeZone": timezone
                },
                "availabilityViewInterval": 30  # 30-minute intervals
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            schedule_data = response.json()
            schedule_items = schedule_data.get('value', [])
            
            if not schedule_items:
                logger.warning(f"No schedule data returned for user {user_id}")
                return []
            
            # Parse availability view
            availability_view = schedule_items[0].get('availabilityView', '')
            working_hours = schedule_items[0].get('workingHours', {})
            
            # Define slot duration (30 minutes as per availabilityViewInterval)
            slot_duration = timedelta(minutes=30)
            
            # Find available slots
            available_slots = []
            current_time = start_time
            
            for status in availability_view:
                # 0 = free, 1 = tentative, 2 = busy, 3 = out of office, 4 = working elsewhere
                if status == '0':  # Free
                    slot_end = current_time + slot_duration
                    
                    # Check if within working hours
                    is_working_hours = self._is_within_working_hours(current_time, working_hours, timezone)
                    
                    if is_working_hours:
                        available_slots.append({
                            "start_time": current_time.isoformat(),
                            "end_time": slot_end.isoformat(),
                            "duration_minutes": int(slot_duration.total_seconds() / 60)
                        })
                
                # Move to next slot
                current_time += slot_duration
                
                # Stop if we've reached the end time
                if current_time >= end_time:
                    break
            
            logger.info(f"Found {len(available_slots)} available slots for user {user_id}")
            return available_slots
        
        except Exception as e:
            logger.error(f"Error getting Microsoft availability: {str(e)}")
            return []
    
    def _is_within_working_hours(self, time: datetime, working_hours: Dict[str, Any], timezone: str) -> bool:
        """
        Check if a time is within working hours.
        
        Args:
            time: Time to check
            working_hours: Working hours data from Microsoft Graph
            timezone: Timezone for working hours
            
        Returns:
            True if time is within working hours
        """
        # Default to standard working hours if not provided
        if not working_hours:
            # Assume Monday-Friday, 9 AM - 5 PM
            days = {0: False, 1: True, 2: True, 3: True, 4: True, 5: True, 6: False}  # 0 = Sunday
            start_time = datetime.strptime("09:00:00", "%H:%M:%S").time()
            end_time = datetime.strptime("17:00:00", "%H:%M:%S").time()
        else:
            # Parse working hours from Microsoft Graph
            days = {
                0: 'sunday' in working_hours.get('daysOfWeek', []),
                1: 'monday' in working_hours.get('daysOfWeek', []),
                2: 'tuesday' in working_hours.get('daysOfWeek', []),
                3: 'wednesday' in working_hours.get('daysOfWeek', []),
                4: 'thursday' in working_hours.get('daysOfWeek', []),
                5: 'friday' in working_hours.get('daysOfWeek', []),
                6: 'saturday' in working_hours.get('daysOfWeek', [])
            }
            
            start_time_str = working_hours.get('startTime', "09:00:00")
            end_time_str = working_hours.get('endTime', "17:00:00")
            
            start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
            end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
        
        # Convert time to timezone
        local_time = time.astimezone(pytz.timezone(timezone))
        
        # Check day of week
        day_of_week = local_time.weekday()  # 0 = Monday in datetime
        if day_of_week == 6:  # Convert to 0 = Sunday
            day_of_week = 0
        else:
            day_of_week += 1
        
        is_working_day = days.get(day_of_week, False)
        
        # Check time of day
        time_of_day = local_time.time()
        is_working_time = start_time <= time_of_day <= end_time
        
        return is_working_day and is_working_time
    
    def create_event(self, 
                    user_id: str, 
                    event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event.
        
        Args:
            user_id: User identifier (email address for Microsoft)
            event_details: Event details dictionary
            
        Returns:
            Created event data
        """
        logger.info(f"Creating event for user {user_id}")
        
        try:
            # Get access token
            token = self._get_token(user_id)
            
            # Extract event details
            title = event_details.get('title', 'Interview')
            location = event_details.get('location', '')
            description = event_details.get('description', '')
            start_time = event_details.get('start_time')
            end_time = event_details.get('end_time')
            timezone = event_details.get('timezone', 'UTC')
            attendees = event_details.get('attendees', [])
            
            # Validate required fields
            if not start_time or not end_time:
                raise ValueError("Start time and end time are required")
            
            # Parse times if they are strings
            if isinstance(start_time, str):
                start_time = date_parser.parse(start_time)
            if isinstance(end_time, str):
                end_time = date_parser.parse(end_time)
            
            # Convert times to ISO format
            start_iso = start_time.astimezone(pytz.timezone(timezone)).isoformat()
            end_iso = end_time.astimezone(pytz.timezone(timezone)).isoformat()
            
            # Create event
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendar/events"
            
            headers = {
                'Authorization': f"Bearer {token}",
                'Content-Type': 'application/json'
            }
            
            data = {
                "subject": title,
                "body": {
                    "contentType": "HTML",
                    "content": description
                },
                "start": {
                    "dateTime": start_iso,
                    "timeZone": timezone
                },
                "end": {
                    "dateTime": end_iso,
                    "timeZone": timezone
                },
                "location": {
                    "displayName": location
                },
                "attendees": [
                    {
                        "emailAddress": {
                            "address": email,
                            "name": email.split('@')[0]  # Simple name extraction
                        },
                        "type": "required"
                    } for email in attendees
                ],
                "isOnlineMeeting": True,
                "onlineMeetingProvider": "teamsForBusiness"
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            created_event = response.json()
            
            # Format response
            return {
                'id': created_event['id'],
                'title': created_event['subject'],
                'location': created_event.get('location', {}).get('displayName', ''),
                'description': created_event.get('body', {}).get('content', ''),
                'start_time': created_event['start']['dateTime'],
                'end_time': created_event['end']['dateTime'],
                'timezone': created_event['start']['timeZone'],
                'attendees': [attendee['emailAddress']['address'] for attendee in created_event.get('attendees', [])],
                'web_link': created_event.get('webLink', ''),
                'conference_link': created_event.get('onlineMeeting', {}).get('joinUrl', '')
            }
        
        except Exception as e:
            logger.error(f"Error creating Microsoft event: {str(e)}")
            raise
    
    def update_event(self, 
                    user_id: str, 
                    event_id: str, 
                    event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a calendar event.
        
        Args:
            user_id: User identifier (email address for Microsoft)
            event_id: Event identifier
            event_details: Updated event details
            
        Returns:
            Updated event data
        """
        logger.info(f"Updating event {event_id} for user {user_id}")
        
        try:
            # Get access token
            token = self._get_token(user_id)
            
            # Create update data
            update_data = {}
            
            if 'title' in event_details:
                update_data['subject'] = event_details['title']
            
            if 'description' in event_details:
                update_data['body'] = {
                    "contentType": "HTML",
                    "content": event_details['description']
                }
            
            if 'location' in event_details:
                update_data['location'] = {
                    "displayName": event_details['location']
                }
            
            if 'start_time' in event_details or 'end_time' in event_details or 'timezone' in event_details:
                timezone = event_details.get('timezone', 'UTC')
                
                if 'start_time' in event_details:
                    start_time = event_details['start_time']
                    if isinstance(start_time, str):
                        start_time = date_parser.parse(start_time)
                    start_iso = start_time.astimezone(pytz.timezone(timezone)).isoformat()
                    
                    update_data['start'] = {
                        "dateTime": start_iso,
                        "timeZone": timezone
                    }
                
                if 'end_time' in event_details:
                    end_time = event_details['end_time']
                    if isinstance(end_time, str):
                        end_time = date_parser.parse(end_time)
                    end_iso = end_time.astimezone(pytz.timezone(timezone)).isoformat()
                    
                    update_data['end'] = {
                        "dateTime": end_iso,
                        "timeZone": timezone
                    }
            
            if 'attendees' in event_details:
                update_data['attendees'] = [
                    {
                        "emailAddress": {
                            "address": email,
                            "name": email.split('@')[0]  # Simple name extraction
                        },
                        "type": "required"
                    } for email in event_details['attendees']
                ]
            
            # Update event
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendar/events/{event_id}"
            
            headers = {
                'Authorization': f"Bearer {token}",
                'Content-Type': 'application/json'
            }
            
            response = requests.patch(url, headers=headers, json=update_data)
            response.raise_for_status()
            
            # Get updated event
            get_response = requests.get(url, headers=headers)
            get_response.raise_for_status()
            
            updated_event = get_response.json()
            
            # Format response
            return {
                'id': updated_event['id'],
                'title': updated_event['subject'],
                'location': updated_event.get('location', {}).get('displayName', ''),
                'description': updated_event.get('body', {}).get('content', ''),
                'start_time': updated_event['start']['dateTime'],
                'end_time': updated_event['end']['dateTime'],
                'timezone': updated_event['start']['timeZone'],
                'attendees': [attendee['emailAddress']['address'] for attendee in updated_event.get('attendees', [])],
                'web_link': updated_event.get('webLink', ''),
                'conference_link': updated_event.get('onlineMeeting', {}).get('joinUrl', '')
            }
        
        except Exception as e:
            logger.error(f"Error updating Microsoft event: {str(e)}")
            raise
    
    def delete_event(self, 
                    user_id: str, 
                    event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            user_id: User identifier (email address for Microsoft)
            event_id: Event identifier
            
        Returns:
            True if deletion was successful
        """
        logger.info(f"Deleting event {event_id} for user {user_id}")
        
        try:
            # Get access token
            token = self._get_token(user_id)
            
            # Delete event
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendar/events/{event_id}"
            
            headers = {
                'Authorization': f"Bearer {token}"
            }
            
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Event deleted: {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting Microsoft event: {str(e)}")
            return False
    
    def get_events(self, 
                  user_id: str, 
                  start_time: datetime, 
                  end_time: datetime,
                  timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get user events within a time range.
        
        Args:
            user_id: User identifier (email address for Microsoft)
            start_time: Start of time range
            end_time: End of time range
            timezone: Timezone for event data
            
        Returns:
            List of events
        """
        logger.info(f"Getting events for user {user_id} from {start_time} to {end_time}")
        
        try:
            # Get access token
            token = self._get_token(user_id)
            
            # Convert times to ISO format
            start_iso = start_time.astimezone(pytz.timezone(timezone)).isoformat()
            end_iso = end_time.astimezone(pytz.timezone(timezone)).isoformat()
            
            # Get events
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/calendar/calendarView"
            
            headers = {
                'Authorization': f"Bearer {token}",
                'Prefer': f'outlook.timezone="{timezone}"'
            }
            
            params = {
                'startDateTime': start_iso,
                'endDateTime': end_iso,
                '$select': 'id,subject,bodyPreview,start,end,location,attendees,webLink,onlineMeeting'
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            events_data = response.json()
            events = events_data.get('value', [])
            
            # Format response
            formatted_events = []
            for event in events:
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('subject', 'Untitled Event'),
                    'location': event.get('location', {}).get('displayName', ''),
                    'description': event.get('bodyPreview', ''),
                    'start_time': event['start']['dateTime'],
                    'end_time': event['end']['dateTime'],
                    'timezone': event['start']['timeZone'],
                    'attendees': [attendee['emailAddress']['address'] for attendee in event.get('attendees', [])],
                    'web_link': event.get('webLink', ''),
                    'conference_link': event.get('onlineMeeting', {}).get('joinUrl', '')
                })
            
            logger.info(f"Found {len(formatted_events)} events for user {user_id}")
            return formatted_events
        
        except Exception as e:
            logger.error(f"Error getting Microsoft events: {str(e)}")
            return []


class CalendarService:
    """
    Calendar service that provides a unified interface to different calendar providers.
    """
    
    def __init__(self):
        """Initialize the calendar service."""
        self.integrations = {}
        self.user_providers = {}
        
        logger.info("Calendar Service initialized")
    
    def register_integration(self, provider: str, integration: CalendarIntegrationService) -> None:
        """
        Register a calendar integration.
        
        Args:
            provider: Provider name (e.g., 'google', 'microsoft')
            integration: Calendar integration service
        """
        self.integrations[provider.lower()] = integration
        logger.info(f"Registered calendar integration: {provider}")
    
    def set_user_provider(self, user_id: str, provider: str) -> None:
        """
        Set the calendar provider for a user.
        
        Args:
            user_id: User identifier
            provider: Provider name (e.g., 'google', 'microsoft')
        """
        self.user_providers[user_id] = provider.lower()
        logger.info(f"Set calendar provider for user {user_id}: {provider}")
    
    def _get_integration(self, user_id: str) -> CalendarIntegrationService:
        """
        Get the calendar integration for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Calendar integration service
        """
        provider = self.user_providers.get(user_id)
        
        if not provider:
            raise ValueError(f"No calendar provider set for user {user_id}")
        
        integration = self.integrations.get(provider)
        
        if not integration:
            raise ValueError(f"Calendar provider {provider} not registered")
        
        return integration
    
    def get_availability(self, 
                        user_id: str, 
                        start_time: datetime, 
                        end_time: datetime,
                        timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get user availability within a time range.
        
        Args:
            user_id: User identifier
            start_time: Start of time range
            end_time: End of time range
            timezone: Timezone for availability data
            
        Returns:
            List of available time slots
        """
        integration = self._get_integration(user_id)
        return integration.get_availability(user_id, start_time, end_time, timezone)
    
    def create_event(self, 
                    user_id: str, 
                    event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a calendar event.
        
        Args:
            user_id: User identifier
            event_details: Event details dictionary
            
        Returns:
            Created event data
        """
        integration = self._get_integration(user_id)
        return integration.create_event(user_id, event_details)
    
    def update_event(self, 
                    user_id: str, 
                    event_id: str, 
                    event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a calendar event.
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            event_details: Updated event details
            
        Returns:
            Updated event data
        """
        integration = self._get_integration(user_id)
        return integration.update_event(user_id, event_id, event_details)
    
    def delete_event(self, 
                    user_id: str, 
                    event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            
        Returns:
            True if deletion was successful
        """
        integration = self._get_integration(user_id)
        return integration.delete_event(user_id, event_id)
    
    def get_events(self, 
                  user_id: str, 
                  start_time: datetime, 
                  end_time: datetime,
                  timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get user events within a time range.
        
        Args:
            user_id: User identifier
            start_time: Start of time range
            end_time: End of time range
            timezone: Timezone for event data
            
        Returns:
            List of events
        """
        integration = self._get_integration(user_id)
        return integration.get_events(user_id, start_time, end_time, timezone)
    
    def get_common_availability(self,
                              user_ids: List[str],
                              start_time: datetime,
                              end_time: datetime,
                              duration_minutes: int = 60,
                              timezone: str = "UTC") -> List[Dict[str, Any]]:
        """
        Get common availability for multiple users.
        
        Args:
            user_ids: List of user identifiers
            start_time: Start of time range
            end_time: End of time range
            duration_minutes: Minimum duration of available slots
            timezone: Timezone for availability data
            
        Returns:
            List of common available time slots
        """
        logger.info(f"Getting common availability for {len(user_ids)} users from {start_time} to {end_time}")
        
        # Get availability for each user
        all_availability = {}
        for user_id in user_ids:
            try:
                availability = self.get_availability(user_id, start_time, end_time, timezone)
                all_availability[user_id] = availability
            except Exception as e:
                logger.error(f"Error getting availability for user {user_id}: {str(e)}")
                return []  # If any user's availability can't be retrieved, return empty list
        
        # Find common available slots
        common_slots = self._find_common_slots(all_availability, duration_minutes, timezone)
        
        logger.info(f"Found {len(common_slots)} common available slots")
        return common_slots
    
    def _find_common_slots(self,
                          all_availability: Dict[str, List[Dict[str, Any]]],
                          duration_minutes: int,
                          timezone: str) -> List[Dict[str, Any]]:
        """
        Find common available time slots among multiple users.
        
        Args:
            all_availability: Dictionary mapping user IDs to their availability
            duration_minutes: Minimum duration of available slots
            timezone: Timezone for availability data
            
        Returns:
            List of common available time slots
        """
        if not all_availability:
            return []
        
        # Convert all slots to datetime ranges
        user_ranges = {}
        for user_id, slots in all_availability.items():
            ranges = []
            for slot in slots:
                start = date_parser.parse(slot['start_time'])
                end = date_parser.parse(slot['end_time'])
                ranges.append((start, end))
            user_ranges[user_id] = ranges
        
        # Find overlapping ranges
        common_ranges = []
        
        # Start with the first user's ranges
        first_user = list(user_ranges.keys())[0]
        potential_common = user_ranges[first_user]
        
        # Intersect with each subsequent user's ranges
        for user_id in list(user_ranges.keys())[1:]:
            new_common = []
            user_slots = user_ranges[user_id]
            
            for common_start, common_end in potential_common:
                for slot_start, slot_end in user_slots:
                    # Find intersection
                    intersection_start = max(common_start, slot_start)
                    intersection_end = min(common_end, slot_end)
                    
                    # Check if intersection is valid and meets duration requirement
                    if intersection_start < intersection_end:
                        duration = (intersection_end - intersection_start).total_seconds() / 60
                        if duration >= duration_minutes:
                            new_common.append((intersection_start, intersection_end))
            
            potential_common = new_common
            
            # If no common slots found, exit early
            if not potential_common:
                return []
        
        # Convert back to dictionary format
        common_slots = []
        for start, end in potential_common:
            duration = (end - start).total_seconds() / 60
            
            # Only include slots that meet the minimum duration
            if duration >= duration_minutes:
                common_slots.append({
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                    "duration_minutes": int(duration)
                })
        
        return common_slots


# Example usage
if __name__ == "__main__":
    # Initialize calendar service
    calendar_service = CalendarService()
    
    # Register integrations
    google_integration = GoogleCalendarIntegration(
        credentials_path="path/to/credentials.json",
        token_path="path/to/token.json"
    )
    
    microsoft_integration = MicrosoftCalendarIntegration(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tenant_id="your_tenant_id"
    )
    
    calendar_service.register_integration("google", google_integration)
    calendar_service.register_integration("microsoft", microsoft_integration)
    
    # Set user providers
    calendar_service.set_user_provider("user1@example.com", "google")
    calendar_service.set_user_provider("user2@example.com", "microsoft")
    
    # Example: Get availability
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(days=3)
    
    availability = calendar_service.get_availability(
        user_id="user1@example.com",
        start_time=start_time,
        end_time=end_time,
        timezone="America/New_York"
    )
    
    print(f"Found {len(availability)} available slots")
    
    # Example: Create event
    if availability:
        event_details = {
            "title": "Interview with Candidate",
            "location": "Conference Room A",
            "description": "Technical interview for Software Engineer position",
            "start_time": date_parser.parse(availability[0]["start_time"]),
            "end_time": date_parser.parse(availability[0]["end_time"]),
            "timezone": "America/New_York",
            "attendees": ["candidate@example.com", "interviewer@example.com"]
        }
        
        event = calendar_service.create_event(
            user_id="user1@example.com",
            event_details=event_details
        )
        
        print(f"Created event: {event['id']}")
        print(f"Title: {event['title']}")
        print(f"Start time: {event['start_time']}")
        print(f"End time: {event['end_time']}")
        print(f"Attendees: {', '.join(event['attendees'])}")
        
        # Example: Update event
        updated_details = {
            "title": "Updated: Interview with Candidate",
            "description": "Technical interview for Senior Software Engineer position"
        }
        
        updated_event = calendar_service.update_event(
            user_id="user1@example.com",
            event_id=event['id'],
            event_details=updated_details
        )
        
        print(f"Updated event: {updated_event['id']}")
        print(f"New title: {updated_event['title']}")
        
        # Example: Delete event
        deleted = calendar_service.delete_event(
            user_id="user1@example.com",
            event_id=event['id']
        )
        
        print(f"Event deleted: {deleted}")
    
    # Example: Get common availability
    common_availability = calendar_service.get_common_availability(
        user_ids=["user1@example.com", "user2@example.com"],
        start_time=start_time,
        end_time=end_time,
        duration_minutes=60,
        timezone="America/New_York"
    )
    
    print(f"Found {len(common_availability)} common available slots")
