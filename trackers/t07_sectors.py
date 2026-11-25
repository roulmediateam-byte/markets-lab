from lib.core import CFG
from ._price import movers
TITLE = "ASX sector heatmap"
def run(): return movers("t07_sectors", TITLE, CFG["sectors"])
