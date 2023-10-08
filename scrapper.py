import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

DAY_REGEX = r'\b(?:Poniedziałek|Wtorek|Środa|Czwartek|Piątek|Sobota|Niedziela) \d{4}-\d{2}-\d{2}\b'
HOUR_REGEX = r'\d{2}:\d{2}-\d{2}:\d{2}'
TIMEZONE = 'Europe/Warsaw'
TOPICS = dict()


def get_page_content(page):
    response = requests.get(page)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def get_trs(source):
    return source.find_all('tr')


def tds_to_list(cells):
    list_of_elements = list()
    for cell in cells:
        list_of_elements.append(cell.text)
    return list_of_elements


def get_tds(row):
    cells = row.find_all('td')
    return tds_to_list(cells)


def get_specs_names(rows):
    first_row = rows[0]  # get first row with specs
    cells = first_row.find_all('td')
    return tds_to_list(cells[1:])  # skip first empty cell


def is_matching_regex(cell, regex):
    pattern = re.compile(regex)
    return True if pattern.match(cell) else False


def clean_days(days):
    cleared_days = list()
    for day in days:
        converted = get_tds(day)
        if is_matching_regex(converted[0], DAY_REGEX):
            cleared_days.append(converted)
    return cleared_days


def generate_base_json(specs):
    json = {
        'specs': []
    }

    for spec in specs:
        json['specs'].append({
            "name": spec,
            "events": []
        })
    return json


def day_to_json(day, matching_indexes, json):
    plan_for = day[0].split()[1].split('-')
    yyyy = int(plan_for[0])
    mm = int(plan_for[1])
    dd = int(plan_for[2])

    s = day[2:matching_indexes[0]]
    hours = list()
    for index in matching_indexes:
        cells_in_day = len(s) * 3 + 1  # +1 for hour header
        hours.append(day[index:index + cells_in_day])

    for i, spec in enumerate(s):
        for hour in hours:
            if len(hour) == 0:
                continue
            time = hour[0].split('-')

            start = time[0].split(':')
            start_h = int(start[0])
            start_m = int(start[1])
            start_datetime = datetime(yyyy, mm, dd, start_h, start_m, 0)

            end = time[1].split(':')
            end_h = int(end[0])
            end_m = int(end[1])
            end_datetime = datetime(yyyy, mm, dd, end_h, end_m, 0)

            topic = hour[i * 3 + 1].strip()

            teacher = hour[i * 3 + 2].strip()
            place = hour[i * 3 + 3].strip()
            if topic != '-' and start_datetime > datetime.now():
                topic = topic[:-1].split(' (')
                topic = '[' + topic[1] + '] ' + TOPICS.get(topic[0], topic[0])

                event = {
                    "start": {
                        'dateTime': start_datetime.astimezone().isoformat(),
                        'timeZone': TIMEZONE
                    },
                    "end": {
                        'dateTime': end_datetime.astimezone().isoformat(),
                        'timeZone': TIMEZONE
                    },
                    "summary": topic,
                    "description": teacher,
                    "location": place
                }
                json_add_day_to_base(spec, event, json)


def json_add_day_to_base(spec, event, json):
    for s in json['specs']:
        if s['name'] == spec:
            s['events'].append(event)
            break


def generate_topics(legend):
    rows = get_trs(legend)
    rows = rows[1:]  # Skip Headers
    for row in rows:
        tds = get_tds(row)
        TOPICS[tds[0]] = tds[1]


class Scrapper:
    def __init__(self, link):
        content = get_page_content(link)

        tab_plan = content.find_all("table", {"class": "TabPlan"})
        tab_legend = content.find_all("table", {"class": "TabLegenda"})

        plan = tab_plan[0]

        if len(tab_legend) > 0:
            legend = tab_legend[1]
        else:
            legend = tab_plan[1]

        days = get_trs(plan)

        generate_topics(legend)

        specs = get_specs_names(days)

        self.json = generate_base_json(specs)

        days = days[1:]  # remove first row as specs already extracted

        days = clean_days(days)
        matching_indexes = [index for index, cell in enumerate(days[0]) if is_matching_regex(cell, HOUR_REGEX)]

        for day in days:
            day_to_json(day, matching_indexes, self.json)
