"""Static website: index, one page per day, one latest page per tracker. Images copied into site/img."""
import os, shutil, html, glob, json
from .core import SITE, CFG, TODAY
CSS = """body{font-family:-apple-system,Segoe UI,Arial,sans-serif;max-width:900px;margin:0 auto;padding:24px;color:#1b1b1b;line-height:1.55}
h1{font-size:28px;margin:0}h2{font-size:20px;margin-top:36px;border-bottom:2px solid #1F3864;padding-bottom:4px}
a{color:#1F3864}img{max-width:100%;border:1px solid #eee;margin:8px 0}table{border-collapse:collapse;font-size:13px;margin:8px 0}
td,th{border-bottom:1px solid #ddd;padding:4px 10px;text-align:right}th{background:#1F3864;color:#fff}td:first-child,th:first-child{text-align:left}
.note{color:#666;font-size:12px}.nav a{margin-right:14px}footer{margin-top:48px;color:#666;font-size:12px;border-top:1px solid #ddd;padding-top:12px}"""

def page(title, body):
    s = CFG["site"]
    nav = '<p class="nav"><a href="{b}/index.html">Latest</a><a href="{b}/archive.html">Archive</a><a href="{b}/trackers.html">Trackers</a><a href="{b}/newsletter.html">Newsletter</a><a href="{b}/podcast.xml">Podcast feed</a><a href="{b}/about.html">About</a></p>'.format(b=s["base_url"])
    return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>{html.escape(title)}</title><style>{CSS}</style></head><body><h1>{html.escape(s['title'])}</h1>{nav}{body}<footer>{html.escape(s['disclaimer'])}<br>Built automatically by markets-lab. Notes are AI-assisted and reviewed before publishing.</footer></body></html>"

def img(path):
    os.makedirs(os.path.join(SITE, "img", str(TODAY)), exist_ok=True)
    dst = os.path.join(SITE, "img", str(TODAY), os.path.basename(path)); shutil.copy(path, dst)
    return f"{CFG['site']['base_url']}/img/{TODAY}/{os.path.basename(path)}"

def section(res, note):
    b = f"<h2 id='{res.id}'>{html.escape(res.title)}</h2><p>{html.escape(note)}</p>"
    for c in res.charts: b += f"<img src='{img(c)}' alt='{html.escape(res.title)} chart'>"
    if res.table is not None: b += res.table.to_html(border=0, float_format=lambda x: f"{x:,.2f}")
    if res.links: b += "<p class='note'>Sources: " + ", ".join(f"<a href='{html.escape(u)}'>{html.escape(l)}</a>" for l, u in res.links) + "</p>"
    return b

def write_day(sections_html, lead):
    body = f"<p class='note'>{TODAY:%A %d %B %Y}</p><p><b>{html.escape(lead)}</b></p>" + "".join(sections_html)
    os.makedirs(os.path.join(SITE, "daily"), exist_ok=True)
    open(os.path.join(SITE, "daily", f"{TODAY}.html"), "w").write(page(f"Markets Lab {TODAY}", body))
    open(os.path.join(SITE, "index.html"), "w").write(page("Markets Lab", body))
    days = sorted((os.path.basename(p)[:-5] for p in glob.glob(os.path.join(SITE, "daily", "*.html"))), reverse=True)
    open(os.path.join(SITE, "archive.html"), "w").write(page("Archive", "<h2>Archive</h2><ul>" + "".join(f"<li><a href='{CFG['site']['base_url']}/daily/{d}.html'>{d}</a></li>" for d in days) + "</ul>"))

def write_trackers_index(results):
    os.makedirs(os.path.join(SITE, "trackers"), exist_ok=True)
    rows = "".join(f"<li><a href='{CFG['site']['base_url']}/index.html#{r.id}'>{html.escape(r.title)}</a></li>" for r in results)
    open(os.path.join(SITE, "trackers.html"), "w").write(page("Trackers", f"<h2>Today's trackers ({len(results)})</h2><ul>{rows}</ul><p class='note'>Trackers with no new data on a given day are skipped.</p>"))
    if not os.path.exists(os.path.join(SITE, "about.html")):
        open(os.path.join(SITE, "about.html"), "w").write(page("About", "<h2>About</h2><p>An automated daily research log on Australian and Hong Kong markets, built in Python and GitHub Actions by Adam Lam (UNSW Information Systems). Code: github.com/roulmediateam-byte/markets-lab.</p>"))
