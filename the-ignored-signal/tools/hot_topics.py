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
    except Exception as e:                       # noqa: BLE001 — best-effort source
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
    out: list[Item] = []
    for sub in subs:
        raw = _get(f"https://www.reddit.com/r/{sub}/top.json?limit=25&t=day")
        if not raw:
            continue
        try:
            data = json.loads(raw)
            for c in data.get("data", {}).get("children", []):
                d = c.get("data", {})
                out.append(Item(
                    title=d.get("title", "").strip(),
                    url="https://reddit.com" + d.get("permalink", ""),
                    source=f"r/{sub}",
                    score=int(d.get("ups", 0)) + int(d.get("num_comments", 0)),
                    ts=float(d.get("created_utc", 0) or 0),
                ))
        except Exception as e:                   # noqa: BLE001
            print(f"  · reddit parse {sub}: {e}", file=sys.stderr)
        time.sleep(0.5)                          # be polite, avoid 429
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


# War is international by nature; every other topic must be about ROMANIA, or the
# keyword match just pulls in US/global noise (Trump budget, US courts, etc.).
_INTERNATIONAL = {"Război Rusia-Ucraina"}
_FOREIGN_URL = ("/externe/", "/sua/", "/international", "/mapamond")
_FOREIGN_TITLE = ("trump", " sua", "sua ", "american", "washington", "iran",
                  "coreea", "canada", "beijing", "china ")
_RO_TITLE = ("români", "romania", "românia", "roman", "bucure", "guvernul român",
             "psd", "pnl", "usr", "aur", "iohannis", "ilie bolojan", "leu", "ron",
             "insse", "ins:", "cfr", "anaf", "dna")


def _foreign_noise(it: Item) -> bool:
    """A clearly foreign-politics item with no Romanian angle."""
    u, t = it.url.lower(), it.title.lower()
    looks_foreign = any(f in u for f in _FOREIGN_URL) or any(f in t for f in _FOREIGN_TITLE)
    ro_relevant = any(r in t for r in _RO_TITLE) or it.source in ("r/romania",)
    return looks_foreign and not ro_relevant


def score_topics(items: list[Item]) -> list[TopicHeat]:
    now = time.time()
    heats = {name: TopicHeat(name) for name in TOPICS}
    for it in items:
        t = it.title.lower()
        rec = _recency_weight(it.ts, now)
        # engagement weight: log-ish so one viral post doesn't dominate
        eng = 1.0 + (it.score ** 0.5) / 10.0
        for name, kws in TOPICS.items():
            if not any(k in t for k in kws):
                continue
            if name not in _INTERNATIONAL and _foreign_noise(it):
                continue                          # drop US/global noise from RO topics
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

    print("Scanning free sources (Reddit + Google Trends + RO news RSS)...", file=sys.stderr)
    items = fetch_reddit(["romania", "europe", "worldnews"])
    items += fetch_rss({
        "GoogleTrends-RO": "https://trends.google.com/trends/trendingsearches/daily/rss?geo=RO",
        "Digi24":          "https://www.digi24.ro/rss",
        "G4Media":         "https://www.g4media.ro/feed",
        "HotNews":         "https://hotnews.ro/feed",
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
