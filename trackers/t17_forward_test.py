"""Live forward test. Each run logs tomorrow's signal (committed with a timestamp) and scores yesterday's.
Replace signal() with your own model; keep the logging so the record stays honest."""
import os, pandas as pd, numpy as np, datetime as dt
from lib.core import CFG, Result, prices, DATA, TODAY, pct
from lib import charts
TITLE = "Live forward test (paper)"
LOG = os.path.join(DATA, "forward_test_log.csv")
def signal(close):      # 1 = long, 0 = cash. Placeholder rule: 20-day vs 50-day average.
    return int(close.rolling(20).mean().iloc[-1] > close.rolling(50).mean().iloc[-1])
def run():
    t = CFG["forward_test"]["ticker"]; px = prices([t])
    if px.empty: return None
    close = px[t].dropna(); log = pd.read_csv(LOG) if os.path.exists(LOG) else pd.DataFrame(columns=["signal_date", "logged_at_utc", "signal", "next_return", "strategy_return"])
    ret = close.iloc[-1] / close.iloc[-2] - 1
    if len(log) and pd.isna(log.iloc[-1]["next_return"]):
        log.loc[log.index[-1], "next_return"] = ret; log.loc[log.index[-1], "strategy_return"] = ret * float(log.iloc[-1]["signal"])
    if not len(log) or str(log.iloc[-1]["signal_date"]) != str(close.index[-1].date()):
        log.loc[len(log)] = [str(close.index[-1].date()), dt.datetime.utcnow().isoformat(timespec="seconds"), signal(close), np.nan, np.nan]
    log.to_csv(LOG, index=False)
    done = log.dropna(subset=["strategy_return"])
    facts = [f"Signal for next session: {'long' if log.iloc[-1]['signal'] == 1 else 'cash'} (rule: {CFG['forward_test']['rule'].split('.')[0]}).", f"Live record: {len(done)} scored days since the log started."]
    chs = []
    if len(done) >= 5:
        eq = pd.DataFrame({"Strategy": (1 + done["strategy_return"].astype(float)).cumprod(), "Buy and hold": (1 + done["next_return"].astype(float)).cumprod()})
        eq.index = pd.to_datetime(done["signal_date"]); chs.append(charts.lines(eq * 100, "Forward test since start (rebased to 100)", "t17"))
        facts.append(f"Strategy {pct(eq['Strategy'].iloc[-1]-1)} vs buy and hold {pct(eq['Buy and hold'].iloc[-1]-1)} since the log started.")
    facts.append("Paper trading only; no real money. Every signal is committed to GitHub before the next session, so it cannot be changed afterwards.")
    return Result("t17_forward_test", TITLE, facts, chs, log.tail(10).set_index("signal_date"), headline=facts[0])
