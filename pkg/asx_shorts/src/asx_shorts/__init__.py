"""asx_shorts: tidy ASIC daily short position reports."""
import io, datetime as dt, pandas as pd, requests
URL = "https://download.asic.gov.au/short-selling/RR{date}-001-SSDailyAggShortPos.csv"
__all__ = ["for_date", "latest"]
def _read(raw: bytes):
    """ASIC files have been plain CSV (checked Nov 2026); older ones were UTF-16 tab-separated."""
    try:
        df = pd.read_csv(io.BytesIO(raw))
        if df.shape[1] > 2: return df
    except Exception: pass
    return pd.read_csv(io.StringIO(raw.decode("utf-16", errors="ignore")), sep="\t")
def for_date(d: dt.date) -> pd.DataFrame:
    r = requests.get(URL.format(date=d.strftime("%Y%m%d")), timeout=30, headers={"User-Agent": "asx-shorts"}); r.raise_for_status()
    df = _read(r.content)
    df.columns = [c.strip() for c in df.columns]
    pc = next(c for c in df.columns if "%" in c)
    return df.rename(columns={pc: "pct_short", "Product Code": "code", "Product": "name"})[["code", "name", "pct_short"]].sort_values("pct_short", ascending=False)
def latest(max_back: int = 14):
    for b in range(max_back):
        d = dt.date.today() - dt.timedelta(days=b)
        try: return for_date(d), d
        except Exception: continue
    raise RuntimeError("No ASIC report found in the last %d days" % max_back)
