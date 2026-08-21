#!/usr/bin/env python3
"""
Semnalul Ignorat / Sub Radar — script generator (the discovery → script bridge).

Takes a story brief (a headline/topic, optionally a few source URLs) and drafts a
`romanian_scripts/<slug>.json` in the exact schema the renderer (make_video.py)
consumes, then runs it through the same `validate_script` editorial gate — so the
output is either publish-ready or flagged with the exact gaps.

Two backends:
  * ollama (default, FREE) — a local model via Ollama. No API key, no web search,
    so drafts come out verified=false with [VERIFICĂ] markers for you to check.
  * Claude API (paid) — opus/sonnet/haiku, with web search to verify figures
    against real sources. Needs ANTHROPIC_API_KEY in .env.

Usage:
    # free local (needs `ollama serve` + `ollama pull qwen2.5:7b`)
    python tools/generate_script.py "România are cea mai scumpă energie din UE"
    python tools/generate_script.py "topic" --model ollama:qwen2.5:14b
    # paid, verified
    python tools/generate_script.py "topic" --model sonnet --source https://ec.europa.eu/...
"""
import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

# Reuse the renderer's .env loader + validation gate so the loop stays closed.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_video import _load_dotenv, validate_script, _report_validation  # noqa: E402

import anthropic  # noqa: E402

DEFAULT_MODEL = "claude-opus-4-8"
# Friendly aliases → current model IDs (cheaper = fewer $ per 1M tokens).
MODEL_ALIASES = {
    "opus":   "claude-opus-4-8",     # most capable  ($5 / $25 per 1M)
    "sonnet": "claude-sonnet-4-6",   # ~2x cheaper   ($3 / $15)
    "haiku":  "claude-haiku-4-5",    # cheapest      ($1 / $5)
}
# Free local backend via Ollama (no API key, no web search → drafts for review).
DEFAULT_OLLAMA_MODEL = "qwen2.5:7b"

# Per-language voice + channel (edge-tts neural voices). ro matches the shipped
# scripts (channel "Sub Radar"); the others enable the planned expansion.
LANGUAGES = {
    "ro": {"voice": "ro-RO-EmilNeural", "channel": "Sub Radar",           "name": "Romanian"},
    "en": {"voice": "en-US-GuyNeural",  "channel": "The Ignored Signal",  "name": "English"},
    "fr": {"voice": "fr-FR-HenriNeural","channel": "Le Signal Ignoré",    "name": "French"},
    "de": {"voice": "de-DE-ConradNeural","channel": "Das Überhörte Signal","name": "German"},
    "it": {"voice": "it-IT-DiegoNeural","channel": "Il Segnale Ignorato", "name": "Italian"},
}

