"""Sydney finance graduate jobs board: new listings from configured feeds, linking to the original ad (never copied)."""
from lib.core import CFG, Result, feed_items, load_state, save_state, DEMO
TITLE = "Sydney finance graduate jobs"
def run():
    it = feed_items(CFG.get("job_feeds", []), kind="jobs"); st = load_state("t19", {"seen": []})
    new = [i for i in it if DEMO or i["link"] not in st["seen"]]
    if not new: return None
    st["seen"] = (st["seen"] + [i["link"] for i in new])[-2000:]; save_state("t19", st)
    return Result("t19_jobs", TITLE, [i["title"] for i in new[:20]], [], None, headline=f"{len(new)} new finance graduate roles listed today.", links=[(i["title"][:70], i["link"]) for i in new[:20]])
