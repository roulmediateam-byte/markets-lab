"""13F tracker: when a listed US fund files a new 13F-HR with the SEC, show its largest holdings and changes."""
import re, pandas as pd, xml.etree.ElementTree as ET
from lib.core import CFG, Result, DEMO, http_get, load_state, save_state, save_csv
from lib import charts
TITLE = "13F tracker (US fund holdings)"
UA = CFG["sec_user_agent"]
def holdings(cik, acc):
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}"
    files = http_get(base + "/index.json", UA).json()["directory"]["item"]
    xmlf = next(f["name"] for f in files if f["name"].endswith(".xml") and "primary" not in f["name"].lower())
    root = ET.fromstring(http_get(f"{base}/{xmlf}", UA).content)
    ns = {"n": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
    q = (lambda e, t: e.find(f"n:{t}", ns)) if ns else (lambda e, t: e.find(t))
    rows = [{"Issuer": q(e, "nameOfIssuer").text, "Value ($)": float(q(e, "value").text)} for e in root.iter(root.tag.split("}")[0] + "}infoTable" if ns else "infoTable")]
    return pd.DataFrame(rows).groupby("Issuer").sum().sort_values("Value ($)", ascending=False)
def run():
    st = load_state("t16"); facts, tabs, chs = [], [], []
    for cik, name in CFG["sec_13f_filers"].items():
        try:
            if DEMO:
                acc, h = "demo", pd.DataFrame({"Value ($)": [9e9, 5e9, 3e9, 2e9, 1e9]}, index=["Apple", "Bank of America", "American Express", "Coca-Cola", "Chevron"])
            else:
                sub = http_get(f"https://data.sec.gov/submissions/CIK{cik}.json", UA).json()["filings"]["recent"]
                i = next(i for i, f in enumerate(sub["form"]) if f == "13F-HR"); acc = sub["accessionNumber"][i]
                if st.get(cik) == acc: continue
                h = holdings(cik, acc)
            st[cik] = acc; top = h.head(10); save_csv(h, f"t16_{cik}.csv")
            facts.append(f"{name} filed a new 13F. Largest holding: {top.index[0]} (${top.iloc[0,0]/1e9:.1f}bn reported value).")
            chs.append(charts.bars(top.index.tolist(), (top["Value ($)"] / top["Value ($)"].sum()).tolist(), f"{name}: top 10 holdings, share of top 10", f"t16_{cik}", fmt="{:.0f}%"))
        except Exception as e: print("13F failed", name, e)
    save_state("t16", st)
    if not facts: return None
    return Result("t16_13f", TITLE, facts + ["13F filings are delayed up to 45 days after quarter end and show only US long positions."], chs, None, headline=facts[0], links=[("SEC EDGAR", "https://www.sec.gov/edgar/search/")])
