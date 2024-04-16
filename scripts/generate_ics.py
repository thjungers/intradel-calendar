"""Read calendar data from json/*.json and generate corresponding ics/*.ics files."""

import json
from pathlib import Path

import arrow
import ics

from json_calendar_parser import JsonCalendarParser

from pprint import pprint

ICS_OUTPUT = Path("ics/")

def main():
    for json_file in Path("json").glob("*.json"):
        parser = JsonCalendarParser(json_file)
        parser.save_ics_calendars(ICS_OUTPUT / json_file.stem)


if __name__ == "__main__":
    main()