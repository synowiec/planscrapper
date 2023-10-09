import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]
SERVICE_ACCOUNT_FILE = 'service.json'


def delete_all_upcoming_events(service, calendar_id):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=250, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return

    # Delete all events
    for event in events:
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()


def add_events(service, calendar_id, events):
    for event in events:
        event = service.events().insert(calendarId=calendar_id, body=event).execute()


class GoogleEventAPI:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        self.service = build('calendar', 'v3', credentials=credentials)

    def reload_calendar(self, calendar_id, events):
        try:

            delete_all_upcoming_events(self.service, calendar_id)

            add_events(self.service, calendar_id, events)
        except HttpError as error:
            print('An error occurred: %s' % error)
