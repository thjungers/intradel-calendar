"""Read calendar data from json/*.json and generate corresponding ics/*.ics files."""

import json
from pathlib import Path

import arrow
import ics

from json_calendar_parser import JsonCalendarParser
from utils import DEFAULT_ZONES_KEYWORD

from pprint import pprint

ICS_OUTPUT = Path("ics/")
ICS_OUTPUT.mkdir(exist_ok=True)
GITHUB_PROJECT_URL = "https://github.com/thjungers/intradel-calendar"

def make_markdown_links(municipality, cal_paths, parser):
    """Make the markdown source for the links file, for a given municipality."""
    urls = parser.data["url"]

    links = [f"# {municipality}"]
    if not isinstance(urls, dict):
        # single URL
        links.append(f"[PDF source]({urls})")
    
    for zone, path in cal_paths:
        txt = municipality
        if zone != DEFAULT_ZONES_KEYWORD:
            txt += f" ({zone})"

        md = f"[{txt}]({GITHUB_PROJECT_URL}/releases/latest/download/{path.name})"

        if isinstance(urls, dict):
            # multiple URLs
            md += f" ([PDF source]({urls[zone]}))"

        links.append(md)

    return links


def main():
    links_md = []

    for json_file in Path("json").glob("*.json"):
        parser = JsonCalendarParser(json_file)
        cal_paths = parser.save_ics_calendars(ICS_OUTPUT / json_file.stem)
        links_md.extend(make_markdown_links(json_file.stem, cal_paths, parser))

    with Path("calendar_links.md").open("w") as file:
        file.write("\n\n".join(links_md))


if __name__ == "__main__":
    main()