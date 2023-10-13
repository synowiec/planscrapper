from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]
SERVICE_ACCOUNT_FILE = 'service.json'


def delete_event(service, calendar_id, event_id):
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()


def add_event(service, calendar_id, event):
    service.events().insert(calendarId=calendar_id, body=event).execute()


def delete_all_upcoming_events(service, calendar_id, from_datetime):
    # Call the Calendar API
    now = from_datetime.astimezone().isoformat()
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=250, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return

    # Delete all events
    for event in events:
        delete_event(service, calendar_id, event['id'])


def add_events(service, calendar_id, events):
    for event in events:
        add_event(service, calendar_id, event)


class GoogleEventAPI:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        self.service = build('calendar', 'v3', credentials=credentials)

    def reload_calendar(self, calendar_id, events, from_datetime=datetime.now()):
        try:

            delete_all_upcoming_events(self.service, calendar_id, from_datetime)

            add_events(self.service, calendar_id, events)
        except HttpError as error:
            print('An error occurred: %s' % error)
