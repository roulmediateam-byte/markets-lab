from ._announce import of_kind, build
TITLE = "Australian M&A log"
def run(): return build("t13_mna", TITLE, of_kind("mna"), "Summarise today's M&A announcements")
