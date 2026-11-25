from lib.core import CFG
from ._price import movers
TITLE = "Volatility monitor"
def run(): return movers("t05_volatility", TITLE, CFG["volatility"], extra_vol=True)
