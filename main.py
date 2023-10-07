from scrapper import Scrapper
from calendarAPI import GoogleCalendarAPI

CALENDARS = {
    's1Z1': 'c_fcaca62096e0c7635bc913740fc1628bd9226c1bad7e162a96668d489b29fa34@group.calendar.google.com',
    's1Z2u': 'c_e318bbbf3b9f05e912ed76d8580020acffeec01918fc15faa08f67dab07bebc9@group.calendar.google.com',
    's1Z3u': 'c_60aaa06f57fda41120b2aaffe89955be2594aec2bae430bf9fdd3e39e479637d@group.calendar.google.com',
    's1Z4u': 'c_60984bf3731ed32e6cff4ed47de821fc6956514a770f07915883187c68aca9d8@group.calendar.google.com'
}


def main():
    calendar = GoogleCalendarAPI()
    specs = Scrapper()
    for spec in specs.json['specs']:
        spec_name = spec['name']
        print(f'Processing {spec_name}... ', end='')
        calendar.reload_calendar(CALENDARS[spec_name], spec['events'])
        print('Done.')


if __name__ == '__main__':
    main()
