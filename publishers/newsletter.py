"""Send the daily newsletter. Buttondown: https://docs.buttondown.com (API key in Settings > API).
Ghost: Admin API (key 'id:secret'); posts are created with newsletter sending."""
import os, time, requests
from lib.core import CFG
def send(subject, body_md):
    if CFG["newsletter"]["provider"] == "buttondown":
        r = requests.post("https://api.buttondown.com/v1/emails", timeout=60,
            headers={"Authorization": f"Token {os.environ['NEWSLETTER_API_KEY']}", "X-Buttondown-Live-Dangerously": "true"},
            json={"subject": subject, "body": body_md, "status": "about_to_send"})
        return f"buttondown: {r.status_code} {r.text[:200]}"
    import jwt   # pip install pyjwt (only for Ghost)
    kid, secret = os.environ["NEWSLETTER_API_KEY"].split(":"); iat = int(time.time())
    token = jwt.encode({"iat": iat, "exp": iat + 300, "aud": "/admin/"}, bytes.fromhex(secret), algorithm="HS256", headers={"kid": kid})
    base = CFG["newsletter"]["ghost_admin_url"].rstrip("/")
    r = requests.post(f"{base}/ghost/api/admin/posts/?source=html", headers={"Authorization": f"Ghost {token}"}, timeout=60,
        json={"posts": [{"title": subject, "html": "<p>" + body_md.replace("\n\n", "</p><p>") + "</p>", "status": "published"}]})
    return f"ghost: {r.status_code} {r.text[:200]}"
