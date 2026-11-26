"""Daily build: run every tracker, write notes, website pages and all post drafts into out/. Publishes nothing.
Run locally with:  DEMO=1 python build_all.py"""
import os, sys, json, glob, importlib, traceback, html, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.core import OUT, SITE, CFG, TODAY, DEMO, ROOT
from lib import ai, site

def run_trackers():
    results, log = [], []
    for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "trackers", "t*.py"))):
        mod = "trackers." + os.path.basename(f)[:-3]
        try:
            r = importlib.import_module(mod).run()
            log.append((mod, "ok" if r else "skipped (no new data)"))
            if r: results.append(r)
        except Exception as e:
            log.append((mod, f"FAILED: {e}")); traceback.print_exc()
    return results, log

def main():
    for p in glob.glob(os.path.join(OUT, "*")):
        if os.path.isfile(p): os.remove(p)
    results, log = run_trackers()
    if not results: print("Nothing to publish today"); return
    notes = {r.id: ai.write(f"Write a short note for the section '{r.title}'.", r.facts) for r in results}
    lead = ai.write("Write a two-sentence lead summarising today's market log.", [r.headline for r in results if r.headline], 45)
    # keep every tracker on the page: new sections today, plus the latest saved section for trackers with no new data
    secdir = os.path.join(ROOT, "data", "sections"); os.makedirs(secdir, exist_ok=True)
    new = {r.id: site.section(r, notes[r.id]) for r in results}
    for tid, h in new.items(): open(os.path.join(secdir, f"{tid}.html"), "w").write(h)
    order = [os.path.basename(f)[:-3] for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "trackers", "t*.py")))]
    sections = []
    for tid in order:
        if tid in new: sections.append(new[tid])
        elif os.path.exists(os.path.join(secdir, f"{tid}.html")):
            sections.append(open(os.path.join(secdir, f"{tid}.html")).read().replace("</h2>", "</h2><p class='note'>No new data today; latest available shown.</p>", 1))
    site.write_day(sections, lead); site.write_trackers_index(results)
    url = f"{CFG['site']['base_url']}/daily/{TODAY}.html"; disc = CFG["site"]["disclaimer"]
    heads = [r.headline for r in results if r.headline and r.id != "t20_recap_video"]
    core = next((r for r in results if r.id == "t00_core_etf"), results[0])
    drafts = {
        "linkedin": f"{lead}\n\nToday's log:\n" + "\n".join(f"- {h}" for h in heads[:6]) + f"\n\nCharts, data and code: {url}\n\n{disc}\n#ASX #ETFs #markets #python",
        "threads": f"{core.headline}\n{url}\n{disc}"[:490],
        "x": f"{core.headline} {url}"[:270],
        "video_caption": f"{core.headline} Full log: {url}. {disc} #ASX #investing101 #markets",
    }
    nl_md = f"# Markets Lab, {TODAY:%d %B %Y}\n\n{lead}\n\n" + "\n\n".join(f"## {r.title}\n\n{notes[r.id]}\n\n" + "".join(f"![chart]({CFG['site']['base_url']}/img/{TODAY}/{os.path.basename(c)})\n\n" for c in r.charts) for r in results if r.id != "t20_recap_video") + f"\n\n[Full page with tables and sources]({url})\n\n*{disc}*"
    drafts["newsletter_subject"] = f"Markets Lab {TODAY:%d %b}: {core.headline}"[:150]
    drafts["newsletter_md"] = nl_md
    drafts["podcast_script"] = f"Markets Lab for {TODAY:%A %d %B}. This episode is read by a computer voice. {lead} " + " ".join(notes[r.id] for r in results[:6]) + f" {disc}"
    for k, v in drafts.items(): open(os.path.join(OUT, f"{k}.txt"), "w").write(v)
    try:
        from gtts import gTTS
        gTTS(drafts["podcast_script"], lang="en", tld="com.au").save(os.path.join(OUT, "podcast.mp3"))
    except Exception as e: print("podcast audio skipped:", e)
    manifest = {"date": str(TODAY), "demo": DEMO, "url": url, "trackers": log, "charts": [c for r in results for c in r.charts], "video": os.path.exists(os.path.join(OUT, "recap.mp4")), "podcast_audio": os.path.exists(os.path.join(OUT, "podcast.mp3"))}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    # preview page for the approver (shown in the GitHub run summary and uploaded with the drafts)
    pv = "<h2>Approve today's posts</h2><p>Tap <b>Approve and deploy</b> in GitHub to publish everything below, or <b>Reject</b> to publish nothing.</p>"
    pv += "<h3>Tracker status</h3><ul>" + "".join(f"<li>{html.escape(m)}: {html.escape(s)}</li>" for m, s in log) + "</ul>"
    for k in ("linkedin", "threads", "x", "video_caption", "newsletter_subject"): pv += f"<h3>{k}</h3><pre style='white-space:pre-wrap'>{html.escape(drafts[k])}</pre>"
    pv += "<h3>Newsletter</h3><pre style='white-space:pre-wrap'>" + html.escape(nl_md) + "</pre>"
    open(os.path.join(OUT, "preview.html"), "w").write(site.page("Preview", pv))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        open(summary, "a").write(f"## Drafts for {TODAY}\n\n" + "\n".join(f"- {m}: {s}" for m, s in log) + f"\n\n### LinkedIn\n\n{drafts['linkedin']}\n\n### Newsletter subject\n\n{drafts['newsletter_subject']}\n\nFull preview: download the `drafts` artifact and open preview.html.\n")
    print(json.dumps(log, indent=1))

if __name__ == "__main__": main()
