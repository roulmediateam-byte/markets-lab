"""Macro release watcher: posts only on days a new CPI or labour-force observation appears (RBA tables G1 and H5, which mirror ABS releases)."""
import pandas as pd
from lib.core import CFG, Result, rba_table, load_state, save_state, DEMO
from lib import charts
TITLE = "New macro data (CPI, jobs)"
def run():
    st = load_state("t10"); facts, chs = [], []
    for key, label, pick in (("cpi", "Inflation", lambda c: "Year-ended" in c and "inflation" in c.lower()), ("labour", "Unemployment rate", lambda c: "Unemployment rate" in c)):
        try: df = rba_table(CFG["rba_tables"][key])
        except Exception as e: print("table failed", key, e); continue
        col = next((c for c in df.columns if pick(c)), None)
        if not col: continue
        s = df[col].dropna(); last = str(s.index[-1].date())
        if st.get(key) == last and not DEMO: continue
        st[key] = last
        facts.append(f"{label}: {s.iloc[-1]:.1f}% for the period ending {s.index[-1]:%b %Y}, previous {s.iloc[-2]:.1f}%.")
        chs.append(charts.lines(s.tail(40).to_frame(label), f"{label} (%)", f"t10_{key}"))
    save_state("t10", st)
    if not facts: return None
    return Result("t10_abs_releases", TITLE, facts, chs, None, headline=facts[0], links=[("ABS", "https://www.abs.gov.au/"), ("RBA tables", "https://www.rba.gov.au/statistics/tables/")])
