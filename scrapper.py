import pandas as pd
import re
from datetime import datetime

DAY_REGEX = r'\b(?:Poniedziałek|Wtorek|Środa|Czwartek|Piątek|Sobota|Niedziela) \d{4}-\d{2}-\d{2}\b'
HOUR_REGEX = r'\d{2}:\d{2}-\d{2}:\d{2}'
TIMEZONE = 'Europe/Warsaw'
NO_OF_COLUMNS = 3


def is_matching_regex(cell, regex):
    pattern = re.compile(regex)
    return True if pattern.match(cell) else False


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


def prettify_topic(topic, legend):
    t = topic[:-1].split(' (')
    return '[' + t[1] + '] ' + legend.get(t[0], t[0])


def create_event(json, start_datetime, end_datetime, topic, teacher, location, spec):
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
        "location": location
    }

    for s in json['specs']:
        if s['name'] == spec:
            s['events'].append(event)
            break


def process_plan(df, legend, json, from_datetime, specs):
    # Remove empty rows
    df = df.dropna(subset=[0])

    # Get dimensions
    no_of_columns = len(df.columns)
    no_of_rows = len(df)

    # Initialize variables
    date = None
    start_datetime = None
    end_datetime = None
    topic = None
    teacher = None
    location = None
    spec = None

    # Scan plan
    j = 0
    for i in range(no_of_rows):
        while j < no_of_columns:
            cell = df.iloc[i][j]
            if is_matching_regex(cell, DAY_REGEX):
                date = cell.split(' ')[1].split('-')
                break
            elif is_matching_regex(cell, HOUR_REGEX):
                times = cell.split('-')
                start = times[0].split(':')
                end = times[1].split(':')
                start_datetime = datetime(int(date[0]), int(date[1]), int(date[2]), int(start[0]), int(start[1]), 0)
                end_datetime = datetime(int(date[0]), int(date[1]), int(date[2]), int(end[0]), int(end[1]), 0)
                j += 1
            elif cell.strip() != '-':
                # If any more columns appear add here
                topic = prettify_topic(cell, legend)
                teacher = df.iloc[i][j + 1]
                location = df.iloc[i][j + 2]
                spec = specs[int(j / NO_OF_COLUMNS)]

                # Check if start_datetime exists and any timeframe applied
                if not from_datetime or start_datetime >= from_datetime:
                    create_event(json, start_datetime, end_datetime, topic, teacher, location, spec)
                j += NO_OF_COLUMNS
            else:
                j += NO_OF_COLUMNS
        j = 0


def find_specs(df):
    # Extracting specs
    specs = []
    no_of_columns = len(df.columns)
    i = 1
    while i < no_of_columns:
        specs.append(df.iloc[0][i])
        i += NO_OF_COLUMNS
    return specs


def create_legend_map(df):
    legend = dict()
    no_of_rows = len(df)

    for i in range(1, no_of_rows):
        legend[df.iloc[i][0]] = df.iloc[i][1]
    return legend


class Scrapper:
    def __init__(self, link, from_datetime=None):
        # Find all tables and load to DataFrame
        tables = pd.read_html(link, attrs={'class': 'TabPlan'}, encoding='ISO-8859-2')
        plan = tables[0]
        legend = tables[1]

        # Find specs and initialize json
        specs = find_specs(plan)

        # Initialize JSON based on specs
        self.json = generate_base_json(specs)

        # Create legend map
        legend_map = create_legend_map(legend)

        # Process plan
        process_plan(plan, legend_map, self.json, from_datetime, specs)
