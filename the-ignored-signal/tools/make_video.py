#!/usr/bin/env python3
"""
Semnalul Ignorat — video generator.

Input:  one or more JSON script files (see romanian_scripts/*.json)
Output: vertical 1080x1920 .mp4 — Romanian AI voice + synced bottom-third captions
        on AI-generated Ken Burns backgrounds with xfade scene transitions.
        When given multiple JSON files, outputs one combined video.

Usage:
    python tools/make_video.py romanian_scripts/01_toaleta_apa.json
    python tools/make_video.py romanian_scripts/*.json   # → output/combined.mp4
"""
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import edge_tts
import imageio_ffmpeg


def _load_dotenv(path: str = ".env") -> None:
    """Populate os.environ from a .env file (no external dependency).

    Run from the project root, where the tool already resolves output/ etc.
    Existing environment variables take precedence over the file.
    """
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


_load_dotenv()

# Brand design tokens
FG_ASS     = "&H00DAE5E9"   # #e9e5da — warm white
ACCENT_ASS = "&H002B39C0"   # #c0392b — deep red
MUTED_ASS  = "&H00776063"   # #636077 — muted grey
BLACK_ASS  = "&H00000000"
W, H = 1080, 1920
CAPTION_MAX_WORDS = 5
FONT = "DejaVu Sans"

SRT_TS = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")


# ── Timing helpers ────────────────────────────────────────────────────────────

