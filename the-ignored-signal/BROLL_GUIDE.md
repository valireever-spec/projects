# B-roll Rules — writing `video_search_terms`

Free stock (Pexels) has almost no real Romania footage, so loose terms return
US dashcams (police cars with "911"), Italian streets, or off-topic junk (a
person feeding a bird from a car window). For a Romanian news channel, wrong-
country or off-topic footage destroys credibility. These rules keep every scene
either **authentically Romanian** or **place-agnostic**.

## How the renderer sources each term

- A term that **contains the country name** ("Romania …") is a **PLACE shot** →
  the renderer fetches a real, geotagged Romania photo from **Wikimedia Commons
  first** (with Ken Burns motion). Falls back to Pexels only if Commons has
  nothing.
- Any other term is a **CONCEPT shot** → **Pexels video** (motion).
- Content-hash dedup guarantees no clip repeats within or across a render run.

## The formula: ~4 anchors + ~6 concepts (10 terms/script)

**1. Anchors (3–5) — real Romania places.** Prefix with `Romania` + a named place
Commons actually has, and a simple noun. Reliable subjects: **Bucharest, Cluj,
Timișoara, Iași, Brașov, Sibiu, Constanța, Giurgiu, Transfăgărășan, Carpathian**.
Examples: `Romania Bucharest street traffic`, `Romania Cluj old town`,
`Romania mountain road Transfagarasan`. These render as authentic Romania stills.

**2. Concepts (5–6) — place-agnostic close-ups / abstracts** that physically
cannot reveal a country. Prefer interiors, close-ups, hands, feet, objects,
textures, top-down aerials. Examples:
`rain on car windshield close up`, `hands on steering wheel driving`,
`feet walking pedestrian crosswalk close up`, `red traffic light close up`,
`syringe vaccine close up`, `hands typing keyboard`, `empty classroom desks`,
`worn child shoes close up`, `highway cars aerial top down`.
**Do not** put `Romania` in a concept term — it would route to Commons and grab
an unrelated photo.

**3. NEVER use** — these pull foreign or off-topic stock:
- US / emergency magnets: `ambulance`, `911`, `police`, `sheriff`, `car crash`,
  `accident`, `highway sign`.
- Wide identifiable scenes from Pexels: `city street`, `downtown`, `storefront`,
  `people walking street` — they expose foreign plates, signage, language.
- Vague verbs: `driving`, `rural road driving` — return random clips (this is
  where the bird-in-car came from).

**4. Stay on topic.** Every term must depict the story's subject
(health → clinic / patient / syringe; education → classroom / reading;
poverty → modest home / worn shoes; roads → traffic / crossing / steering wheel).

**5. Mind the stat slot.** If the script has a `stat_window` at `window_idx: 3`,
the term at **index 3** (0-based) of `video_search_terms` is consumed by the
chart. Put a **disposable concept** there, never a prized anchor.

## Always spot-check after rendering

Build a contact sheet and eyeball every scene; replace any foreign/off-topic clip
by rewording that term (make it an anchor, or a tighter close-up), then re-render.

```bash
FF=$(.venv-video/bin/python -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
for f in output/clip_<slug>_*.mp4; do
  "$FF" -y -loglevel error -ss 2 -i "$f" -frames:v 1 -vf scale=320:-1 "/tmp/$(basename "$f").png"
done   # then view the /tmp/*.png tiles
```

## Worked example — `06_siguranta_rutiera` (road safety)

```
"Romania Bucharest street traffic",      # anchor  → real Bucharest
"Romania mountain road Transfagarasan",  # anchor  → real Transfăgărășan
"Romania Bucharest traffic evening",     # anchor  → real Bucharest
"rain on car windshield close up",       # concept (index 3 → eaten by stat)
"Romania traffic street Giurgiu",        # anchor  → real Giurgiu
"car headlights night dark road",        # concept
"feet walking pedestrian crosswalk close up",  # concept
"red traffic light close up",            # concept
"highway cars aerial top down",          # concept (top-down hides plates)
"hands on steering wheel driving"        # concept (interior)
```

Result: 6 real-Romania stills + 5 place-agnostic clips — zero foreign or
off-topic footage.
