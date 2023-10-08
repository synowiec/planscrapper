from pprint import pprint

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]
SERVICE_ACCOUNT_FILE = 'service.json'


def create_share_link(calendar_id, calendar_name):
    return calendar_name + '\t|\t' + 'https://calendar.google.com/calendar/embed?src=' + calendar_id


class GoogleCalendarAPI:
    def __init__(self):
        self.items = None
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        self.service = build('calendar', 'v3', credentials=credentials)
        self.recalculate_list_of_calendars()

    def recalculate_list_of_calendars(self):
        self.items = self.service.calendarList().list().execute()['items']

    def get_list_of_calendars(self):
        return self.items

    def create_calendar(self, calendar_name):
        calendar = {
            'summary': calendar_name
        }
        created_calendar = self.service.calendars().insert(body=calendar).execute()
        self.recalculate_list_of_calendars()
        return created_calendar['id']

    def delete_calendar(self, calendar_id):
        deleted_calendar = self.service.calendars().delete(calendarId=calendar_id).execute()
        self.recalculate_list_of_calendars()

    def get_calendar_details(self, calendar_id):
        calendar = self.service.calendars().get(calendarId=calendar_id).execute()

    def create_rule_for_public_access(self, calendar_id):
        rule = {
            'scope': {
                'type': 'default'
            },
            'role': 'reader'
        }
        created_rule = self.service.acl().insert(calendarId=calendar_id, body=rule).execute()

    def get_list_acl_rules(self, calendar_id):
        rule = self.service.acl().list(calendarId=calendar_id).execute()
        pprint(rule)

    def generate_links(self):
        for item in self.items:
            print(create_share_link(item['id'], item['summary']))