def srt_ts_to_seconds(ts: str) -> float:
    h, m, s, ms = SRT_TS.match(ts).groups()
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def seconds_to_ass(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


# ── Caption chunking ──────────────────────────────────────────────────────────

BREAK_PUNCT = (",", ";", ":", ".", "!", "?", "—", "…")


def parse_srt_words(srt: str) -> list:
    words = []
    for block in re.split(r"\n\s*\n", srt.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) < 3:
            continue
        m = re.search(r"(\S+)\s*-->\s*(\S+)", lines[1])
        if not m:
            continue
        start = srt_ts_to_seconds(m.group(1))
        end   = srt_ts_to_seconds(m.group(2))
        text  = " ".join(lines[2:]).strip()
        words.append((start, end, text))
    return words


def chunk_captions(cues: list) -> list:
    chunks = []
    for start, end, text in cues:
        toks = text.split()
        if not toks:
            continue
        span = (end - start) / len(toks)
        group: list[str] = []
        for i, tok in enumerate(toks):
            if not group:
                gstart = start + i * span
            group.append(tok)
            end_of_phrase = tok.endswith(BREAK_PUNCT)
            if len(group) >= CAPTION_MAX_WORDS or end_of_phrase or i == len(toks) - 1:
                disp = " ".join(group).rstrip(".,;:!?—…")
                if disp:
                    chunks.append([gstart, start + (i + 1) * span, disp])
                group = []
    for i in range(len(chunks) - 1):
        chunks[i][1] = chunks[i + 1][0]
    return chunks


# ── ASS subtitle builder ──────────────────────────────────────────────────────

def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


HOOK_DUR    = 2.0
END_DUR     = 4.0
# TikTok's Creator Rewards Program only pays on videos longer than 60s, so pad
# the outro (b-roll keeps rolling under a held CTA) up to this floor.
MIN_DURATION = 62.0
SAFE_TOP    = 170
# Bottom-anchored MarginV (px up from bottom edge, PlayResY=1920).
# Captions sit in the bottom third (~77% down) but clear of the bottom ~15%
# platform UI safe zone; source sits just below the captions.
CAP_MARGIN  = 430
SAFE_BOTTOM = 340


def build_ass(chunks: list, duration: float, channel: str,
              source_text: str, show_source: bool,
              hook_card: str, cta_question: str,
              narration_dur: float | None = None) -> str:
    # duration = full video length (may exceed narration when padded for TikTok);
    # narration_dur = when the voice ends, so the CTA card holds through the outro.
    DARK_BOX = "&H440F0909"

    styles = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 1
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{FONT},48,{FG_ASS},{FG_ASS},{BLACK_ASS},&H00000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,{CAP_MARGIN},1
Style: Header,{FONT},38,{MUTED_ASS},{MUTED_ASS},{BLACK_ASS},&H00000000,0,0,0,0,100,100,3,0,1,2,0,8,60,60,{SAFE_TOP},1
Style: Source,{FONT},34,{ACCENT_ASS},{ACCENT_ASS},{BLACK_ASS},&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,60,60,{SAFE_BOTTOM},1
Style: HookCard,{FONT},82,{FG_ASS},{FG_ASS},{BLACK_ASS},{DARK_BOX},-1,0,0,0,100,100,2,0,3,0,0,5,80,80,0,1
Style: EndCard,{FONT},68,{ACCENT_ASS},{ACCENT_ASS},{BLACK_ASS},{DARK_BOX},-1,0,0,0,100,100,2,0,3,0,0,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    narr_end     = narration_dur if narration_dur is not None else duration
    end_ts       = seconds_to_ass(duration)
    hook_end_ts  = seconds_to_ass(HOOK_DUR)
    # CTA appears when narration ends (or the last END_DUR if not padded) and
    # holds to the end, so the padded outro shows the call to action, not silence.
    end_start_ts = seconds_to_ass(max(0.0, min(narr_end, duration - END_DUR)))

    events = []

    if hook_card:
        hook_text = ass_escape(hook_card.upper()).replace("\n", "\\N")
        events.append(
            f"Dialogue: 1,0:00:00.00,{hook_end_ts},HookCard,,0,0,0,,{hook_text}"
        )

    events.append(
        f"Dialogue: 0,0:00:00.00,{end_ts},Header,,0,0,0,,{ass_escape(channel.upper())}"
    )
    if show_source and source_text:
        events.append(
            f"Dialogue: 0,0:00:00.00,{end_ts},Source,,0,0,0,,{ass_escape(source_text)}"
        )

    for start, end, text in chunks:
        display_start = max(start, HOOK_DUR) if hook_card else start
        if display_start >= end:
            continue
        events.append(
            f"Dialogue: 0,{seconds_to_ass(display_start)},{seconds_to_ass(end)},"
            f"Caption,,0,0,0,,{ass_escape(text.upper())}"
        )

    end_text = ass_escape(channel.upper())
    if cta_question:
        end_text += r"\N" + ass_escape(cta_question)
    events.append(
        f"Dialogue: 1,{end_start_ts},{end_ts},EndCard,,0,0,0,,{end_text}"
    )

    return styles + "\n".join(events) + "\n"


# ── Voice synthesis ───────────────────────────────────────────────────────────

async def synth(text: str, voice: str, mp3_path: Path) -> str:
    communicate = edge_tts.Communicate(text, voice)
    submaker    = edge_tts.SubMaker()
    with open(mp3_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
    return submaker.get_srt()


# ── Duration helper ───────────────────────────────────────────────────────────

def media_duration(ffmpeg_bin: str, path: Path) -> float:
    out = subprocess.run(
        [ffmpeg_bin, "-i", str(path)], capture_output=True, text=True
    ).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        return 0.0
    h, mn, s = m.groups()
    return int(h) * 3600 + int(mn) * 60 + float(s)


# ── Local search term extraction ──────────────────────────────────────────────

_RO_STOPWORDS = {
    "și","în","din","de","la","cu","pe","că","să","nu","este","sunt","au",
    "o","un","ale","al","a","ai","pentru","prin","mai","dar","sau","dacă",
    "când","care","ce","cum","tot","toți","toate","această","acest","lor",
    "lui","ei","el","ea","noi","voi","eu","tu","se","le","li","îi","îl",
    "am","ești","fi","fost","face","despre","după","între","spre","până",
    "fără","toată","mult","puțin","mare","mic","doar","chiar","încă",
    "deja","acum","atunci","apoi","înainte","mereu","poate","trebuie",
    "vrea","ști","zice","spune","ani","an","tot","iar","nici","ci","fie",
    "din","este","suntem","avem","este","eram","unor","unui","unei",
    "practic","conform","conform","această","aceasta","acesta","aceste",
    "mult","puțin","toată","întreg","doar","chiar","exact","același","aceeași",
}

_RO_VISUAL: dict[str, tuple[str, bool]] = {
    "apă":        ("water faucet tap running", False),
    "toaletă":    ("toilet bathroom indoor", False),
    "robinet":    ("faucet tap water running", False),
    "apei":       ("water running sink", False),
    "casă":       ("village rural house", True),
    "casa":       ("village rural house", True),
    "locuință":   ("old house rural interior", True),
    "locuința":   ("old house rural interior", True),
    "locuinței":  ("rural home interior", True),
    "sat":        ("village rural countryside", True),
    "sate":       ("village rural house", True),
    "gospodării": ("rural household family", True),
    "gospodărilor": ("rural household family", True),
    "rural":      ("rural countryside village", True),
    "copii":      ("children kids village", True),
    "bătrâni":    ("elderly old people village", True),
    "oameni":     ("people street village", True),
    "familie":    ("family rural home", True),
    "pensionari": ("elderly retired people", True),
    "familii":    ("family rural home", True),
    "sărăcie":    ("poverty poor village", True),
    "infecții":   ("doctor patient medical", False),
    "boli":       ("sick patient hospital", False),
    "căldură":    ("heating radiator home winter", False),
    "iarnă":      ("winter snow village", True),
    "iarna":      ("winter snow house cold", True),
    "frigul":     ("winter cold snow house", True),
    "facturi":    ("energy bills expenses stress", False),
    "mâncare":    ("family cooking food kitchen", False),
    "pădure":     ("forest trees nature", True),
    "păduri":     ("forest trees mountain", True),
    "pădurile":   ("forest trees logging", True),
    "copaci":     ("forest trees", True),
    "tăieri":     ("logging deforestation forest", True),
    "tăierile":   ("logging deforestation forest", True),
    "tăiate":     ("deforestation logging cut", True),
    "virgin":     ("old growth forest pristine", True),
    "virgine":    ("old growth forest pristine", True),
    "natură":     ("nature landscape scenic", True),
    "câmp":       ("field countryside green", True),
    "munte":      ("mountain landscape", True),
    "munți":      ("mountain Carpathian landscape", True),
    "curtea":     ("court justice building", False),
    "comisia":    ("parliament government building", False),
    "amenzile":   ("government official building", False),
    "amenzi":     ("court law building", False),
    "oraș":       ("city urban street", True),
    "stradă":     ("street people urban", True),
    "canalizare": ("water pipe infrastructure", False),
}

def _term_for_window(window_text: str, country: str, seen: set[str]) -> str | None:
    from collections import Counter
    words = re.findall(r"[a-zăâîșț]+", window_text.lower())
    freq  = Counter(w for w in words if w not in _RO_STOPWORDS and len(w) > 3)
    for word, _ in freq.most_common(20):
        entry = _RO_VISUAL.get(word)
        if not entry:
            continue
        concept, needs_country = entry
        query = f"{country} {concept}" if needs_country and country else f"European {concept}"
        if query not in seen:
            return query
    return None


def extract_timed_terms(chunks: list, country: str, n_clips: int) -> list[str]:
    if not chunks:
        return []
    total_dur = chunks[-1][1]
    window    = total_dur / n_clips
    seen:    set[str]  = set()
    queries: list[str] = []
    generic_pool = [
        f"{country} village rural", f"{country} countryside landscape",
        f"{country} people street", f"{country} old house",
        f"{country} city urban",    f"{country} nature forest",
        f"{country} rural life",    f"{country} landscape",
    ] if country else ["countryside village", "nature landscape", "people street"]
    for i in range(n_clips):
        w_start = i * window
        w_end   = (i + 1) * window
        window_text = " ".join(
            text for start, end, text in chunks if w_start <= start < w_end
        )
        q = _term_for_window(window_text, country, seen)
        if not q:
            for g in generic_pool:
                if g not in seen:
                    q = g
                    break
        if q:
            seen.add(q)
            queries.append(q)
    return queries


# ── Image sourcing: real photos (Pexels + Wikimedia) → AI fallback ────────────

FPS      = 25
KB_SCALE = 1.40

# Real-photo sources. Pexels needs a free key (PEXELS_API_KEY in .env) and its
# license requires no attribution. Wikimedia is keyless, but its CC-BY images
# need a credit line (written to <slug>_credits.txt). AI is the never-fail
# fallback so a render never breaks for lack of an image.
PEXELS_KEY    = os.environ.get("PEXELS_API_KEY", "").strip()
USE_WIKIMEDIA = True

# Per-run registry of image content hashes already used, so no scene photo
# repeats within a video or across videos rendered in the same invocation.
_USED_IMG_HASHES: set[str] = set()


def _img_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _is_fresh(path: Path) -> bool:
    """True if the file exists, is non-trivial, and not already used this run."""
    return (path.exists() and path.stat().st_size > 10_000
            and _img_hash(path) not in _USED_IMG_HASHES)


_ANGLES_A = [
    "wide establishing shot, golden hour",
    "medium shot, overcast dramatic sky",
    "wide angle, muted tones",
    "establishing shot, dusk light",
]


def _image_prompt(visual_term: str, idx: int = 0) -> str:
    angle = _ANGLES_A[idx % 4]
    return (
        f"{visual_term}, {angle}, "
        "cinematic documentary photography, dramatic natural lighting, "
        "moody atmosphere, photorealistic, ultra detailed, "
        "no text, no watermark, no logo"
    )


def _fetch_pollinations(prompt: str, dest: Path, seed: int) -> bool:
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={W}&height={H}&nologo=true&seed={seed}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "TheIgnoredSignal/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            return dest.stat().st_size > 10_000
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 15 * (attempt + 1)
                print(f"    rate-limited — retrying in {wait}s...")
                import time; time.sleep(wait)
            else:
                print(f"    error: {e}")
                break
        except Exception as e:
            print(f"    error: {e}")
            break
    dest.unlink(missing_ok=True)
    return False


# Wikimedia's policy requires a descriptive UA with contact info, else 429s.
WIKI_UA = "TheIgnoredSignal/1.0 (news-video-tool; contact ilie_vali@yahoo.com)"


def _download(url: str, dest: Path, timeout: int = 90,
              ua: str = "TheIgnoredSignal/1.0") -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as f:
            f.write(resp.read())
        return dest.stat().st_size > 10_000
    except Exception as e:
        print(f"    download error: {e}")
        dest.unlink(missing_ok=True)
        return False


def _fetch_pexels(term: str, dest: Path) -> bool:
    """Real, commercially-licensed photo from Pexels (no attribution required).

    Walks the result list and accepts the first photo not already used this
    run, so distinct scenes never share an image.
    """
    if not PEXELS_KEY:
        return False
    url = ("https://api.pexels.com/v1/search?"
           f"query={urllib.parse.quote(term)}&orientation=portrait"
           "&size=large&per_page=15")
    req = urllib.request.Request(
        url, headers={"Authorization": PEXELS_KEY,
                      "User-Agent": "TheIgnoredSignal/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            photos = json.loads(resp.read().decode()).get("photos", [])
    except Exception as e:
        print(f"    pexels error: {e}")
        return False
    for photo in photos:
        src = photo["src"]
        if not _download(src.get("original") or src.get("large2x"), dest):
            continue
        if _img_hash(dest) in _USED_IMG_HASHES:
            continue          # duplicate of an image already used — try next
        return True
    return False


def _fetch_pexels_video(term: str, dest: Path) -> bool:
    """Real motion b-roll from Pexels Videos (no attribution required).

    Picks a portrait mp4 near 1080x1920 (kept light), skipping any clip already
    used this run. Returns False when nothing suitable is found so the caller
    falls back to a still image.
    """
    if not PEXELS_KEY:
        return False
    url = ("https://api.pexels.com/videos/search?"
           f"query={urllib.parse.quote(term)}&orientation=portrait"
           "&size=medium&per_page=10")
    req = urllib.request.Request(
        url, headers={"Authorization": PEXELS_KEY,
                      "User-Agent": "TheIgnoredSignal/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            videos = json.loads(resp.read().decode()).get("videos", [])
    except Exception as e:
        print(f"    pexels video error: {e}")
        return False
    for v in videos:
        files = [f for f in v.get("video_files", [])
                 if f.get("file_type") == "video/mp4" and f.get("height")]
        if not files:
            continue
        portrait = [f for f in files if f["height"] >= f.get("width", 0)] or files
        # Prefer the file closest to 1080x1920 among >=1280 tall; else the tallest.
        tall   = [f for f in portrait if f["height"] >= 1280]
        choice = (min(tall, key=lambda f: abs(f["height"] - H)) if tall
                  else max(portrait, key=lambda f: f["height"]))
        if not _download(choice["link"], dest, timeout=180):
            continue
        if _img_hash(dest) in _USED_IMG_HASHES:
            continue          # duplicate clip already used — try next
        return True
    return False


_WIKI_OK = ("cc ", "cc0", "public domain", "no restrictions")


def _clean_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def _fetch_wikimedia(term: str, dest: Path) -> tuple[bool, str]:
    """Authentic Commons photo. Returns (ok, attribution) — CC-BY needs credit."""
    url = ("https://commons.wikimedia.org/w/api.php?action=query"
           "&generator=search&gsrnamespace=6&gsrlimit=10"
           f"&gsrsearch={urllib.parse.quote(term)}"
           "&prop=imageinfo&iiprop=url|extmetadata|mime|size"
           f"&iiurlwidth={W}&format=json")
    req = urllib.request.Request(url, headers={"User-Agent": WIKI_UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            pages = json.loads(resp.read().decode()).get("query", {}).get("pages", {})
    except Exception as e:
        print(f"    wikimedia error: {e}")
        return False, ""
    import time
    # Preserve Commons' search-relevance ranking (index), not file size.
    for p in sorted(pages.values(), key=lambda p: p.get("index", 1e9)):
        ii = p.get("imageinfo", [{}])[0]
        if ii.get("mime") != "image/jpeg" or ii.get("width", 0) < W:
            continue
        em  = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", "")
        if not any(tok in lic.lower() for tok in _WIKI_OK):
            continue
        thumb = ii.get("thumburl")
        time.sleep(0.4)   # be gentle with the upload CDN
        if not thumb or not _download(thumb, dest, ua=WIKI_UA):
            continue
        if _img_hash(dest) in _USED_IMG_HASHES:
            continue          # duplicate of an image already used — try next
        author = _clean_html(em.get("Artist", {}).get("value", "")) or "Wikimedia Commons"
        title  = p.get("title", "").replace("File:", "")
        return True, f'"{title}" by {author} — {lic} (Wikimedia Commons)'
    return False, ""


def get_scene_media(search_terms: list[str], out_dir: Path, slug: str,
                    country: str = "") -> list[tuple[str, Path]]:
    """One scene per visual term, returned as (kind, path) with kind in
    {"video", "image"}.

    Priority per slot: cached clip → Pexels video → cached photo → Pexels photo
    → Wikimedia (country-specific) → cached AI → Pollinations. Real motion wins,
    then real stills, with AI as the never-fail fallback. No media repeats within
    or across a run. Wikimedia attributions go to <slug>_credits.txt.
    """
    media:   list[tuple[str, Path]] = []
    credits: list[str]              = []

    def use(kind: str, path: Path) -> None:
        """Record the media as used (dedup) and add it to the scene list."""
        _USED_IMG_HASHES.add(_img_hash(path))
        media.append((kind, path))

    for i, term in enumerate(search_terms):
        clip   = out_dir / f"clip_{slug}_{i}.mp4"    # video b-roll cache
        photo  = out_dir / f"photo_{slug}_{i}.jpg"   # real-photo cache
        dest_a = out_dir / f"img_{slug}_{i}a.jpg"    # legacy AI pair cache
        dest   = out_dir / f"img_{slug}_{i}.jpg"     # AI cache

        print(f"  [{i+1}/{len(search_terms)}] {term!r}")

        # 0 — cached video clip
        if _is_fresh(clip):
            use("video", clip); print(f"    clip cached: {clip.name}"); continue
        # 1 — Pexels video (real motion b-roll)
        if _fetch_pexels_video(term, clip):
            use("video", clip)
            print(f"    Pexels video ✓ ({clip.stat().st_size // 1024} KB)"); continue

        # 2 — cached real photo
        if _is_fresh(photo):
            use("image", photo); print(f"    photo cached: {photo.name}"); continue
        # 3 — Pexels photo
        if _fetch_pexels(term, photo):
            use("image", photo)
            print(f"    Pexels photo ✓ ({photo.stat().st_size // 1024} KB)"); continue
        # 4 — Wikimedia for authentic country-specific slots (needs credit)
        if USE_WIKIMEDIA and country and term.lower().startswith(country.lower()):
            ok, attribution = _fetch_wikimedia(term, photo)
            if ok:
                use("image", photo); credits.append(attribution)
                print(f"    Wikimedia ✓ — {attribution}"); continue

        # 5 — reuse an existing AI image if present (unless it's a dup)
        if _is_fresh(dest_a):
            use("image", dest_a); print(f"    AI cached: {dest_a.name}"); continue
        if _is_fresh(dest):
            use("image", dest); print(f"    AI cached: {dest.name}"); continue

        # 6 — generate with Pollinations (never-fail fallback)
        print(f"    generating (AI fallback)...")
        if _fetch_pollinations(_image_prompt(term, i), dest, i * 137 + 42):
            use("image", dest); print(f"    AI ✓ ({dest.stat().st_size // 1024} KB)")
        else:
            print(f"    failed — skipped")

    if credits:
        cf = out_dir / f"{slug}_credits.txt"
        cf.write_text(
            "Image credits (Wikimedia Commons — include in video description):\n"
            + "\n".join(f"- {c}" for c in credits) + "\n",
            encoding="utf-8",
        )
        print(f"  Wrote {len(credits)} image credit(s) → {cf.name}")
    return media


# ── Stat animation (matplotlib) ───────────────────────────────────────────────

def make_stat_clip(stat: dict, clip_dur: float, out_path: Path, ffmpeg_bin: str) -> bool:
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["animation.ffmpeg_path"] = ffmpeg_bin
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    BG    = "#09090f"
    CARD  = "#0e0e18"
    FG    = "#e9e5da"
    MUTED = "#636077"

    values  = stat["values"]
    metric  = stat.get("metric", "")
    source  = stat.get("source", "")
    n_bars  = len(values)
    max_val = max(v["value"] for v in values) * 1.25

    total_frames  = int(clip_dur * FPS)
    anim_frames   = int(total_frames * 0.55)

    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100, facecolor=BG)
    ax  = fig.add_axes([0.12, 0.28, 0.76, 0.42], facecolor=CARD)

    ax.set_xlim(-0.5, n_bars - 0.5)
    ax.set_ylim(0, max_val)
    ax.set_facecolor(CARD)
    ax.tick_params(colors=MUTED, labelsize=22)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_xticks(range(n_bars))
    ax.set_xticklabels([v["label"] for v in values], color=FG, fontsize=26, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_edgecolor("#1b1b2a")
    ax.yaxis.label.set_color(MUTED)
    ax.tick_params(axis="y", colors=MUTED)
    ax.grid(axis="y", color="#1b1b2a", linewidth=0.8)

    bars = ax.bar(
        range(n_bars), [0] * n_bars,
        color=[v["color"] for v in values],
        width=0.55, zorder=3,
    )
    val_texts = [
        ax.text(i, 0, "", ha="center", va="bottom", color=FG,
                fontsize=30, fontweight="bold")
        for i in range(n_bars)
    ]

    fig.text(0.5, 0.76, metric, ha="center", va="center",
             color=FG, fontsize=28, fontweight="bold", wrap=True)
    fig.text(0.5, 0.18, source, ha="center", va="center",
             color=MUTED, fontsize=20)

    def update(frame: int):
        t = min(frame / anim_frames, 1.0) if anim_frames > 0 else 1.0
        ease = 1 - (1 - t) ** 3
        for j, (bar, entry) in enumerate(zip(bars, values)):
            h = entry["value"] * ease
            bar.set_height(h)
            val_texts[j].set_position((j, h + max_val * 0.01))
            val_texts[j].set_text(f"{h:.1f}%" if h > 0.5 else "")
        return bars

    ani = animation.FuncAnimation(
        fig, update, frames=total_frames, interval=1000 / FPS, blit=True
    )

    tmp_mp4 = out_path.with_suffix(".tmp.mp4")
    writer  = animation.FFMpegWriter(fps=FPS, codec="libx264",
                                     extra_args=["-pix_fmt", "yuv420p", "-preset", "medium"])
    ani.save(str(tmp_mp4), writer=writer, dpi=100)
    plt.close(fig)
    tmp_mp4.rename(out_path)
    return out_path.exists()


# ── Ken Burns + xfade filter graph ───────────────────────────────────────────

_KB_IN  = "min(zoom+{r:.6f},1.3)"
_KB_OUT = "if(eq(on,1),1.3,max(zoom-{r:.6f},1.0))"
_KB_CTR = ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
_KB_TOP = ("iw/2-(iw/zoom/2)", "if(gte(ih*0.12,ih-ih/zoom),ih-ih/zoom,ih*0.12)")
_KB_BOT = ("iw/2-(iw/zoom/2)", "if(gte(ih*0.45,ih-ih/zoom),ih-ih/zoom,ih*0.45)")

# Alternating Ken Burns styles: one per visual window
_KB_STYLES = [
    (_KB_IN,  _KB_CTR),
    (_KB_IN,  _KB_TOP),
    (_KB_OUT, _KB_CTR),
    (_KB_OUT, _KB_BOT),
]

XFADE_DUR = 0.5   # seconds of crossfade between adjacent scenes


def _kb(stream_idx: int, out_label: str, clip_dur: float,
        z_expr: str, xy: tuple[str, str]) -> str:
    """Ken Burns on one looped image → strict CFR output for xfade.
    Runs XFADE_DUR longer than clip_dur so the xfade chain never starves."""
    n_frames = max(FPS, int((clip_dur + XFADE_DUR) * FPS))
    rate     = 0.30 / n_frames
    big_w    = int(W * KB_SCALE)
    big_h    = int(H * KB_SCALE)
    x_expr, y_expr = xy
    return (
        f"[{stream_idx}:v]"
        f"scale={big_w}:{big_h}:force_original_aspect_ratio=increase,crop={big_w}:{big_h},"
        f"zoompan=z='{z_expr.format(r=rate)}':x='{x_expr}':y='{y_expr}'"
        f":d={n_frames}:s={W}x{H}:fps={FPS},"
        f"setpts=PTS-STARTPTS,"
        f"eq=brightness=-0.05:saturation=0.9,"
        # fps must be the LAST rate-setting filter: setpts/eq reset frame_rate
        # to 1/0 (undefined), which xfade rejects with "constant frame rate" error.
        f"fps={FPS},format=yuv420p[{out_label}]"
    )


def _video_scene(stream_idx: int, out_label: str, clip_dur: float) -> str:
    """Real video b-roll → fill 1080x1920, graded to match stills, CFR for xfade.
    tpad clones the last frame so short clips still reach clip_dur."""
    return (
        f"[{stream_idx}:v]"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        # Normalize odd/slow-mo source rates (some Pexels clips are 60-98 fps)
        # to CFR before timing ops. NOTE: no setpts before tpad — a preceding
        # setpts silently disables tpad's clone padding, collapsing the chain.
        f"fps={FPS},"
        f"tpad=stop_mode=clone:stop_duration=3,"
        # +XFADE_DUR surplus so the xfade chain never starves on rounding
        f"trim=end={clip_dur + XFADE_DUR:.3f},setpts=PTS-STARTPTS,"
        f"eq=brightness=-0.05:saturation=0.9,"
        f"fps={FPS},format=yuv420p[{out_label}]"
    )


def _stat_scene(stream_idx: int, out_label: str, clip_dur: float) -> str:
    """Matplotlib stat clip → letterboxed onto the brand background, CFR."""
    return (
        f"[{stream_idx}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=#09090f,"
        # no setpts before tpad — it silently disables the clone padding
        f"tpad=stop_mode=clone:stop_duration=3,"
        # +XFADE_DUR surplus so the xfade chain never starves on rounding
        f"trim=end={clip_dur + XFADE_DUR:.3f},setpts=PTS-STARTPTS,"
        # fps last, after trim/setpts, so xfade sees a defined frame_rate
        f"fps={FPS},format=yuv420p[{out_label}]"
    )


def build_filter_complex(
    ass_arg: str,
    scenes: list[tuple[str, int]],   # ordered (kind, ffmpeg stream index) per window
    narration_dur: float,
) -> tuple[str, float]:
    """One scene per window — video b-roll, image Ken Burns, or stat clip —
    joined by an xfade chain. clip_dur is solved so the crossfaded total ≈
    narration_dur (offset_i = i * (clip_dur - XFADE_DUR))."""
    n = len(scenes)
    if n == 0:
        raise ValueError("no visual content")

    # solve: n*clip_dur - (n-1)*XFADE_DUR = narration_dur
    clip_dur = (narration_dur + (n - 1) * XFADE_DUR) / n

    parts:  list[str] = []
    labels: list[str] = []
    kb_i = 0                       # Ken Burns style rotates across image scenes
    for wi, (kind, sidx) in enumerate(scenes):
        lbl = f"s{wi}"
        if kind == "video":
            parts.append(_video_scene(sidx, lbl, clip_dur))
        elif kind == "stat":
            parts.append(_stat_scene(sidx, lbl, clip_dur))
        else:  # image
            z_expr, xy = _KB_STYLES[kb_i % len(_KB_STYLES)]
            kb_i += 1
            parts.append(_kb(sidx, lbl, clip_dur, z_expr, xy))
        labels.append(lbl)

    if n == 1:
        final = labels[0]
    else:
        current = labels[0]
        for i in range(1, n):
            offset = i * (clip_dur - XFADE_DUR)
            nxt    = f"xf{i}"
            parts.append(
                f"[{current}][{labels[i]}]xfade=transition=fade"
                f":duration={XFADE_DUR:.3f}:offset={offset:.3f}[{nxt}]"
            )
            current = nxt
        final = current

    parts.append(f"[{final}]subtitles='{ass_arg}'[v]")
    return ";".join(parts), clip_dur


def filter_gradient(ass_arg: str) -> str:
    return "[0:v]format=yuv420p[bg];[bg]subtitles='" + ass_arg + "'[v]"


# ── Upload package (title / description / hashtags / thumbnail) ───────────────

AI_DISCLOSURE_RO = ("Narațiune cu voce generată de AI. Imaginile și clipurile "
                    "sunt ilustrative (surse: Pexels, Wikimedia Commons).")
AI_DISCLOSURE_EN = ("AI-generated voice-over. Footage is illustrative "
                    "(Pexels, Wikimedia Commons).")


def _hashtags(data: dict, platform: str) -> list[str]:
    channel = data.get("channel", "Sub Radar")
    tags = ["#" + re.sub(r"\s+", "", channel)]
    if data.get("country"):
        tags.append("#" + data["country"])
    tags += ["#" + t.lstrip("#") for t in data.get("hashtags", [])]
    tags += (["#Shorts", "#stiri", "#news"] if platform == "youtube"
             else ["#fyp", "#foryou", "#stiri"])
    seen, out = set(), []
    for t in tags:
        if len(t) > 1 and t.lower() not in seen:
            seen.add(t.lower()); out.append(t)
    return out[:15]


def _read_credits(out_dir: Path, slug: str) -> list[str]:
    cf = out_dir / f"{slug}_credits.txt"
    if not cf.exists():
        return []
    return [ln[2:].strip() for ln in cf.read_text(encoding="utf-8").splitlines()
            if ln.startswith("- ")]


def make_thumbnail(mp4_path: Path, out_path: Path, ffmpeg: str) -> bool:
    """Grab the styled hook-card frame (~1.2s) as a ready-branded thumbnail."""
    r = subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-ss", "1.2", "-i", str(mp4_path),
         "-frames:v", "1", "-q:v", "3", str(out_path)],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and out_path.exists()


def write_upload_package(data: dict, out_dir: Path, slug: str,
                         total: float, ffmpeg: str, mp4_path: Path) -> Path:
    """Emit a per-video upload sheet (title, description, hashtags, disclosure)
    for YouTube Shorts + TikTok, plus a branded thumbnail."""
    headline  = data.get("headline", slug)
    channel   = data.get("channel", "Sub Radar")
    hook      = data.get("hook_card", "").replace("\n", " ").strip() or headline
    source_os = data.get("source_onscreen", "")
    ver_note  = data.get("verification_note", "")
    sources   = data.get("sources", [])

    yt_tags = _hashtags(data, "youtube")
    tt_tags = _hashtags(data, "tiktok")

    src_lines = ([f"- {source_os}"] if source_os else []) + [f"- {s}" for s in sources]
    if not src_lines:
        src_lines = ["- (adaugă sursele aici)"]
    cred_lines = ["- Video & foto: Pexels (Pexels License — fără atribuire necesară)"]
    cred_lines += [f"- {c}" for c in _read_credits(out_dir, slug)]

    yt_title = headline if len(headline) <= 90 else headline[:87] + "..."
    ver_line = f"✅ {ver_note}" if ver_note else ""
    nl = "\n"

    md = f"""# Upload package — {slug}

**Channel:** {channel}  ·  **Durată:** {total:.0f}s  ·  **Verificat:** {data.get("verified", False)}
**Thumbnail:** {slug}_thumb.jpg

---

## ▶️ YouTube Shorts

**Titlu:**
{yt_title} #Shorts

**Descriere:**
{hook}

📌 Surse:
{nl.join(src_lines)}
{ver_line}

🎬 Credite:
{nl.join(cred_lines)}

⚠️ {AI_DISCLOSURE_RO}
⚠️ {AI_DISCLOSURE_EN}

{" ".join(yt_tags)}

**Tags (câmpul Tags, fără #):** {", ".join(t.lstrip("#") for t in yt_tags)}

> La publicare setează 'Altered content = Yes' (voce AI).

---

## 🎵 TikTok

**Caption:**
{hook} {" ".join(tt_tags)}

⚠️ {AI_DISCLOSURE_RO}

> Bifează 'AI-generated content' în setările clipului.
"""
    pkg = out_dir / f"{slug}_upload.md"
    pkg.write_text(md, encoding="utf-8")
    thumb = out_dir / f"{slug}_thumb.jpg"
    ok = make_thumbnail(mp4_path, thumb, ffmpeg)
    print(f"  Upload package → {pkg.name}" + (f" + {thumb.name}" if ok else ""))
    return pkg


# ── Pre-publish validation ────────────────────────────────────────────────────

# Russia/hybrid-war stories trigger enhanced verification (>=3 sources, 24h hold).
RUSSIA_FLAG_KEYWORDS = (
    "russia", "rusia", "ukraine", "ucraina", "belarus", "nato", "kremlin",
    "putin", "wagner", "fsb", "svr", "disinformation", "dezinformare",
    "hybrid war", "razboi hibrid", "război hibrid", "election interference",
)

VERIFY_MARKER = re.compile(r"\[VERIFIC[ĂA][^\]]*\]", re.IGNORECASE)


def validate_script(data: dict) -> list[tuple[str, str]]:
    """Editorial gate before a script becomes a publish-ready video.
    Returns (level, message) pairs; level is 'error' (blocks) or 'warn'."""
    issues: list[tuple[str, str]] = []
    text = " ".join(str(data.get(k, "")) for k in (
        "headline", "hook_card", "narration", "source_onscreen",
        "verification_note", "cta_question", "category"))

    markers = VERIFY_MARKER.findall(text)
    if markers:
        issues.append(("error", f"{len(markers)} unresolved verify marker(s), "
                                f"e.g. {markers[0]}"))
    if data.get("verified") is not True:
        issues.append(("error", "verified is not true — nothing publishes unverified"))
    if not str(data.get("source_onscreen", "")).strip():
        issues.append(("error", "missing source_onscreen — sources must show on screen"))
    if not str(data.get("narration", "")).strip():
        issues.append(("error", "missing narration"))

    n_sources = (1 if str(data.get("source_onscreen", "")).strip() else 0) \
        + len(data.get("sources", []))
    if n_sources < 2:
        issues.append(("warn", f"only {n_sources} source(s); editorial minimum is 2 "
                               f"(add a sources[] list)"))

    if any(k in text.lower() for k in RUSSIA_FLAG_KEYWORDS):
        if n_sources < 3:
            issues.append(("error", f"Russia-flagged story needs >=3 sources; "
                                    f"found {n_sources}"))
        issues.append(("warn", "Russia flag: >=2 sources must be official/institutional "
                               "and hold 24h before publishing"))
    return issues


def _report_validation(name: str, issues: list[tuple[str, str]]) -> bool:
    """Print validation results; return True when there are no errors."""
    errors = [m for lvl, m in issues if lvl == "error"]
    warns  = [m for lvl, m in issues if lvl == "warn"]
    if not issues:
        print(f"  ✓ validation passed")
        return True
    print(f"  {'✗' if errors else '⚠'} {len(errors)} error(s), {len(warns)} warning(s)")
    for m in errors:
        print(f"      ERROR: {m}")
    for m in warns:
        print(f"      warn:  {m}")
    return not errors


# ── Per-script renderer ───────────────────────────────────────────────────────

def _render_script(script_path: Path, out_dir: Path, ffmpeg: str,
                   force: bool = False) -> Path | None:
    data = json.loads(script_path.read_text(encoding="utf-8"))

    print(f"\n=== {script_path.name} ===")
    if not _report_validation(script_path.name, validate_script(data)) and not force:
        print("  SKIPPED — fix the errors above, or re-run with --force")
        return None

    narration      = data.get("narration", "")
    voice          = data.get("voice", "ro-RO-EmilNeural")
    channel        = data.get("channel", "Semnalul Ignorat")
    source_text    = data.get("source_onscreen", "")
    show_source    = data.get("show_source", True)
    slug           = data.get("slug", script_path.stem)
    country        = data.get("country", "")
    fallback_terms = data.get("video_search_terms", ["documentary city", "nature landscape", "people walking"])
    cta_question   = data.get("cta_question", "")
    hook_card      = data.get("hook_card", "")
    if not hook_card and narration:
        first_sentence = re.split(r"[.!?]", narration)[0].strip()
        hook_card = first_sentence[:80]

    mp3_path = out_dir / f"{slug}.mp3"
    ass_path = out_dir / f"{slug}.ass"
    mp4_path = out_dir / f"{slug}.mp4"

    # 1 — Voice
    print(f"[1/4] Synthesizing voice ({voice})...")
    srt = asyncio.run(synth(narration, voice, mp3_path))

    # 2 — Captions
    print("[2/4] Building captions...")
    cues   = parse_srt_words(srt)
    chunks = chunk_captions(cues)
    dur    = media_duration(ffmpeg, mp3_path)
    total  = max(dur, MIN_DURATION)   # pad short videos past TikTok's 60s floor
    ass_path.write_text(
        build_ass(chunks, total, channel, source_text, show_source,
                  hook_card, cta_question, narration_dur=dur),
        encoding="utf-8",
    )
    pad_note = f" (+{total - dur:.1f}s outro)" if total > dur + 0.1 else ""
    print(f"       {len(chunks)} caption chunks, {dur:.1f}s narration{pad_note}")

    # 3 — Images + stat animations
    n_wins    = max(6, min(12, int(total / 5)))
    stat_defs = data.get("stat_windows", [])

    print(f"[3/4] Building {n_wins} visual windows...")
    search_terms = extract_timed_terms(chunks, country, n_wins)
    if not search_terms:
        search_terms = (fallback_terms * ((n_wins // len(fallback_terms)) + 1))[:n_wins]

    stat_clips: dict[int, Path] = {}
    for sd in stat_defs:
        win_idx  = sd["window_idx"]
        out_clip = out_dir / f"stat_{slug}_{win_idx}.mp4"
        if out_clip.exists() and out_clip.stat().st_size > 10_000:
            print(f"  Stat [{win_idx}] cached: {out_clip.name}")
            stat_clips[win_idx] = out_clip
        else:
            clip_dur_est = total / n_wins
            print(f"  Stat [{win_idx}] rendering: {sd.get('metric', '')!r}...")
            if make_stat_clip(sd, clip_dur_est, out_clip, ffmpeg):
                print(f"    ok")
                stat_clips[win_idx] = out_clip
            else:
                print(f"    failed — will use image instead")

    visual_terms = [t for i, t in enumerate(search_terms) if i not in stat_clips]
    print(f"  Visual windows: {len(visual_terms)}")
    for t in visual_terms:
        print(f"    • {t}")
    media = get_scene_media(visual_terms, out_dir, slug, country)
    n_videos = sum(1 for k, _ in media if k == "video")
    print(f"  {len(media)} scene(s) ready — {n_videos} video, "
          f"{len(media) - n_videos} still")

    # 4 — Render
    print(f"[4/4] Rendering {W}×{H} @ {total:.1f}s...")
    ass_arg = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")

    if media or stat_clips:
        # Interleave stat windows with fetched media in window order.
        media_iter = iter(media)
        n_windows  = len(media) + len(stat_clips)
        scene_order: list[tuple[str, Path]] = []
        for win_idx in range(n_windows):
            if win_idx in stat_clips:
                scene_order.append(("stat", stat_clips[win_idx]))
            else:
                scene_order.append(next(media_iter))

        # One ffmpeg input per scene, in order: stills are looped, clips are not.
        inputs: list[str] = []
        scenes: list[tuple[str, int]] = []
        for idx, (kind, path) in enumerate(scene_order):
            if kind == "image":
                inputs += ["-loop", "1", "-r", str(FPS), "-t", "999", "-i", str(path)]
            else:  # video or stat mp4
                inputs += ["-i", str(path)]
            scenes.append((kind, idx))

        audio_idx = len(scene_order)
        filter_str, clip_dur = build_filter_complex(ass_arg, scenes, total)
        # When padded, fade the narration out and fill the outro with silence.
        afilter = (f"afade=t=out:st={max(0.0, dur - 0.4):.2f}:d=0.4,apad"
                   if total > dur + 0.1 else "anull")

        cmd = [
            ffmpeg, "-y",
            *inputs,
            "-i", str(mp3_path),
            "-filter_complex", filter_str,
            "-map", "[v]", "-map", f"{audio_idx}:a",
            "-af", afilter,
            "-c:v", "libx264", "-preset", "medium", "-crf", "26",
            "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(total + 0.3),
            str(mp4_path),
        ]
    else:
        cmd = [
            ffmpeg, "-y",
            "-f", "lavfi", "-i",
            f"gradients=s={W}x{H}:c0=0x0a0a14:c1=0x05050b"
            f":nb_colors=2:speed=0.004:d={total:.2f}:r=30",
            "-i", str(mp3_path),
            "-filter_complex", filter_gradient(ass_arg),
            "-map", "[v]", "-map", "1:a",
            "-af", "apad",
            "-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(total),
            str(mp4_path),
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ffmpeg error:\n" + result.stderr[-3000:])
        return None

    size_mb = mp4_path.stat().st_size / 1_048_576
    print(f"  Done → {mp4_path}  ({size_mb:.1f} MB, {total:.1f}s, "
          f"{n_videos} video + {len(media) - n_videos} still + "
          f"{len(stat_clips)} stat scenes)")

    write_upload_package(data, out_dir, slug, total, ffmpeg, mp4_path)
    return mp4_path


# ── Concat helper ─────────────────────────────────────────────────────────────

def _concat_videos(mp4_paths: list[Path], out_path: Path, ffmpeg_bin: str) -> None:
    list_path = out_path.parent / "_concat_list.txt"
    list_path.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in mp4_paths),
        encoding="utf-8",
    )
    result = subprocess.run(
        [ffmpeg_bin, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_path), "-c", "copy", str(out_path)],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        size_mb = out_path.stat().st_size / 1_048_576
        print(f"\nCombined → {out_path}  ({size_mb:.1f} MB, {len(mp4_paths)} scripts)")
    else:
        print(f"Concat failed:\n{result.stderr[-2000:]}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    args         = sys.argv[1:]
    force        = "--force" in args
    check_only   = "--check" in args
    script_paths = [Path(a) for a in args if not a.startswith("--")]
    if not script_paths:
        print("Usage: python tools/make_video.py [--check] [--force] "
              "<script1.json> [script2.json ...]")
        sys.exit(1)

    # Validation-only mode: report and exit non-zero if any script has errors.
    if check_only:
        all_ok = True
        for sp in script_paths:
            print(f"=== {sp.name} ===")
            try:
                data = json.loads(sp.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"  ✗ cannot read: {e}")
                all_ok = False
                continue
            all_ok = _report_validation(sp.name, validate_script(data)) and all_ok
        print(f"\n{'All scripts valid ✓' if all_ok else 'Validation FAILED ✗'}")
        sys.exit(0 if all_ok else 1)

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    mp4_paths: list[Path] = []
    for sp in script_paths:
        mp4 = _render_script(sp, out_dir, ffmpeg, force=force)
        if mp4:
            mp4_paths.append(mp4)

    if len(mp4_paths) > 1:
        _concat_videos(mp4_paths, out_dir / "combined.mp4", ffmpeg)
    elif mp4_paths:
        print(f"\nOutput → {mp4_paths[0]}")


if __name__ == "__main__":
    main()
