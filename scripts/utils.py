"""Utility functions for the project."""

from datetime import date, timedelta
import arrow

ONEDAY = timedelta(days=1)

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