"""ETF screener and DCF calculator. Deploy free on Streamlit Community Cloud (New app > this repo > app/streamlit_app.py).
Data refreshes automatically: it reads the CSV the daily build commits."""
import pandas as pd, streamlit as st
RAW = "https://raw.githubusercontent.com/roulmediateam-byte/markets-lab/main/data/core_etf_prices.csv"
st.set_page_config(page_title="Markets Lab tools", layout="wide")
st.title("Markets Lab: ETF screener and DCF calculator"); st.caption("General information only, not financial advice.")
tab1, tab2 = st.tabs(["ETF screener", "DCF calculator"])
with tab1:
    px = pd.read_csv(RAW, index_col=0, parse_dates=True)
    win = st.select_slider("Window", ["1 week", "1 month", "3 months", "6 months", "1 year"], "1 month")
    n = {"1 week": 5, "1 month": 21, "3 months": 63, "6 months": 126, "1 year": 252}[win]
    r = (px.iloc[-1] / px.iloc[-min(n, len(px) - 1)] - 1).sort_values(ascending=False)
    vol = px.pct_change().tail(n).std() * (252 ** 0.5)
    st.dataframe(pd.DataFrame({"Return": r, "Annualised vol": vol}).style.format("{:.1%}"))
    st.line_chart(px.tail(n) / px.tail(n).iloc[0] * 100)
with tab2:
    c1, c2 = st.columns(2)
    fcf = c1.number_input("Free cash flow next year ($m)", value=100.0); g = c1.slider("Growth years 2 to 5", 0.0, 0.3, 0.08)
    wacc = c2.slider("WACC", 0.05, 0.15, 0.09); tg = c2.slider("Terminal growth", 0.0, 0.04, 0.025)
    net_debt = c2.number_input("Net debt ($m)", value=300.0); shares = c2.number_input("Shares (m)", value=100.0)
    flows = [fcf * (1 + g) ** i for i in range(5)]; pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(flows))
    tv = flows[-1] * (1 + tg) / (wacc - tg); pv_tv = tv / (1 + wacc) ** 5; ev = pv + pv_tv
    st.metric("Enterprise value ($m)", f"{ev:,.0f}"); st.metric("Equity value per share ($)", f"{(ev - net_debt) / shares:,.2f}")
    st.caption(f"Terminal value is {pv_tv / ev:.0%} of enterprise value.")
