"""Shared fetch and keyword classification for ASX announcement trackers 11 to 15.
Uses only feeds listed in config.yaml (announcement_feeds). Posts summarise and link out; never copy announcements."""
import re
from lib.core import CFG, feed_items, Result
from lib import ai
_cache = None
KINDS = {"capital": r"placement|entitlement|share purchase plan|\bSPP\b|capital raising|trading halt pending",
         "mna": r"scheme implementation|takeover|bidder's statement|target's statement|acquisition|merger|non-binding indicative",
         "director": r"appendix 3y|change of director'?s interest",
         "results": r"half year|full year|annual report|results|appendix 4d|appendix 4e"}
def items():
    global _cache
    if _cache is None: _cache = feed_items(CFG.get("announcement_feeds", []), kind="announcements")
    return _cache
def of_kind(k): return [i for i in items() if re.search(KINDS[k], i["title"], re.I)]
def build(tid, title, rows, task):
    if not rows: return None
    facts = [r["title"] for r in rows[:15]]
    note_facts = facts + ["These are headlines only; read each original announcement for details."]
    return Result(tid, title, note_facts, [], None, headline=f"{title}: {len(rows)} today.", links=[(r["title"][:60], r["link"]) for r in rows[:15]])
