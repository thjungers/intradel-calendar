import sys
from utils import get_changelog_version

if len(sys.argv) != 2:
    print("Usage: ./get_changelog_version.py version_tag")
    exit(1)

print(get_changelog_version(sys.argv[1]))