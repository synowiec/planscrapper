from calendar_controller import GoogleCalendarAPI
from scrapper import Scrapper
from events_controller import GoogleEventAPI
import json
from datetime import datetime

PLANS_TO_SCRAP_JSON = 'plans_to_scrap.json'
FROM_DATETIME = datetime.now()


def load_json(file):
    with open(file, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def main():
    plans_to_scrap = load_json(PLANS_TO_SCRAP_JSON)
    events = GoogleEventAPI()
    calendar = GoogleCalendarAPI()

    for spec in plans_to_scrap:
        spec_link = plans_to_scrap[spec]

        # Create Scrapper
        scrapper = Scrapper(spec_link, FROM_DATETIME)
        groups = set([group['name'] for group in scrapper.json['specs']])

        # Prepare Calendars
        # Check if each group exists; if not - create calendar with proper privileges
        existing_calendars = set([c['summary'] for c in calendar.items])
        calendars_to_create = groups - existing_calendars

        # Create missing calendars
        for c in calendars_to_create:
            new_calendar_id = calendar.create_calendar(c)
            # Set public privileges
            calendar.create_rule_for_public_access(new_calendar_id)

        # Delete upcoming events and add new events
        for s in scrapper.json['specs']:
            print('Processing ' + s['name'] + '...', end='')
            group_name = s['name']
            calendar_id = next(item['id'] for item in calendar.items if item['summary'] == group_name)
            events_to_load = s['events']
            events.reload_calendar(calendar_id, events_to_load)
            print('Done.')

    print('All plans scrapped and updated.')


def show_links():
    calendar = GoogleCalendarAPI()
    calendar.generate_links()


if __name__ == '__main__':
    main()
    show_links()
