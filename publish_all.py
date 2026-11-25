"""Runs ONLY after you tap Approve: posts the drafts in out/ everywhere. Each channel fails independently."""
import os, sys, json, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.core import OUT, CFG, TODAY
from publishers import postiz, newsletter, podcast
def rd(k): return open(os.path.join(OUT, f"{k}.txt")).read()
log = []
def step(name, fn):
    try: log.append(fn())
    except Exception as e: log.append(f"{name}: FAILED {e}"); traceback.print_exc()
m = json.load(open(os.path.join(OUT, "manifest.json")))
step("podcast", lambda: podcast.add_episode(f"Markets Lab {TODAY:%d %b %Y}", rd("podcast_script")))
if os.environ.get("POSTIZ_API_KEY"):
    img = []
    step("upload", lambda: img.append(postiz.upload(m["charts"][0])) or "upload: chart ok")
    step("linkedin", lambda: postiz.post("linkedin", rd("linkedin"), img))
    step("threads", lambda: postiz.post("threads", rd("threads"), img))
    step("x", lambda: postiz.post("x", rd("x"), img))
    if m.get("video"):
        vid = []
        step("video upload", lambda: vid.append(postiz.upload(os.path.join(OUT, "recap.mp4"))) or "upload: video ok")
        for p in ("instagram", "tiktok", "youtube"): step(p, lambda p=p: postiz.post(p, rd("video_caption"), vid))
else: log.append("social: skipped (POSTIZ_API_KEY not set)")
if os.environ.get("NEWSLETTER_API_KEY"): step("newsletter", lambda: newsletter.send(rd("newsletter_subject"), rd("newsletter_md")))
else: log.append("newsletter: skipped (NEWSLETTER_API_KEY not set)")
print("\n".join(log))
s = os.environ.get("GITHUB_STEP_SUMMARY")
if s: open(s, "a").write("## Published\n\n" + "\n".join(f"- {l}" for l in log) + "\n")
