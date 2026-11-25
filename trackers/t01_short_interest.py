"""ASX short interest from ASIC's daily aggregated short position reports (published with a lag of a few days)."""
import datetime as dt, io, pandas as pd, numpy as np
from lib.core import CFG, Result, DEMO, TODAY, http_get, save_csv, load_state, save_state
from lib import charts
TITLE = "ASX short interest (ASIC)"
def _read(raw: bytes):
    """ASIC files have been plain CSV (checked Nov 2026); older ones were UTF-16 tab-separated."""
    try:
        df = pd.read_csv(io.BytesIO(raw))
        if df.shape[1] > 2: return df
    except Exception: pass
    return pd.read_csv(io.StringIO(raw.decode("utf-16", errors="ignore")), sep="\t")
def _fetch():
    if DEMO:
        rng = np.random.default_rng(1); codes = [f"DM{i:02d}" for i in range(40)]
        return pd.DataFrame({"Product Code": codes, "Product": [f"Demo Company {c}" for c in codes], "% Short": rng.gamma(2, 2, 40)}), str(TODAY)
    for back in range(3, 12):
        d = TODAY - dt.timedelta(days=back)
        try:
            raw = http_get(CFG["asic_short_url_pattern"].format(date=d.strftime("%Y%m%d"))).content
            df = _read(raw)
            df.columns = [c.strip() for c in df.columns]
            pc = [c for c in df.columns if "%" in c][0]
            return df.rename(columns={pc: "% Short"})[["Product Code", "Product", "% Short"]], str(d)
        except Exception: continue
    return None, None
def run():
    df, asof = _fetch()
    if df is None: return None
    st = load_state("t01")
    if st.get("asof") == asof: return None            # nothing new since last run
    df["% Short"] = pd.to_numeric(df["% Short"], errors="coerce"); df = df.dropna()
    df = df[df["Product"].str.contains("ORD", case=False, na=False) | DEMO].sort_values("% Short", ascending=False)   # ordinary shares only; ETF units can exceed 100%
    prev = pd.Series(st.get("prev", {}), dtype=float)
    df["Change (pts)"] = df["Product Code"].map(prev).rsub(df["% Short"]) if len(prev) else np.nan
    save_csv(df.set_index("Product Code"), "t01_short_interest.csv")
    save_state("t01", {"asof": asof, "prev": dict(zip(df["Product Code"], df["% Short"]))})
    top = df.head(10)
    facts = [f"Data as at {asof} (ASIC publishes with a lag)."] + [f"{r['Product Code']} {r['% Short']:.1f}% of shares on issue reported short." for _, r in top.head(5).iterrows()]
    if df["Change (pts)"].notna().any():
        big = df.loc[df["Change (pts)"].abs().idxmax()]; facts.append(f"Biggest change: {big['Product Code']} {big['Change (pts)']:+.1f} points.")
    c = charts.bars(top["Product Code"].tolist(), (top["% Short"] / 100).tolist(), f"Most-shorted ASX stocks, as at {asof}", "t01", fmt="{:.1f}%")
    return Result("t01_short_interest", TITLE, facts, [c], top.set_index("Product Code").round(2).fillna("-"), headline=f"Most-shorted on the ASX: {top.iloc[0]['Product Code']} at {top.iloc[0]['% Short']:.1f}%.", links=[("ASIC short position reports", "https://asic.gov.au/regulatory-resources/markets/short-selling/short-position-reports-table/")])
