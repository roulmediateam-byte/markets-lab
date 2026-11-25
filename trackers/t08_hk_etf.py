"""HK ETF premium/discount. Prices from Yahoo; NAV only if you add issuer NAV CSV URLs in config (check terms). Without NAV it reports price moves."""
import io, pandas as pd
from lib.core import CFG, Result, DEMO, prices, http_get, pct, save_csv
from lib import charts
TITLE = "Hong Kong ETF tracker"
def run():
    names = CFG["hk_etfs"]; px = prices(list(names))
    if px.empty: return None
    save_csv(px.tail(260), "t08_hk_etfs.csv")
    rows = []
    for t in px.columns:
        nav = None
        if DEMO: nav = px[t].iloc[-1] * 0.998
        elif t in CFG.get("hk_nav_csv_urls", {}):
            try: nav = float(pd.read_csv(io.StringIO(http_get(CFG["hk_nav_csv_urls"][t]).text)).iloc[-1]["NAV"])
            except Exception as e: print("NAV failed", t, e)
        prem = (px[t].iloc[-1] / nav - 1) if nav else None
        rows.append({"Ticker": t, "Name": names[t], "Price": round(px[t].iloc[-1], 3), "1 day": px[t].iloc[-1] / px[t].iloc[-2] - 1, "Premium/discount to NAV": prem})
    tab = pd.DataFrame(rows).set_index("Ticker")
    facts = [f"{r.Name}: {pct(r['1 day'])} on the day" + (f", trading at {r['Premium/discount to NAV']*100:+.2f}% to NAV." if pd.notna(r['Premium/discount to NAV']) else ".") for _, r in tab.iterrows()]
    c = charts.bars(tab["Name"].tolist(), tab["1 day"].tolist(), "Hong Kong ETFs, 1-day move", "t08")
    show = tab.copy(); show["1 day"] = show["1 day"].map(lambda x: f"{x*100:+.1f}%"); show["Premium/discount to NAV"] = show["Premium/discount to NAV"].map(lambda x: "n/a" if pd.isna(x) else f"{x*100:+.2f}%")
    return Result("t08_hk_etf", TITLE, facts, [c], show, headline=facts[0])
