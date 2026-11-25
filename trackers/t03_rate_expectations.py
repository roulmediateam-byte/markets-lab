"""RBA rate expectations proxy: 3-month and 6-month bank bill rates (BABs/NCDs) versus the cash rate target, from RBA table F1.
Bills carry a small credit and term premium, so only large gaps are read as a lean. (RBA F1 OIS columns were found empty in Nov 2026.)"""
from lib.core import CFG, Result, rba_table, save_csv, load_state, save_state, DEMO
from lib import charts
TITLE = "RBA rate expectations (bank bill proxy)"
def run():
    df = rba_table(CFG["rba_tables"]["money_market"])
    if DEMO: df = df.rename(columns={"3-month BBSW": "3-month BABs/NCDs"}); df["6-month BABs/NCDs"] = df["3-month BABs/NCDs"] + 0.05
    find = lambda k: next((c for c in df.columns if k in c), None)
    cols = {find("Cash Rate Target"): "Cash rate target", find("3-month BABs"): "3-month bank bill", find("6-month BABs"): "6-month bank bill"}
    if None in cols: return None
    d = df[list(cols)].rename(columns=cols).dropna().tail(260)
    if (df.index[-1] - d.index[-1]).days > 10: return None      # stale series, do not post
    save_csv(d, "t03_rates.csv")
    st = load_state("t03")
    if st.get("last") == str(d.index[-1].date()) and not DEMO: return None
    save_state("t03", {"last": str(d.index[-1].date())})
    s3 = (d["3-month bank bill"] - d["Cash rate target"]).iloc[-1] * 100; s6 = (d["6-month bank bill"] - d["Cash rate target"]).iloc[-1] * 100
    lean = lambda s: "a hike" if s > 25 else "a cut" if s < -10 else "no clear move"
    c = charts.lines(d.tail(130), "Cash rate target vs bank bills (%)", "t03")
    facts = [f"Data as at {d.index[-1]:%d %b %Y}.", "Bank bills include a small credit and term premium, so this is a rough guide; the ASX RBA Rate Tracker is the direct measure.", f"Cash rate target {d['Cash rate target'].iloc[-1]:.2f}%.",
             f"3-month bank bill {d['3-month bank bill'].iloc[-1]:.2f}% ({s3:+.0f} bp vs cash), leaning toward {lean(s3)} within three months.",
             f"6-month bank bill {d['6-month bank bill'].iloc[-1]:.2f}% ({s6:+.0f} bp vs cash), leaning toward {lean(s6)} within six months."]
    return Result("t03_rate_expectations", TITLE, facts, [c], None, headline=f"Bank bills vs RBA cash rate: 3m {s3:+.0f} bp, 6m {s6:+.0f} bp.", links=[("RBA table F1", "https://www.rba.gov.au/statistics/tables/"), ("ASX RBA Rate Tracker", "https://www.asx.com.au/markets/trade-our-derivatives-market/futures-market/rba-rate-tracker")])
