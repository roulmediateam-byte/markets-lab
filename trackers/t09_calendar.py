"""Economic calendar: events in the next 7 days, from config.yaml (keep the dates current)."""
import datetime as dt, pandas as pd
from lib.core import CFG, Result, TODAY
TITLE = "Economic calendar, next 7 days"
def run():
    ev = [e for e in CFG.get("economic_calendar", []) if TODAY <= dt.date.fromisoformat(str(e["date"])) <= TODAY + dt.timedelta(days=7)]
    if not ev: return None
    tab = pd.DataFrame(ev).set_index("date")
    return Result("t09_calendar", TITLE, [f"{e['date']}: {e['event']}" for e in ev], [], tab, headline=f"Coming up: {ev[0]['event']} ({ev[0]['date']}).", links=[("RBA calendar", "https://www.rba.gov.au/schedules-events/"), ("ABS release calendar", "https://www.abs.gov.au/release-calendar")])
