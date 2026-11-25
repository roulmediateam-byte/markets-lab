from ._announce import of_kind, build
TITLE = "ASX capital raisings"
def run(): return build("t12_capital_raisings", TITLE, of_kind("capital"), "Summarise today's capital raisings")
