#!/usr/bin/env python3
"""
Sub Radar — hot-topic detector.

Scans FREE, no-auth sources (Reddit public JSON, Google Trends daily RSS for
Romania, a few Romanian news RSS feeds) and ranks them against the channel's
proven topic taxonomy (migration/diaspora, pensions, salaries, corruption,
Russia-Ukraine war, + secondary themes). Output: the hottest topics right now
with sample headlines/links and a ready-to-use string for generate_script.py.

No API key needed. Sources that fail (404/timeout/429) are skipped, not fatal.

Usage:
    python tools/hot_topics.py                 # top topics, human-readable
    python tools/hot_topics.py --top 5         # limit to 5 topics
    python tools/hot_topics.py --json          # machine-readable
    python tools/hot_topics.py --headlines 5   # sample headlines per topic
"""
import argparse
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone

UA = {"User-Agent": "SubRadar-HotTopics/1.0 (research; contact via channel)"}

# ── Topic taxonomy (channel winners first). Keywords are lowercase substrings,
#    Romanian + English, matched against titles. Order = display priority. ──────
TOPICS: dict[str, list[str]] = {
    "Migrație & diaspora": [
        "diaspora", "diasporă", "emigr", "migrați", "migrant", "plecat din țară",
        "români din străinătate", "remiten", "brain drain", "depopula", "migration",
    ],
    "Pensii": ["pensi", "pension", "vârsta de pensionare", "punct de pensie"],
    "Salarii & cost de trai": [
        "salari", "salary", "wage", "venit minim", "minim pe economie",
        "coșul zilnic", "scumpiri", "inflați", "cost of living", "putere de cumpărare",
    ],
    "Corupție & justiție": [
        "corupți", "corruption", "dna", "mită", "șpagă", "spaga", "dosar penal",
        "condamnat", "abuz în serviciu", "conflict de interese", "achizi", "fraud",
    ],
    "Război Rusia-Ucraina": [
        "ucrain", "ukrain", "rusia", "russia", "russian", "război", "front",
        "putin", "zelenski", "zelensky", "kremlin", "drone", "dronă", "nato",
        "moscova", "moscow", "kiev", "kyiv",
    ],
    "Energie": ["energ", "gaz", "electricitate", "factură", "curent", "nuclear", "eolian"],
    "Sănătate": ["spital", "sănătate", "medic", "cancer", "boală", "sistem medical", "health"],
    "Fonduri UE & infrastructură": [
        "pnrr", "fonduri europene", "absorbți", "autostrad", "autostradă",
        "infrastructur", "cohesion", "eu funds", "cfr", "cale ferată",
    ],
    "Politică internă & guvern": [
        "guvern", "coaliți", "premier", "moțiune", "buget", "deficit", "alegeri",
        "parlament", "criza politic", "remaniere",
    ],
}


@dataclass
class Item:
    title: str
    url: str
    source: str
    score: int          # engagement (reddit ups+comments) or 1 for RSS
    ts: float           # unix seconds; 0 if unknown


@dataclass
class TopicHeat:
    name: str
    heat: float = 0.0
    items: list[Item] = field(default_factory=list)


def _get(url: str, timeout: int = 12) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:          # best-effort source
        print(f"  · skip {url.split('//')[-1][:40]} (HTTP {e.code})", file=sys.stderr)
        return None
    except Exception as e:                        # noqa: BLE001 — best-effort source
        print(f"  · skip {url.split('//')[-1][:40]} ({type(e).__name__})", file=sys.stderr)
        return None


def _recency_weight(ts: float, now: float) -> float:
    """1.0 for fresh (<6h), decaying to ~0.3 by 48h, 0.15 floor."""
    if ts <= 0:
        return 0.5
    age_h = max(0.0, (now - ts) / 3600.0)
    if age_h < 6:
        return 1.0
    if age_h > 48:
        return 0.15
    return max(0.15, 1.0 - (age_h - 6) / 60.0)


