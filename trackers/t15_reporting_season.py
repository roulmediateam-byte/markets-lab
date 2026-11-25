from lib.core import TODAY, DEMO
from ._announce import of_kind, build
TITLE = "Reporting season tracker"
def run():
    if TODAY.month not in (2, 8) and not DEMO: return None     # ASX reporting seasons
    return build("t15_reporting_season", TITLE, of_kind("results"), "Summarise today's results announcements")
