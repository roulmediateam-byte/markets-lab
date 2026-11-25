from ._announce import items, build
TITLE = "ASX announcements digest"
def run(): return build("t11_announcements", TITLE, items(), "Summarise today's ASX announcements")