SYSTEM = """You are the researcher-writer for "Sub Radar" / "Semnalul Ignorat", a \
factual, neutral short-form news channel about underreported European stories.

Your job: research the given story with the web_search tool, verify the key \
figures against REAL primary sources, and return ONE script as a JSON object \
that a video renderer will consume.

EDITORIAL RULES (non-negotiable):
- Framing: NOT "the press hid this from you". Instead: "it was reported briefly, \
  then dropped out of the news — here are the sources, judge for yourself."
- Tone: a trusted friend who read the report and explains it. No opinion, no \
  speculation, no sensationalism. Every claim must be sourced.
- Sourcing: find at least 2 INDEPENDENT legitimate sources, at least one a \
  primary/institutional source (EU/Eurostat/national statistics office, a court, \
  a government body, a peer-reviewed study, UN/NATO/Council of Europe, or a named \
  senior official on record). Prefer official documents over news articles.
- Russia/Ukraine/NATO/Belarus/Kremlin/disinformation/election-interference \
  stories need 3+ sources, at least 2 official/institutional, and a 24h hold — \
  set verified=false unless you can meet that bar from search.
- Set "verified": true ONLY if you actually found and cited enough real sources \
  with the correct figures. If you cannot verify a number, set verified=false and \
  keep the marker [VERIFICĂ] next to that number in the narration.

WRITING RULES for the narration (spoken text):
- Language: write in the requested language. Natural, spoken register.
- Length: ~45-60 seconds of speech (roughly 120-150 words).
- Structure it as: hook (a striking verified fact) → what happened → why it \
  matters → a short close inviting the viewer to follow.
- Spell numbers out as WORDS for text-to-speech (e.g. "cincisprezece la sută", \
  not "15%"). Never use symbols like %, €. No markdown, no emojis, no line breaks.

Return ONLY a JSON object (no prose, no markdown fences) with these fields:
{
  "slug": "short_snake_case_slug",
  "headline": "one-line headline in the target language",
  "source_onscreen": "short source label shown on screen, e.g. 'Eurostat, EU-SILC 2023'",
  "hook_card": "TWO SHORT LINES for the opening card, separated by \\n",
  "cta_question": "a short viewer question for the end card",
  "verified": true or false,
  "verification_note": "1-2 sentences: what you verified and against which source(s)",
  "narration": "the full spoken narration, numbers spelled out, one paragraph",
  "sources": [
    "[PRIMARĂ] Institution — document/dataset (year) → domain.tld",
    "[SECUNDARĂ] Outlet/body — what it is → domain.tld"
  ],
  "stat_windows": [
    {"window_idx": 3,
     "values": [{"label": "România", "value": 15.4, "color": "#c0392b"},
                {"label": "Media UE", "value": 3.1, "color": "#1a6bb5"}],
     "metric": "short metric label in target language",
     "source": "short source label"}
  ],
  "video_search_terms": ["8-10 ENGLISH b-roll search phrases for stock footage"]
}
Rules for those fields:
- "stat_windows": include ONE only if the story has a clear 2-3 value numeric \
  comparison with real, verified numbers; otherwise use an empty array [].
- "video_search_terms": English, concrete, stock-footage-friendly. Prefix \
  place-specific ones with the country (e.g. "Romania rural village"); use \
  "European ..." for generic institutional shots.
- Do NOT include voice/channel/country — the tool fills those in.
"""


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return (text[:40] or "story").rstrip("_")


def _next_index(out_dir: Path) -> str:
    nums = [int(m.group(1)) for p in out_dir.glob("*.json")
            if (m := re.match(r"(\d+)_", p.name))]
    return f"{(max(nums) + 1) if nums else 1:02d}"


def _parse_json(text: str) -> dict:
    """Pull the JSON object out of a model's text response (tolerates fences)."""
    if "```" in text:
        text = text.replace("```json", "```").split("```")[1]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"no JSON object in model response:\n{text[:500]}")
    return json.loads(text[start:end + 1])


def resolve_model(spec: str) -> tuple[str, str]:
    """Map a --model value to (backend, model_id). 'ollama' / 'ollama:<name>'
    selects the free local backend; everything else is the paid Claude API."""
    if spec == "ollama":
        return "ollama", DEFAULT_OLLAMA_MODEL
    if spec.startswith("ollama:"):
        return "ollama", spec.split(":", 1)[1]
    return "anthropic", MODEL_ALIASES.get(spec, spec)


def _generate_anthropic(user_prompt: str, model: str) -> dict:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    # Haiku 4.5 lacks adaptive thinking and dynamic-filter web search — degrade
    # gracefully so the cheapest tier still works.
    limited = "haiku" in model
    kwargs = dict(
        model=model,
        max_tokens=8000,
        system=SYSTEM,
        tools=[{"type": "web_search_20250305" if limited else "web_search_20260209",
                "name": "web_search"}],
    )
    if not limited:
        kwargs["thinking"] = {"type": "adaptive"}

    messages = [{"role": "user", "content": user_prompt}]
    resp = None
    for _ in range(6):  # server-side web-search loop may pause_turn
        resp = client.messages.create(messages=messages, **kwargs)
        if resp.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": resp.content})
            continue
        break
    text = "\n".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    return _parse_json(text)


def _generate_ollama(user_prompt: str, model: str) -> dict:
    """Free local backend. Needs `ollama serve` running and the model pulled."""
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": user_prompt}],
        "stream": False,
        "format": "json",              # Ollama structured-output mode → valid JSON
        "options": {"temperature": 0.6, "num_ctx": 8192},
    }).encode()
    req = urllib.request.Request(url + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read().decode())
    except urllib.error.URLError as e:
        raise SystemExit(
            f"Cannot reach Ollama at {url}. Start it and pull the model:\n"
            f"    ollama serve            (usually already running)\n"
            f"    ollama pull {model}\n  ({e})")
    if data.get("error"):
        raise SystemExit(f"Ollama error: {data['error']}  (try: ollama pull {model})")
    return _parse_json(data.get("message", {}).get("content", ""))


