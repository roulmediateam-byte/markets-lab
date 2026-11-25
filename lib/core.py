"""Shared helpers: config, dates, data access (live or DEMO), results."""
import os, io, json, datetime as dt, hashlib, random
from dataclasses import dataclass, field
import numpy as np, pandas as pd, requests, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.environ.get("DEMO", "0") == "1"
CFG = yaml.safe_load(open(os.path.join(ROOT, "config.yaml")))
TODAY = dt.date.fromisoformat(os.environ["RUN_DATE"]) if os.environ.get("RUN_DATE") else dt.date.today()
DATA = os.path.join(ROOT, "data"); OUT = os.path.join(ROOT, "out"); SITE = os.path.join(ROOT, "site")
for d in (DATA, OUT, SITE, os.path.join(OUT, "charts")): os.makedirs(d, exist_ok=True)

@dataclass
class Result:
    id: str                 # e.g. "t01_short_interest"
    title: str
    facts: list             # plain-English factual lines (fed to the AI note and to posts)
    charts: list = field(default_factory=list)   # PNG paths
    table: pd.DataFrame | None = None
    headline: str = ""      # one line for social posts
    links: list = field(default_factory=list)    # (label, url) to original sources

def _seed(s): return int(hashlib.md5((s + str(TODAY)).encode()).hexdigest()[:8], 16)

def prices(tickers, days=400):
    """Daily closes, columns = tickers. Missing tickers are dropped."""
    tickers = list(tickers)
    if DEMO:
        idx = pd.bdate_range(end=TODAY, periods=days)
        out = {}
        for t in tickers:
            rng = np.random.default_rng(_seed(t) % (2**32))
            out[t] = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.011, len(idx))))
        return pd.DataFrame(out, index=idx)
    import yfinance as yf
    df = yf.download(tickers, period=f"{int(days*1.5)}d", auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series): df = df.to_frame(tickers[0])
    return df.dropna(axis=1, how="all").ffill().dropna(how="all")

def http_get(url, ua=None, timeout=30):
    r = requests.get(url, headers={"User-Agent": ua or "markets-lab/1.0 (research project)"}, timeout=timeout)
    r.raise_for_status(); return r

def _dates(vals):
    vals = pd.Series([v.strip() for v in vals]); out = pd.to_datetime(vals, format="%d-%b-%Y", errors="coerce")
    for fmt in ("%d/%m/%Y", "%b-%Y", "%Y-%m-%d"):
        out = out.fillna(pd.to_datetime(vals, format=fmt, errors="coerce"))
    return pd.DatetimeIndex(out)

def rba_table(url):
    """Parse an RBA statistical-table CSV into a DataFrame indexed by date, columns = series titles."""
    if DEMO:
        idx = pd.bdate_range(end=TODAY, periods=300)
        rng = np.random.default_rng(_seed(url) % (2**32))
        base = {"f2": {"2y": 3.6, "3y": 3.7, "5y": 3.9, "10y": 4.4}, "f1": {"Cash Rate Target": 3.6, "3-month BBSW": 3.75},
                "g1": {"Year-ended inflation": 2.8}, "h5": {"Unemployment rate": 4.2}}
        key = "f2" if "f2" in url else "f1" if "f1" in url else "g1" if "g1" in url else "h5"
        return pd.DataFrame({k: v + np.cumsum(rng.normal(0, 0.02, len(idx))) for k, v in base[key].items()}, index=idx)
    raw = http_get(url).content
    try: text = raw.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError: text = raw.decode("latin-1").splitlines()
    rows = [r.split(",") for r in text]
    title = next(r for r in rows if r and r[0].strip() == "Title")[1:]
    start = next(i for i, r in enumerate(rows) if r and r[0].strip() == "Series ID") + 1
    data = [r for r in rows[start:] if r and r[0].strip()]
    df = pd.DataFrame([(r[1:] + [""] * len(title))[:len(title)] for r in data], index=_dates([r[0] for r in data]), columns=title)
    df = df[df.index.notna() & (df.index <= pd.Timestamp(TODAY))]   # drop undated rows and forecast dates
    return df.apply(pd.to_numeric, errors="coerce").dropna(how="all").sort_index()

def feed_items(urls, kind="news", n=60):
    """Return list of dicts {title, link, published} from RSS/Atom feeds."""
    if DEMO:
        rng = random.Random(_seed(kind))
        words = {"news": ["ASX 200 edges higher as miners rally", "Bank shares slip on margin concerns", "Iron ore price climbs on China stimulus hopes", "Tech stocks fall after weak US guidance", "RBA minutes signal patient approach", "Gold hits record as dollar weakens"],
                 "announcements": ["Placement and share purchase plan to raise $45m", "Appendix 3Y change of director's interest notice", "Scheme implementation deed with acquirer", "Half year results and dividend", "Quarterly activities report", "Trading halt pending capital raising"],
                 "jobs": ["Graduate Analyst 2027, Investment Banking", "Graduate Program 2027, Markets", "Analyst, Equity Research", "Graduate, Valuations and Modelling"]}[kind]
        return [{"title": f"DEMO: {rng.choice(['ABC', 'XYZ', 'QRS', 'LMN'])} {rng.choice(words)}", "link": "https://example.com", "published": str(TODAY)} for _ in range(min(n, 12))]
    import feedparser
    items = []
    for u in urls:
        try:
            for e in feedparser.parse(u).entries[:n]:
                items.append({"title": e.get("title", ""), "link": e.get("link", ""), "published": e.get("published", "")})
        except Exception as ex:
            print("feed failed", u, ex)
    return items

def save_csv(df, name):
    p = os.path.join(DATA, name); df.to_csv(p); return p

def load_state(name, default=None):
    p = os.path.join(DATA, f"state_{name}.json")
    return json.load(open(p)) if os.path.exists(p) else (default if default is not None else {})

def save_state(name, obj):
    json.dump(obj, open(os.path.join(DATA, f"state_{name}.json"), "w"), indent=1, default=str)

def pct(x): return f"{x*100:+.1f}%"
