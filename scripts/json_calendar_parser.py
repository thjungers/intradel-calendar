from collections import defaultdict
import json
from pathlib import Path
import arrow
import ics
from utils import get_arrow_datetime, make_ics_path, DEFAULT_ZONES_KEYWORD

TIMEZONE = "Europe/Brussels"
ICS_CREATOR = "IntradelCalendars"
EVENT_CREATED_DATE = arrow.now().shift(years=-1).replace(month=9, day=1, hour=12, minute=0, second=0)  # Required by the ICS specifications

class JsonCalendarParser:
    def __init__(self, file: Path) -> None:
        self.file = file
        self.zones = set()

        self._parse()

    def _parse(self) -> None:
        self._load_data()

        self.collection_types = self.data["collection_types"]

        self._validate()

        self.collection_events = self._get_collection_events()
        self.other_events = self._get_other_events()

    def _load_data(self) -> None:
        with self.file.open("r") as file:
            self.data = json.load(file)

    def _get_collection_event_config(self, collection_type):
        return self.data["collection_events"].get(
            collection_type, self.data["collection_events"][DEFAULT_ZONES_KEYWORD]
        )

    def _validate(self) -> None:
        """Validate the file against some rules.
        
        Raises: 
            ValueError: if the file is malformed.
        """
        # Collection types that are in "collections" but are not declared
        unexpected_collection_types = self.data["collections"].keys() - self.collection_types.keys()
        if unexpected_collection_types:
            raise ValueError(
                f"Unknown waste collection type(s) found in {self.file}: "
                f"{unexpected_collection_types}"
            )
        
        # Collection types that are declared but are not in "collections"
        missing_collection_types = self.collection_types.keys() - self.data["collections"].keys()
        if missing_collection_types:
            raise ValueError(
                f"Expected waste collection type(s) {missing_collection_types}, "
                f"not found in {self.file}"
            )
        
        # Dates that have a comment but are not in the "dates" field
        for collection_type, collection_group in self.data["collections"].items():
            for zone, zone_group in collection_group.items():
                missing_dates = zone_group["comments"].keys() - set(zone_group["dates"])
                if missing_dates:
                    raise ValueError(
                        f"Comments are provided for dates {missing_dates} "
                        f"for collection type {collection_type!r} (zone {zone!r}), "
                        "but these are not in the 'dates' field"
                    )
                
        # Collection event config with inverted start and end
        for collection_type, event_config in self.data["collection_events"].items():
            datetimes = {
                kind: get_arrow_datetime(
                    date="2020-09-01", 
                    time=event_config[kind]["time"],
                    tz=TIMEZONE,
                    day_offset=event_config[kind]["day_offset"],
                )
                for kind in ("start", "end")
            }

            if datetimes["end"] <= datetimes["start"]:
                raise ValueError(
                    f"Invalid collection event config for collection type {collection_type!r} in {self.file}: "
                    "the end datetime must be after the start datetime."
                )
        
    def _get_collection_events(self) -> dict[str, list[ics.Event]]:
        events = defaultdict(list)

        for collection_type, collection_event_name in self.collection_types.items():
            zones = self.data["collections"][collection_type]

            for zone_name, zone in zones.items():
                self.zones.add(zone_name)

                for collection_date in zone["dates"]:
                    name = collection_event_name
                    if comment := zone["comments"].get(collection_date):
                        name += f" ({comment})"

                    datetimes = self._make_collection_event_datetimes(collection_date, collection_type)

                    events[zone_name].append(
                        ics.Event(
                            name=name,
                            begin=datetimes["start"],
                            end=datetimes["end"],
                            created=EVENT_CREATED_DATE,
                            last_modified=arrow.utcnow(),
                        )
                    )
            
        return events

    def _make_collection_event_datetimes(
        self, collection_date: str, collection_type: str
    ) -> dict[str, arrow.Arrow]:
        datetimes = {
            kind: get_arrow_datetime(
                date=collection_date, 
                time=self._get_collection_event_config(collection_type)[kind]['time'],
                tz=TIMEZONE, 
                day_offset=self._get_collection_event_config(collection_type)[kind]["day_offset"],
            )
            for kind in ("start", "end")
        }
        
        return datetimes
    
    def _get_other_events(self) -> list[ics.Event]:
        events = []

        for json_event in self.data["events"]:
            event = ics.Event(
                name=json_event["name"],
                begin=json_event["date"],
                created=EVENT_CREATED_DATE,
                last_modified=arrow.utcnow(),
                location=json_event["location"]
            )
            event.make_all_day()
            events.append(event)

        return events
    
    def get_ics_calendars(self) -> dict[str, ics.Calendar]:
        calendars = {}

        zones = list(self.collection_events.keys())
        try:
            zones.remove(DEFAULT_ZONES_KEYWORD)
        except ValueError:
            # "_" not in zones: ok
            pass

        if not zones:
            zones = [DEFAULT_ZONES_KEYWORD]

        for zone in zones:
            events = self.collection_events.get(zone, [])
            if zone != DEFAULT_ZONES_KEYWORD:
                events.extend(self.collection_events.get(DEFAULT_ZONES_KEYWORD, []))
            events.extend(self.other_events)

            calendars[zone] = ics.Calendar(events=events, creator=ICS_CREATOR)

        return calendars

    def save_ics_calendars(self, path: Path) -> list[tuple[str, Path]]:
        """Save the ICS calendar files to the given path. The path is appended with the zone name 
        (except if there are no zones) and the .ics extension.
        """
        calendars = self.get_ics_calendars()

        paths = []
        for zone, calendar in calendars.items():
            calendar_path = make_ics_path(path, zone)
            paths.append((zone, calendar_path))
            self._save_ics_calendar(calendar, calendar_path)
        
        return paths
        
    def _save_ics_calendar(self, calendar: ics.Calendar, path: Path) -> None:
        """Save a single ICS calendar to the given path."""
        with path.open("w", newline="") as file:
            file.writelines(calendar.serialize_iter())