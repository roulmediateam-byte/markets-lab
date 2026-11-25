"""Turns tracker facts into short written notes. Without AI_API_KEY it falls back to plain templates."""
import os, requests
from .core import CFG
RULES = ("You write short, factual market notes for a public research site run by a finance graduate in Sydney. "
         "Use only the facts given. Never recommend buying or selling anything, never predict prices, no hype, no emoji. "
         "Plain English, short sentences. Australian spelling.")

def write(task, facts, max_words=120):
    key = os.environ.get("AI_API_KEY")
    text_facts = "\n".join(f"- {f}" for f in facts)
    if not key:
        return " ".join(facts[:6])
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", timeout=60,
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": CFG["ai"]["model"], "max_tokens": CFG["ai"]["max_tokens"], "system": RULES,
                  "messages": [{"role": "user", "content": f"{task} Max {max_words} words.\nFacts:\n{text_facts}"}]})
        r.raise_for_status()
        j = r.json()
        text = "".join(b.get("text", "") for b in j.get("content", []) if b.get("type") == "text").strip()
        if not text: raise ValueError(f"no text in response: {str(j)[:300]}")
        return text
    except Exception as e:
        body = getattr(getattr(e, "response", None), "text", "")
        print("AI note failed, using template:", e, body[:300])
        return " ".join(facts[:6])
