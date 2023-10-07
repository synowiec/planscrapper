from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]
BEGINNING_OF_SEMESTER = '2023-10-01T19:21:48.992325Z'

def delete_all_upcoming_events(service, calendar_id):
    # Call the Calendar API
    # now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    now = BEGINNING_OF_SEMESTER
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=250, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return

    print(f'Found {len(events)} old events. Deleting...', end='')
    # Delete all events
    for event in events:
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()


def add_events(service, calendar_id, events):
    print('Adding...', end='')
    for event in events:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()


class GoogleCalendarAPI:
    def __init__(self):
        """Shows basic usage of the Google Calendar API.
            Prints the start and name of the next 10 events on the user's calendar.
            """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        self.service = build('calendar', 'v3', credentials=creds)

    def reload_calendar(self, calendar_id, events):
        try:

            delete_all_upcoming_events(self.service, calendar_id)

            add_events(self.service, calendar_id, events)

        except HttpError as error:
            print('An error occurred: %s' % error)