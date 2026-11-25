from lib.core import CFG
from ._price import movers
TITLE = "AUD FX dashboard"
def run(): return movers("t04_fx", TITLE, CFG["fx"], extra_vol=True, line_cols=list(CFG["fx"])[:2])