def fetch_reddit(subs: list[str]) -> list[Item]:
    # Reddit's public *.json endpoint now 403s unauthenticated/datacenter
    # requests, but the per-subreddit Atom feed (/top/.rss) still serves. The
    # tradeoff: Atom carries no ups/comments, so items score as topic mentions
    # (score=1) like any RSS source — not the engagement-weighted virality the
    # .json feed gave us. Restore true weighting only via Reddit OAuth.
    ATOM = "{http://www.w3.org/2005/Atom}"
    out: list[Item] = []
    for i, sub in enumerate(subs):
        raw = _get(f"https://www.reddit.com/r/{sub}/top/.rss?t=day")
        if not raw:
            continue
        try:
            root = ET.fromstring(raw)
            for e in root.iter(f"{ATOM}entry"):
                title = (e.findtext(f"{ATOM}title") or "").strip()
                link_el = e.find(f"{ATOM}link")
                link = link_el.get("href", "") if link_el is not None else ""
                ts = 0.0
                stamp = e.findtext(f"{ATOM}updated") or e.findtext(f"{ATOM}published")
                if stamp:
                    try:
                        ts = datetime.fromisoformat(stamp.strip()).timestamp()
                    except ValueError:
                        pass
                if title:
                    out.append(Item(title=title, url=link, source=f"r/{sub}",
                                    score=1, ts=ts))
        except ET.ParseError as e:               # noqa: BLE001
            print(f"  · reddit parse {sub}: {e}", file=sys.stderr)
        if i < len(subs) - 1:
            time.sleep(4)                        # Reddit RSS 429s on tight spacing
    return out


def _parse_rss(raw: bytes, source: str) -> list[Item]:
    out: list[Item] = []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return out
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        ts = 0.0
        pub = it.findtext("pubDate")
        if pub:
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
                try:
                    ts = datetime.strptime(pub.strip(), fmt).timestamp()
                    break
                except ValueError:
                    continue
        if title:
            out.append(Item(title=title, url=link, source=source, score=1, ts=ts))
    return out


def fetch_rss(feeds: dict[str, str]) -> list[Item]:
    out: list[Item] = []
    for name, url in feeds.items():
        raw = _get(url)
        if raw:
            out += _parse_rss(raw, name)
    return out


# Foreign-noise filter: keyword matching pulls in US/global stories (Trump, US
# governors, Dolly Parton…) that aren't about Romania. Drop them from every topic.
# War is REGION-AWARE: US-domestic items are dropped, but anything touching
# Ukraine/Russia/Moldova/NATO stays. Diaspora-source items are never noise.
_FOREIGN_URL = ("/externe/", "/sua/", "/international", "/mapamond")
_FOREIGN_TITLE = (
    "trump", "sua", "american", "washington", "white house", "biden",
    "harris", "pentagon", "iran", "coreea", "canada", "beijing", "china",
    "tennessee", "nashville", "dolly parton", "texas", "florida", "california",
    "new york", "los angeles", "hollywood", "guvernatorul statului", "governor",
)
_RO_TITLE = (
    "români", "romania", "românia", "roman", "bucure", "guvernul român",
    "bolojan", "nicușor", "psd", "pnl", "usr", "aur", "iohannis", "leu", "ron",
    "insse", "ins:", "cfr", "anaf", "dna", "pnrr",
)
_WAR_REGION = (
    "ucrain", "ukrain", "rusia", "russia", "russian", "moldova", "nato",
    "marea neagr", "chișin", "chisin", "kiev", "kyiv", "odesa", "donbas",
    "crimeea", "basarabia", "transnistria", "zaporoj", "putin", "kremlin",
)


# Diaspora feeds only inform the diaspora topic, and only for genuine diaspora-LIFE
# items (drop sports/olympiads that merely mention Italy/Spain).
_DIASPORA_SIGNAL = (
    "diaspora", "emigr", "migran", "migrați", "comunitatea român", "muncitor",
    "plecat", "străinătate", "strainatate", "remiten", "azil", "permis de",
    "reședin", "deporta", "exploatat", "refugiat", "integr", "se întorc",
)


def _compile(words: tuple[str, ...]) -> "re.Pattern[str]":
    """Match each keyword at a LEFT word boundary — prefixes like 'emigr' still
    match 'emigrare', but whole words like 'nato' no longer match 'guverNATOrul'."""
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(w) for w in words) + ")")


_TOPIC_RE = {name: _compile(tuple(kws)) for name, kws in TOPICS.items()}
_FOREIGN_TITLE_RE = _compile(_FOREIGN_TITLE)
_RO_TITLE_RE = _compile(_RO_TITLE)
_WAR_REGION_RE = _compile(_WAR_REGION)
_DIASPORA_SIGNAL_RE = _compile(_DIASPORA_SIGNAL)


def _is_diaspora(it: Item) -> bool:
    return it.source.startswith("GNews-diaspora")


def _foreign_noise(it: Item) -> bool:
    """A clearly foreign (usually US) item with no Romanian angle."""
    u, t = it.url.lower(), it.title.lower()
    looks_foreign = any(f in u for f in _FOREIGN_URL) or _FOREIGN_TITLE_RE.search(t)
    ro_relevant = _RO_TITLE_RE.search(t) or it.source == "r/romania"
    return bool(looks_foreign) and not ro_relevant


