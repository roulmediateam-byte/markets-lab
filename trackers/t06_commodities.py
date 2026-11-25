from lib.core import CFG
from ._price import movers
TITLE = "Commodities and ASX miners"
def run(): return movers("t06_commodities", TITLE, {**CFG["commodities"], **CFG["miners"]}, line_cols=list(CFG["commodities"])[:2])
