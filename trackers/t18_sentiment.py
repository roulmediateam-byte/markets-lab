"""News-sentiment index: scores public headlines with a small finance word list and compares with the ASX 200.
Upgrade path: swap score() for the Hugging Face model trained by hf/train_sentiment.py."""
import os, re, pandas as pd
from lib.core import CFG, Result, feed_items, prices, DATA, TODAY, pct
from lib import charts
TITLE = "ASX news-sentiment index"
POS = "gain gains rally rallies rise rises rose climb climbs record beat beats upgrade upgraded strong growth surge jumps higher profit boost".split()
NEG = "fall falls fell slump slip slips drop drops decline loss losses weak miss misses downgrade downgraded cut cuts lower plunge fears concern concerns".split()
LOG = os.path.join(DATA, "sentiment_log.csv")
def score(t):
    w = re.findall(r"[a-z]+", t.lower()); p = sum(x in POS for x in w); n = sum(x in NEG for x in w)
    return (p - n) / max(p + n, 1)
def run():
    it = feed_items(CFG.get("news_feeds", []), kind="news")
    if not it: return None
    s = sum(score(i["title"]) for i in it) / len(it)
    log = pd.read_csv(LOG) if os.path.exists(LOG) else pd.DataFrame(columns=["date", "sentiment", "headlines"])
    log = log[log["date"] != str(TODAY)]; log.loc[len(log)] = [str(TODAY), s, len(it)]; log.to_csv(LOG, index=False)
    facts = [f"Sentiment score {s:+.2f} on a -1 to +1 scale from {len(it)} headlines.", f"Most positive: {max(it, key=lambda i: score(i['title']))['title']}", f"Most negative: {min(it, key=lambda i: score(i['title']))['title']}"]
    chs = []
    if len(log) >= 5:
        chs.append(charts.lines(log.set_index(pd.to_datetime(log["date"]))[["sentiment"]].rolling(5, min_periods=1).mean(), "News sentiment, 5-day average", "t18"))
    return Result("t18_sentiment", TITLE, facts, chs, None, headline=facts[0])