def _is_noise(it: Item, topic: str) -> bool:
    if _is_diaspora(it):
        return False
    if not _foreign_noise(it):
        return False
    if topic == "Război Rusia-Ucraina":          # keep only region-relevant war
        return not _WAR_REGION_RE.search(it.title.lower())
    return True


def score_topics(items: list[Item]) -> list[TopicHeat]:
    now = time.time()
    heats = {name: TopicHeat(name) for name in TOPICS}
    for it in items:
        t = it.title.lower()
        rec = _recency_weight(it.ts, now)
        # engagement weight: log-ish so one viral post doesn't dominate
        eng = 1.0 + (it.score ** 0.5) / 10.0
        if _is_diaspora(it):
            # Only genuinely diaspora-life items; drop sports/events noise.
            if _DIASPORA_SIGNAL_RE.search(t):
                heats["Migrație & diaspora"].heat += rec * eng
                heats["Migrație & diaspora"].items.append(it)
            continue
        for name in TOPICS:
            if not _TOPIC_RE[name].search(t):
                continue
            if _is_noise(it, name):
                continue                          # drop US/global noise
            heats[name].heat += rec * eng
            heats[name].items.append(it)
    ranked = [h for h in heats.values() if h.items]
    for h in ranked:
        h.items.sort(key=lambda i: (i.score, i.ts), reverse=True)
    ranked.sort(key=lambda h: h.heat, reverse=True)
    return ranked


def main() -> None:
    ap = argparse.ArgumentParser(description="Detect the hottest topics for Sub Radar.")
    ap.add_argument("--top", type=int, default=8, help="max topics to show")
    ap.add_argument("--headlines", type=int, default=3, help="sample headlines per topic")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    print("Scanning free sources (Reddit + Google Trends + RO news + diaspora)...", file=sys.stderr)
    # Only r/romania: Reddit's no-auth RSS rate-limits this IP to ~1 request per
    # window, so europe/worldnews reliably 429 behind it and just add noise.
    # r/romania is the channel-relevant sub anyway. Re-add the others via OAuth.
    items = fetch_reddit(["romania"])
    items += fetch_rss({
        "GoogleTrends-RO": "https://trends.google.com/trending/rss?geo=RO",
        "Digi24":          "https://www.digi24.ro/rss",
        "G4Media":         "https://www.g4media.ro/feed",
        "HotNews":         "https://hotnews.ro/feed",
        # Diaspora-specific: Google News searches for Romanians abroad (top
        # audience countries) — these are ALWAYS treated as diaspora-relevant.
        "GNews-diaspora-IT": "https://news.google.com/rss/search?q=rom%C3%A2ni+Italia&hl=ro&gl=RO&ceid=RO:ro",
        "GNews-diaspora-DE": "https://news.google.com/rss/search?q=rom%C3%A2ni+Germania&hl=ro&gl=RO&ceid=RO:ro",
        "GNews-diaspora-ES": "https://news.google.com/rss/search?q=rom%C3%A2ni+Spania&hl=ro&gl=RO&ceid=RO:ro",
        "GNews-diaspora":    "https://news.google.com/rss/search?q=diaspora+rom%C3%A2n%C4%83&hl=ro&gl=RO&ceid=RO:ro",
    })
    print(f"  collected {len(items)} items", file=sys.stderr)

    ranked = score_topics(items)[: args.top]

    if args.json:
        print(json.dumps([
            {"topic": h.name, "heat": round(h.heat, 1), "n": len(h.items),
             "headlines": [{"title": i.title, "url": i.url, "source": i.source,
                            "score": i.score} for i in h.items[: args.headlines]]}
            for h in ranked
        ], ensure_ascii=False, indent=2))
        return

    if not ranked:
        print("No topics matched — sources may be down. Try again shortly.")
        return

    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    print(f"\n=== Hottest topics for Sub Radar · {stamp} ===\n")
    for rank, h in enumerate(ranked, 1):
        print(f"{rank}. {h.name}   [heat {h.heat:.1f} · {len(h.items)} mentions]")
        for it in h.items[: args.headlines]:
            eng = f"↑{it.score}" if it.score > 1 else it.source
            print(f"     • {it.title[:88]}  ({eng})")
            if it.url:
                print(f"       {it.url}")
        print()

    top = ranked[0]
    print("→ Suggested next video (hottest, channel-fit):")
    print(f'   python tools/generate_script.py "{top.name}: {top.items[0].title[:70]}"')


if __name__ == "__main__":
    main()
