import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .core import OUT
NAVY, PINK, GOLD, GREY = "#1F3864", "#C42E74", "#9C7A00", "#888888"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25})

def _save(fig, name):
    p = os.path.join(OUT, "charts", f"{name}.png"); fig.tight_layout(); fig.savefig(p, dpi=150); plt.close(fig); return p

def bars(labels, values, title, name, fmt="{:+.1f}%", scale=100):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    vals = [v * scale for v in values]
    ax.barh(labels, vals, color=[NAVY if v >= 0 else PINK for v in vals])
    for i, v in enumerate(vals): ax.text(v, i, " " + fmt.format(v), va="center", ha="left" if v >= 0 else "right", fontsize=9)
    ax.axvline(0, color=GREY, lw=.8); ax.set_title(title, loc="left", fontweight="bold"); ax.invert_yaxis()
    ax.text(0, -0.12, "Source: markets-lab. General information only, not financial advice.", transform=ax.transAxes, fontsize=7, color=GREY)
    return _save(fig, name)

def lines(df, title, name, ylabel="", rebase=False):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    d = df / df.iloc[0] * 100 if rebase else df
    for i, c in enumerate(d.columns): ax.plot(d.index, d[c], lw=1.6, label=str(c))
    ax.set_title(title, loc="left", fontweight="bold"); ax.set_ylabel(ylabel)
    if len(d.columns) > 1: ax.legend(frameon=False, fontsize=8, ncol=2)
    ax.text(0, -0.15, "Source: markets-lab. General information only, not financial advice.", transform=ax.transAxes, fontsize=7, color=GREY)
    return _save(fig, name)

def curve(x, ys, title, name):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for (lab, y), c in zip(ys.items(), [NAVY, PINK, GOLD]): ax.plot(x, y, marker="o", lw=2, label=lab, color=c)
    ax.set_title(title, loc="left", fontweight="bold"); ax.set_ylabel("Yield (%)"); ax.legend(frameon=False)
    return _save(fig, name)
