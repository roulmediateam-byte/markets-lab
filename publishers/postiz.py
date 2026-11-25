"""Post to LinkedIn, Threads, X, Instagram, TikTok and YouTube through the Postiz public API.
Docs: https://docs.postiz.com/public-api  (API key: Postiz > Settings > Developers > Public API).
Each platform may need extra 'settings' (e.g. YouTube title, TikTok privacy). Check GET /integration-settings/<id> once and add them in SETTINGS below."""
import os, datetime as dt, requests
from lib.core import CFG
SETTINGS = {   # fill per platform after checking /integration-settings/<id>
    "youtube": {"title": "ASX ETFs today", "type": "public"},
    "tiktok": {"privacy_level": "PUBLIC_TO_EVERYONE", "content_posting_method": "DIRECT_POST"},
}
def _h(): return {"Authorization": os.environ["POSTIZ_API_KEY"]}
def upload(path):
    with open(path, "rb") as f:
        r = requests.post(CFG["postiz"]["base_url"] + "/upload", headers=_h(), files={"file": f}, timeout=300)
    r.raise_for_status(); j = r.json(); return {"id": j["id"], "path": j["path"]}
def post(platform, text, media=None):
    iid = CFG["postiz"]["integrations"].get(platform)
    if not iid: return f"{platform}: skipped (no integration id in config.yaml)"
    item = {"integration": {"id": iid}, "value": [{"content": text, "image": media or []}]}
    if platform in SETTINGS: item["settings"] = SETTINGS[platform]
    body = {"type": "now", "date": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "shortLink": False, "tags": [], "posts": [item]}
    r = requests.post(CFG["postiz"]["base_url"] + "/posts", headers={**_h(), "Content-Type": "application/json"}, json=body, timeout=120)
    return f"{platform}: {r.status_code} {r.text[:200]}"
