"""Australian government bond yield curve from RBA table F2."""
import pandas as pd
from lib.core import CFG, Result, rba_table, save_csv, load_state, save_state, DEMO
from lib import charts
TITLE = "Australian yield curve (RBA F2)"
def run():
    df = rba_table(CFG["rba_tables"]["yields"])
    cols = [c for c in df.columns if any(k in c for k in ("2 year", "3 year", "5 year", "10 year", "2y", "3y", "5y", "10y"))][:4]
    if not cols or len(df) < 30: return None
    df = df[cols].dropna(); save_csv(df.tail(260), "t02_yields.csv")
    if load_state("t02").get("last") == str(df.index[-1].date()) and not DEMO: return None
    save_state("t02", {"last": str(df.index[-1].date())})
    labels = ["2y", "3y", "5y", "10y"][:len(cols)]
    now, mago = df.iloc[-1], df.iloc[-22]
    c = charts.curve(labels, {f"Latest ({df.index[-1]:%d %b})": now.values, f"1 month ago ({df.index[-22]:%d %b})": mago.values}, "Australian government bond yield curve", "t02")
    slope = now.iloc[-1] - now.iloc[0]
    facts = [f"Data as at {df.index[-1]:%d %b %Y}."] + [f"{l} yield {v:.2f}% ({(v - m)*100:+.0f} bp over a month)." for l, v, m in zip(labels, now.values, mago.values)] + [f"10y minus 2y slope: {slope*100:+.0f} bp ({'upward sloping' if slope > 0 else 'inverted'})."]
    tab = pd.DataFrame({"Latest (%)": now.values, "1 month ago (%)": mago.values, "Change (bp)": (now.values - mago.values) * 100}, index=labels).round(2)
    return Result("t02_yield_curve", TITLE, facts, [c], tab, headline=f"AU 10y at {now.iloc[-1]:.2f}%, curve slope {slope*100:+.0f} bp.", links=[("RBA table F2", "https://www.rba.gov.au/statistics/tables/")])
