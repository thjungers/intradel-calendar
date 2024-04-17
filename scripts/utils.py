"""Utility functions for the project."""

from datetime import date, timedelta
from pathlib import Path
import arrow

ONEDAY = timedelta(days=1)
DEFAULT_ZONES_KEYWORD = "_"

def all_days_year(year: int, dayofweek: int) -> list[date]:
    range_start = date(year, 1, 1)
    range_end = date(year, 12, 31)

    dates = []
    cur_date = range_start
    while cur_date <= range_end:
        if cur_date.isoweekday() == dayofweek:
            dates.append(cur_date)
        cur_date += ONEDAY
    return dates

def print_dates(dates: list[date], quoted=True) -> None:
    template = "{date:%Y-%m-%d}"
    if quoted:
        template = '"' + template + '",'

    for date in dates:
        print(template.format(date=date))

def get_arrow_datetime(date: str, time: str, tz: str, day_offset: int) -> arrow.Arrow:
    return arrow.get(
        f"{date} {time} {tz}", 
        "YYYY-MM-DD HH:mm:ss ZZZ"
    ).shift(days=day_offset)

def make_ics_path(path: Path, zone: str) -> Path:
    if zone != DEFAULT_ZONES_KEYWORD:
        path = path.with_name(
            path.name + "_" + zone.replace(" ", "-").lower()
        )
    return path.with_suffix(".ics")