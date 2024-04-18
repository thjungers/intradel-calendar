"""Utility functions for the project."""

from datetime import date, timedelta
from pathlib import Path
import re
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

def get_changelog_version(version_tag: str) -> str:
    """Extract the changelog for the given version tag from CHANGELOG.md.
    
    Parameters:
        version_tag: The version tag, optionnaly prepended by "refs/tags/".
    """
    version = re.match("^(?:refs/tags/)?(v.*)$", version_tag).group(1) # type: ignore

    root = Path(__file__).parent.parent

    changelog = []

    with (root / "CHANGELOG.md").open("r") as file:
        while line := file.readline():
            if line.strip() == f"# {version}":
                break
        else:
            raise ValueError(f"Section for version {version} not found in CHANGELOG.md")
        
        while line := file.readline():
            if line.startswith("# "):
                break

            line = line.strip()
            if line:
                changelog.append(line)

    return "\n".join(changelog)