def generate(topic: str, lang: str, country: str, category: str,
             sources: list[str], backend: str, model: str) -> dict:
    lang_name = LANGUAGES[lang]["name"]
    brief = [f"Story / topic: {topic}",
             f"Target language: {lang_name} ({lang})",
             f"Country focus: {country or 'Europe'}"]
    if category:
        brief.append(f"Category: {category}")
    if sources:
        brief.append("Starting source leads:")
        brief += [f"- {s}" for s in sources]

    if backend == "ollama":
        # No web search locally — draft honestly and defer verification to a human.
        brief.append("\nYou do NOT have web search. Draft from your own knowledge, "
                     'set "verified": false, and put [VERIFICĂ] right after every '
                     "specific number, percentage, or date so a human can verify it. "
                     "Then return the JSON script.")
        return _generate_ollama("\n".join(brief), model)

    brief.append("\nResearch this now with web_search, then return the JSON script.")
    return _generate_anthropic("\n".join(brief), model)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a validated script JSON from a story brief.")
    ap.add_argument("topic", help="headline or topic to research and script")
    ap.add_argument("--lang", default="ro", choices=sorted(LANGUAGES), help="target language (default ro)")
    ap.add_argument("--country", default="Romania", help="country focus (default Romania)")
    ap.add_argument("--category", default="", help="optional content category (helps Russia-flag detection)")
    ap.add_argument("--source", action="append", default=[], dest="sources",
                    help="optional starting source URL/hint (repeatable)")
    ap.add_argument("--slug", default="", help="output slug (default: auto NN_<topic>)")
    ap.add_argument("--out-dir", default="romanian_scripts", help="output directory")
    ap.add_argument("--channel", default="", help="override channel name")
    ap.add_argument("--model", default="ollama",
                    help="ollama (default, FREE local via Ollama) | ollama:<name> "
                         "| opus | sonnet | haiku (paid Claude API) | any full model id")
    args = ap.parse_args()
    backend, model = resolve_model(args.model)

    _load_dotenv()
    if backend == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        print("ERROR: ANTHROPIC_API_KEY is not set. Add it to .env for the paid "
              "Claude backend, or use --model ollama for the free local one.")
        sys.exit(2)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True)

    tag = "web search" if backend == "anthropic" else "local, no web search — draft for review"
    print(f"Drafting ({model}, {tag}): {args.topic!r} [{args.lang}]...")
    try:
        data = generate(args.topic, args.lang, args.country, args.category,
                        args.sources, backend, model)
    except anthropic.APIError as e:
        print(f"Claude API error: {e}")
        sys.exit(1)

    # Fill tool-owned fields and defaults; never trust the model for these.
    lang_cfg = LANGUAGES[args.lang]
    slug = args.slug or data.get("slug") or f"{_next_index(out_dir)}_{_slugify(args.topic)}"
    slug = _slugify(slug) if not re.match(r"^\d+_", slug) else slug
    data["slug"] = slug
    data["voice"] = lang_cfg["voice"]
    data["channel"] = args.channel or lang_cfg["channel"]
    data["country"] = args.country
    data.setdefault("sources", [])
    data.setdefault("stat_windows", [])
    data.setdefault("video_search_terms",
                    [f"{args.country} city", f"{args.country} people street", "European institution building"])

    out_path = out_dir / f"{slug}.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\n=== {out_path.name} ===")
    print(f"  headline: {data.get('headline','')}")
    ok = _report_validation(out_path.name, validate_script(data))
    print(f"\nWrote {out_path}")
    if ok:
        print("Ready to render:  "
              f".venv-video/bin/python tools/make_video.py {out_path}")
    else:
        print("Fix the errors above (or re-run generation), then render. "
              "The renderer will refuse it as-is.")


if __name__ == "__main__":
    main()
