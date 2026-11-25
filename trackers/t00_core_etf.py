"""Core daily ETF report: 1-day, 1-month and YTD moves for a fixed ASX ETF list, plus volume of the day's story."""
from lib.core import CFG, Result, prices, save_csv, pct, TODAY
from lib import charts
import pandas as pd
TITLE = "Daily ASX ETF report"
def run():
    names = CFG["core_etfs"]; px = prices(list(names) + [CFG["benchmark"]])
    if px.empty or len(px) < 30: return None
    save_csv(px.tail(260), "core_etf_prices.csv")
    last = px.iloc[-1]; d1 = px.iloc[-1] / px.iloc[-2] - 1; m1 = px.iloc[-1] / px.iloc[-22] - 1
    ytd_base = px[px.index.year == px.index[-1].year].iloc[0]; ytd = last / ytd_base - 1
    tab = pd.DataFrame({"Name": [names.get(t, "ASX 200 index") for t in px.columns], "1 day": d1, "1 month": m1, "YTD": ytd}).sort_values("1 day", ascending=False)
    etf = tab.drop(CFG["benchmark"], errors="ignore")
    best, worst = etf.index[0], etf.index[-1]
    facts = [f"ASX 200 moved {pct(d1.get(CFG['benchmark'], 0))} on the day." ,
             f"Best ETF on the list: {best} ({names[best]}) {pct(etf.loc[best,'1 day'])}.",
             f"Weakest: {worst} ({names[worst]}) {pct(etf.loc[worst,'1 day'])}.",
             f"Over one month the best was {etf['1 month'].idxmax()} at {pct(etf['1 month'].max())}."]
    c1 = charts.bars([f"{t} {names[t][:22]}" for t in etf.index], etf["1 day"].tolist(), f"ASX ETFs, 1-day move, {TODAY:%d %b %Y}", "core_1d")
    c2 = charts.lines(px[list(etf.index[:3]) + [etf.index[-1]]].tail(66), "Last 3 months, rebased to 100", "core_3m", rebase=True)
    show = tab.copy()
    for c in ("1 day", "1 month", "YTD"): show[c] = show[c].map(lambda x: f"{x*100:+.1f}%")
    return Result("t00_core_etf", TITLE, facts, [c1, c2], show, headline=f"ASX 200 {pct(d1.get(CFG['benchmark'],0))}; best ETF on the list {best} {pct(etf.loc[best,'1 day'])}, weakest {worst} {pct(etf.loc[worst,'1 day'])}.")
