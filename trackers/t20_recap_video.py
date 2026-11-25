"""Daily 20-second vertical recap video (MP4, 1080x1920) built from the core ETF data. Voiceover is added in build_all if gTTS is available."""
import os, subprocess, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from lib.core import CFG, Result, OUT, DATA, TODAY
TITLE = "Daily recap video"
def run():
    p = os.path.join(DATA, "core_etf_prices.csv")
    if not os.path.exists(p): return None
    px = pd.read_csv(p, index_col=0, parse_dates=True); names = CFG["core_etfs"]
    d1 = (px.iloc[-1] / px.iloc[-2] - 1).drop(CFG["benchmark"], errors="ignore").sort_values()
    fig, ax = plt.subplots(figsize=(5.4, 9.6), dpi=200); fig.patch.set_facecolor("#0E1A33")
    def frame(k):
        ax.clear(); ax.set_facecolor("#0E1A33"); f = min(1, (k + 1) / 40)
        ax.barh([n.replace(".AX", "") for n in d1.index], d1.values * 100 * f, color=["#3A8AD4" if v >= 0 else "#DE4B8C" for v in d1.values])
        ax.set_xlim(min(d1.min() * 130, -0.5), max(d1.max() * 130, 0.5)); ax.tick_params(colors="white"); [s.set_visible(False) for s in ax.spines.values()]
        ax.set_title(f"ASX ETFs today\n{TODAY:%d %b %Y}", color="white", fontsize=20, fontweight="bold", pad=20)
        ax.text(0.5, -0.08, "General information only, not financial advice", transform=ax.transAxes, ha="center", color="#aaaaaa", fontsize=9)
    out = os.path.join(OUT, "recap.mp4")
    FuncAnimation(fig, frame, frames=200).save(out, writer=FFMpegWriter(fps=10, bitrate=3000)); plt.close(fig)
    return Result("t20_recap_video", TITLE, ["Recap video built (20 seconds, vertical)."], [], None, headline="Today's 20-second ASX ETF recap.")
