from ._announce import of_kind, build
TITLE = "Director trades (Appendix 3Y)"
def run(): return build("t14_director_trades", TITLE, of_kind("director"), "Summarise today's director interest notices")
