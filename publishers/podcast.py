"""Adds today's episode to site/podcast.xml (RSS). Submit https://<site>/podcast.xml once to Spotify for Creators and Apple Podcasts."""
import os, shutil, html, email.utils, datetime as dt
from lib.core import CFG, SITE, OUT, TODAY
def add_episode(title, summary):
    mp3 = os.path.join(OUT, "podcast.mp3")
    if not os.path.exists(mp3): return "podcast: skipped (no audio)"
    os.makedirs(os.path.join(SITE, "podcast"), exist_ok=True); dst = os.path.join(SITE, "podcast", f"{TODAY}.mp3"); shutil.copy(mp3, dst)
    base = CFG["site"]["base_url"]; feed = os.path.join(SITE, "podcast.xml")
    item = (f"<item><title>{html.escape(title)}</title><description>{html.escape(summary[:900])}</description>"
            f"<enclosure url='{base}/podcast/{TODAY}.mp3' length='{os.path.getsize(dst)}' type='audio/mpeg'/>"
            f"<guid>{base}/podcast/{TODAY}.mp3</guid><pubDate>{email.utils.format_datetime(dt.datetime.now(dt.timezone.utc))}</pubDate></item>")
    old = open(feed).read() if os.path.exists(feed) else ""
    items = old.split("<!--items-->")[1].split("<!--/items-->")[0] if "<!--items-->" in old else ""
    head = (f"<?xml version='1.0' encoding='UTF-8'?><rss version='2.0' xmlns:itunes='http://www.itunes.com/dtds/podcast-1.0.dtd'><channel>"
            f"<title>Markets Lab Daily</title><link>{base}</link><language>en-au</language><description>Daily two-minute log of ASX and Hong Kong markets, read by a computer voice. {html.escape(CFG['site']['disclaimer'])}</description>"
            f"<itunes:author>{html.escape(CFG['site']['author'])}</itunes:author><itunes:owner><itunes:name>{html.escape(CFG['site']['author'])}</itunes:name><itunes:email>lamyeelok16@gmail.com</itunes:email></itunes:owner><itunes:image href='{base}/img/podcast-cover.png'/><itunes:explicit>false</itunes:explicit><itunes:category text='Business'><itunes:category text='Investing'/></itunes:category>")
    open(feed, "w").write(head + "<!--items-->" + item + items + "<!--/items--></channel></rss>")
    return "podcast: episode added"
