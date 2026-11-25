"""Shared builder for price-based trackers (FX, volatility, commodities, sectors)."""
from lib.core import Result, prices, save_csv, pct, TODAY
from lib import charts
import pandas as pd, numpy as np
def movers(tid, title, names, extra_vol=False, line_cols=None):
    px = prices(list(names))
    px = px.loc[:, px.iloc[-1].notna() & px.iloc[-2].notna() & px.iloc[-22].notna()]   # drop series with missing recent prices
    if px.empty or len(px) < 30: return None
    save_csv(px.tail(260), f"{tid}.csv")
    d1 = px.iloc[-1] / px.iloc[-2] - 1; w1 = px.iloc[-1] / px.iloc[-6] - 1; m1 = px.iloc[-1] / px.iloc[-22] - 1
    tab = pd.DataFrame({"Name": [names[c] for c in px.columns], "Last": px.iloc[-1].round(4), "1 day": d1, "1 week": w1, "1 month": m1})
    if extra_vol:
        tab["1m realised vol"] = (np.log(px).diff().tail(21).std() * np.sqrt(252))
    tab = tab.sort_values("1 day", ascending=False)
    facts = [f"{names[c]}: {pct(tab.loc[c,'1 day'])} on the day, {pct(tab.loc[c,'1 month'])} over a month." for c in tab.index]
    ch = [charts.bars([names[c] for c in tab.index], tab["1 day"].tolist(), f"{title}, 1-day move, {TODAY:%d %b %Y}", tid)]
    if line_cols: ch.append(charts.lines(px[line_cols].tail(126), f"{title}, last 6 months (rebased)", tid + "_6m", rebase=True))
    show = tab.copy()
    for c in ("1 day", "1 week", "1 month") + (("1m realised vol",) if extra_vol else ()): show[c] = show[c].map(lambda x: f"{x*100:+.1f}%")
    big = tab["1 day"].abs().idxmax()
    return Result(tid, title, facts, ch, show, headline=f"{title}: biggest move {names[big]} {pct(tab.loc[big,'1 day'])}.")
