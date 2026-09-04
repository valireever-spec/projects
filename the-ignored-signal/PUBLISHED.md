# Published videos — Sub Radar

Tracks which scripts are **live** and how they perform. Two rules:

1. **Do not re-render or overwrite a LIVE video** (`output/<slug>.mp4`, `.mp3`,
   `.ass`, thumbnail, upload package) without asking — the published version must
   stay reproducible. Quality-pass re-renders only apply to unpublished scripts.
2. Add an analytics snapshot whenever new performance data comes in (append,
   don't overwrite — the history shows what changes help).

Channel baselines (update as they shift): **view rate ~58.3%**, **avg view
duration ~28s**. Retention target for stat-heavy Shorts: **>60%**.

## Status

| #  | Slug                       | Title                                                     | Platform       | Published   | Status | Views* |
|----|----------------------------|-----------------------------------------------------------|----------------|-------------|--------|--------|
| 01 | `01_toaleta_apa`           | Cea mai mare pondere din UE fără toaletă cu apă în casă    | YouTube Shorts | 2026-08-21  | LIVE   | 20     |
| 02 | `02_saracie_energetica`    | Unul din șase români nu-și poate încălzi locuința         | YouTube Shorts | 2026-08-22  | LIVE   | 13     |
| 04 | `04_cancer_col_uterin`     | Cea mai mare mortalitate prin cancer de col uterin din UE | YouTube Shorts | 2026-08-22  | LIVE   | 25     |
| 08 | `08_saracia_copiilor`      | Unul din trei copii din România e la risc de sărăcie      | YouTube Shorts | 2026-08-21  | LIVE   | 11     |

*Views as of 2026-08-22, first 24–48h. Unpublished: 03, 05, 06, 07, 09, 10.

> **Do not re-render 01/02/04/08.** New hook/pacing changes apply only to the
> unpublished six.

## Scheduled — auto-publish one per day (all uploaded 2026-08-22)

> **UPCOMING SCHEDULE (private + publishAt, verified via API 2026-09-04 — source
> of truth; table below is historical). Daily 19:00 RO (16:00Z), gap-free:**
> 09-05 `Bf74MFSgqvk` 16 poluare · 09-06 `tu0yw3clUhY` 14 tezaur ·
> 09-07 `wRpNTAFFE0c` 18 Polonia · 09-08 `arsXkGsJfMw` 22 remese ·
> 09-09 `KmS5huTI2l8` 23 copii-rămași · 09-10 `bLUMD8BDvPY` 24 pensionari-vs-salariați ·
> 09-11 `RNcz_80FtS4` 25 sate · 09-12 `Yz0LV4uPunU` 26 întorc ·
> 09-13 `2b8IDJS0iP0` 27 pensii-speciale · **09-14 `8vuX0s8g3Qc` 21 instabilitate 🆕** ·
> 09-15 `6jdlrpOwC_4` 28 PNRR · **09-16 `dhWc5XEjou4` 30 SOTEU 🆕** ·
> 09-17 `CXKuSNII1kM` 29 Neptun-Deep.
> **2026-09-04:** filled the only gap (09-14) with **21 instabilitate guverne**
> (26 PM vs 4) and added **30 SOTEU** at 09-16 — both via `upload.py --publish-at`
> (schedule_uploads.sh maps date by queue position, can't target a single day).
> Bulk 09-05→09-13/15/17 were scheduled in the 2026-09-02 upload batch.
> **Pipeline fully scheduled 09-05→09-17, gap-free — nothing rendered-but-
> unscheduled remains.** (`24_cine_iti_plateste_pensia` is scheduled 09-10 —
> earlier mislabeled here as "20 imigranți"; video 20 is already public/live.)
> ⚠️ Match uploaded videos to scripts by **headline**, not truncated titles —
> `bLUMD8BDvPY`'s title ("…mai mulți pensionari") is 24, not 20.
> **MANUAL for every scheduled video before its publish time:** set
> Altered content = Yes (AI voice); pin the auto-posted debate comment.

Re-rendered 2026-08-22 with question-hooks + quality pass (loudnorm −14 LUFS,
crf 20 encode); stat videos (05/06/10) also got faster ~4s pacing. Uploaded as
private drafts via `tools/schedule_uploads.sh`, each with a `publishAt` (19:00
Europe/Bucharest). YouTube flips them to Public at that time.

**Before each publish time, in Studio:** ① set **Altered content = Yes** (AI),
② set the branded thumbnail for the five marked *auto* (see note below).

| Publish (19:00 RO) | # / Slug                       | Video ID     | Thumb  | AI flag |
|--------------------|--------------------------------|--------------|--------|---------|
| 2026-08-23         | `03_taieri_ilegale`            | (test upload)| custom | ☐       |
| 2026-08-24         | `09_depopulare`                | 5jh9Em9QLy8  | custom | ☑       | re-render 2026-08-24: hard-number hook + personal pension pivot (analytics); AI flag set |
| 2026-08-25         | `07_emigratia_medicilor`       | Rh0fT6PNLDw  | custom | ☐       |
| 2026-08-26         | `05_analfabetism_functional`   | d-7riWPCKzA  | custom | ☐       |
| 2026-08-27         | `10_competente_digitale`       | lVI6shAJVsI  | custom | ☐       |
| 2026-08-28         | `06_siguranta_rutiera`         | t83Qa0YQWwE  | custom | ☐       |
| 2026-08-29         | `11_pensii`                    | jpxavB1Q2oM  | PENDING | ☐       | footage QC'd clean (AI+dedup+geo-guard) |
| 2026-08-30         | `12_atunci_speranta_viata`     | IiCjOT0Q480  | PENDING | ☐       | footage QC'd clean; thumb via retry cron |
| 2026-08-31         | `13_ceausescu_datoria`         | TjsASUa2jVw  | PENDING | ☐       | audio fix (+5% pace, no gaps); thumb via finish_pending cron |
| 2026-09-01         | `17_mame_minore`               | tJwHFSIyJhI  | custom  | ☐       | Teen/underage mothers (Eurostat: ~45% of EU under-15 births are RO; 746 girls 10-14 in 2022). All Studio feedback + **AI-generated people-free stills** (`ai:` terms — stock kept leaking people of various ethnicities + off-topic shots; also swapped an uncanny teddy-bear render for baby shoes). `music: false`; narration pause fix ("a șaptea, cresc"). Uploaded 2026-08-26, publishAt 09-01 16:00Z. Sensitive → possible limited-ads. MANUAL: set AI flag. ✅ Debate comment POSTED (`Ugx4GXSyg-Ovhq63Pap4AaABAg`) — **click ⋮ → Pin in Studio**. ✅ Title fixed 09-04 (payoff "în România" restored; was truncated to "…sunt #Shorts"). |
| 2026-09-02         | `15_propaganda_rusa`           | t-_rsypj4Z8  | custom  | ☐       | **NEW-FORMAT PILOT** (catchphrase hook, karaoke, ~3.5s cuts, stat overlay); Russia 24h hold (verified 2026-08-24, clears 08-25); MANUAL: set AI flag. Debate comment AUTO-POSTS on publish (cron → `post_comment.py`); you only click ⋮ → Pin |
| 2026-09-05         | `18_romania_polonia`           | wRpNTAFFE0c  | custom  | ☐       | Romania vs Poland — **continuity angle** from a user-supplied video, all claims re-verified (S&P/FTSE developed-market reclassification, highways 5.200 vs 1.418 km CNAIR/GDDKiA, EU-funds absorption, VAT gap). AI concrete stills; stat overlay km (unit-bug fixed). Uploaded 2026-08-28, publishAt 09-05 16:00Z. ⚠️ reconfirm exact km + €250bn before publish. MANUAL: set AI flag. Debate comment auto-posts → Pin |
| 2026-09-04         | `14_tezaurul_romaniei`         | tu0yw3clUhY  | custom  | ☐       | Displaced from 09-01 by 17. **Re-uploaded 2026-08-26**, publishAt 09-04 16:00Z. **Russia-flagged** (1916 gold to Moscow) — enhanced-verification gate initially blocked it (only 1 authoritative source); added a 2nd (`[STUDIU]` Romașcanu monograph) → passes with BNR primary + study. **Piper/Mihai voice**, Rusia/URSS fix, real Cloșca. MANUAL: set AI flag + human review (Russia 24h). Debate comment auto-posts → Pin |
| 2026-09-03         | `16_poluare_aer`               | Bf74MFSgqvk  | custom  | ☐       | Re-uploaded 2026-08-27 (stat unit fix: bars showed "%" instead of µg/m³ — old draft YtAGQf9Ixco deleted). Air pollution (~18k deaths/yr, EEA + CJUE C-638/18, Ploiești refinery angle). Built 2026-08-26 with **all migration-video Studio feedback**: ~34s, +7% pace, front-loaded stake, stat overlay on Bucharest line (~12.5–15s), debate-CTA close. **People-free / location-neutral b-roll** (no city/skyline/faces). Uploaded 2026-08-26 as private draft, publishAt 09-03 16:00Z. MANUAL: set AI flag. Debate comment auto-posts via `post_comment.py` → click ⋮ → Pin |
| 2026-09-16         | `30_soteu_romania`             | dhWc5XEjou4  | custom | ☐       | **Build-ahead SOTEU newsjack** — "partea despre România pe care n-o auzi" pegs von der Leyen's State of the Union (16 Sep, Strasbourg). `verified=true`; **Russia-clean** (no 24h hold). Rendered 2026-09-04 (36.8s, Piper/mihai, people-free AI stills, deficit **8,4% vs plafon 3%** stat overlay). 4 figures web-verified: SOTEU date, ECB Convergence Report iunie 2026 (euro "progres limitat"), EC deficit forecast, Eurostat tertiary 23,2% vs 44,8%. Uploaded 2026-09-04 (private, publishAt 09-16 16:00Z). ⚠️ **Title fixed via API to payoff-first** (`upload.py` derives title from the headline's FIRST sentence → uploaded the weak setup line; corrected `videos.update` → "Partea despre România pe care n-o auzi…"; SAME bug as 17). MANUAL: set AI flag; pin auto-comment. Optional: after 16 Sep add one line on whether RO was mentioned. |

**Thumbnails:** ✅ all six custom (verified via API 2026-08-22). The five that
initially 429'd on the thumbnail API were set manually in Studio.

**AI flag:** the ☐ column can't be read via API — tick each off here as you set
"Altered content = Yes" in Studio, before that video's publish time.

## Automation status (checked 2026-08-22)

**Automatic publishing is NOT set up — nothing will publish on its own tomorrow.**

- **No scheduler.** No cron / systemd / `at` job runs `tools/upload.py`. The four
  live videos were uploaded manually via YouTube Studio (consistent with the
  point below).
- **No OAuth token** (`tools/.youtube_token.json` absent). `upload.py`'s first run
  opens a browser for consent — so it cannot run unattended until authorized once.
  `tools/client_secret.json` is present (valid Desktop-app credentials).
- **AI disclosure is manual.** YouTube's "Altered content = Yes" (AI voice) flag
  is **not settable via the API** — it must be toggled in Studio before a video
  goes public. This blocks fully hands-off publishing.

**Scheduled daily uploads:** `tools/schedule_uploads.sh` uploads the queue as
private drafts with `publishAt` staggered one per day at 19:00 Europe/Bucharest
(override with `START_DATE=` / `PUBLISH_LOCAL_TIME=`). First run authorizes via
Firefox and writes `tools/.youtube_token.json`.

```bash
tools/schedule_uploads.sh --dry-run          # preview the plan
tools/schedule_uploads.sh 03_taieri_ilegale  # test one (auth + schedule for its day)
# then the remaining five (days stay correct — assigned by queue position):
tools/schedule_uploads.sh 09_depopulare 07_emigratia_medicilor \
    05_analfabetism_functional 10_competente_digitale 06_siguranta_rutiera
```

> ⚠️ Still set **"Altered content = Yes"** in Studio for each draft *before* its
> publish time — the AI disclosure can't be set via API. Running the full script
> again would re-upload duplicates, so pass explicit slugs after the 03 test.

## Channel-level snapshots

### 2026-08-22 — traffic sources (first ~24h, channel is Shorts-only)

| Source                | Views | %   |
|-----------------------|-------|-----|
| Other YouTube features| 13    | 52% |
| YouTube Search        | 7     | 28% |
| Browse features       | 3     | 12% |

Reading:
- **Other YouTube features (52%)** — direct links / shares / internal surfaces.
  Early videos are being opened or shared directly. Good early sign.
- **YouTube Search (28%)** — strong for a 24h-old channel. Titles/topics
  (cervical cancer, child poverty) are actively searched → **titles and topics
  matter; keep them clear and search-legible.**
- **Browse features (12%)** — Home / subscriptions feed. Grows as we publish more.
- **Shorts feed is not yet the primary source** — normal at 24h. To grow it:
  keep relevant hashtags + `#Shorts` in the description (helps placement in the
  vertical feed), and lift retention (>60%) so the algorithm pushes it wider.

## Analytics snapshots

### Geography — 2026-08-29 (~1.372 views) — DIASPORA is half the audience

| Țară | Views | % | AVD | Citire |
|------|------:|--:|-----|--------|
| România | 700 | 51% | **0:17** | jumătate din views, dar cea mai slabă retenție |
| Germania | 182 | 13% | 0:24 | diaspora |
| Italia | 126 | 9% | **0:39** | diaspora — de 2,3× timpul României |
| Moldova | 84 | 6% | 0:25 | vorbitori de română |
| Spania | 56 | 4% | 0:25 | diaspora |
| Austria/UK/Franța | 86 | 6% | ~0:21 | diaspora |

**Two strategy-shaping findings:**
- **~49% of viewers are abroad** (DE/IT/ES/AT/UK/FR) + Moldova — the exact top
  Romanian-diaspora countries. Audience = Romanians at home AND diaspora, ~half each.
- **Diaspora retention is far higher:** Romania 17s vs Italy 39s (2.3×), DE/MD/ES
  ~24–25s (~1.5×). Romania = 51% of views but only 38% of watch time; Italy = 9% of
  views but 17% of watch time. The people who LEFT are the most engaged — the core
  topics (migration, depopulation, Poland comparison) are literally their story.

Actions:
- **Frame migration/diaspora content to the person abroad** ("tu, care ai plecat în
  Italia/Germania…"). Doubly validates the migration + internal-politics focus.
- **Domestic 17s retention is the drag** → the ≤35s + first-8s-stake fixes target it;
  also test a less-fatalistic tone for home (relentless "Romania is failing" may cause
  domestic swipe while diaspora leans in). See [[ignored_signal_script_pattern]].
- **Growth:** DE/IT diaspora already highly engaged in Romanian → DE/IT subtitles (or
  the deferred multilingual expansion) would compound an audience already watching.

### Channel — 2026-08-28 (14-day pull + realtime)

Totals (14d): **1.780 views, +6 subs, AVD 23s, 50,9% avg watched, 30 likes, 2 comm.**
Traffic: **94% Shorts feed** (up from ~53% a week ago) → retention is now the master
lever (feed push scales with it). Public videos: 9, ~2.072 views total.

Per-video (retention%): migration 1.364 / 49,2% · doctors 291 / 45,0% · court(CJUE)
125 / 57,3% · analfabetism 147 · cancer 40 / 45,9% · toaletă 35 / 111,9% (loops) ·
energie 19 / 60,4% · sărăcia copiilor 17 / 75,7% · competențe digitale 56 (day 1).

Issues → fixes:
- **Retention/length:** most 45–57% watched, videos 45–51s. Migration curve drops
  106%→76%→54% across 10–30% — bleeds between hook and the data section. Fix:
  ≤35s (done on 16/17/18) + **move the personal stake into the first ~8s** (before
  any methodology). See [[ignored-signal-script-pattern]].
- **Engagement 1,7% likes / 2 comments:** debate-CTA + auto-pinned comment on
  16/17/18 (live 09-01→05) — watch whether comments lift.
- **Single-video dependence:** migration = 65% of views. Repeat the winning formula
  (universal + personal + hard-number). Abstract stat topics (energy, child poverty,
  digital skills) consistently flop; personal/accountability ones win.



### 07_emigratia_medicilor — "Aproape paisprezece mii de medici au plecat din România între 2009 și 2015 #Shorts"

**2026-08-26 — ~1 day after publish (YouTube Studio feedback)**

- **250+ views** — typical range (not a breakout like 09).
- **View rate 34.9%** — just above channel avg (34.7%). Hook works.
- **AVD 21s = 42.8% of a 51s video.** Two familiar problems: **(1) too long** —
  51s is well over the ~34s target (same spelled-out-numbers bloat we keep hitting);
  **(2) mid-video technical dip** — narration goes technical mid-way (years of med
  school, state funding) and loses viewers before the human/patient impact lands.
- **3 likes, 0 comments** — the passive-consumption / no-debate-CTA pattern again.

Reinforces the exact fixes now standard on 16/17: compress to ~30–34s, front-load
the human stake, end on a debate question. Studio's own suggestion for next time:
close with "Cunoști spitale rămase fără specialiști?" or "Ce i-ar face pe medici
să rămână?"

### 09_depopulare — "Peste trei milioane de români au plecat din țară de la aderarea la UE #Shorts"

Video ID `5jh9Em9QLy8` · published 2026-08-24 16:00 UTC.

**2026-08-25 — ~24h after publish (realtime `videos.statistics`, YouTube Data API)**

- **1,325 views · 22 likes · 1 comment** — a **breakout**: ~40–60× the channel's
  11–37 first-24–48h baseline. Best-performing video to date by a wide margin.
- Hard-number hook ("Peste trei milioane…") + personal pension pivot (the
  analytics-driven re-render from 2026-08-24). This format is working — reuse it.

> ⚠️ Source note: these are **realtime** counts from `videos.statistics`. At the
> time of capture the **Analytics API lagged** — `tools/analytics.py` (7-day,
> `yt-analytics`) showed only 89 channel views and didn't list this video, and the
> cached channel total read 195. That is reporting lag (~1–3 days), **not** a
> different channel — both resolve to `UClF3jQtev_wsMBZuce7ZQvg` (Sub Radar).
> See [[ignored-signal-analytics-lag]].

To capture once the Analytics API catches up (re-run `analytics.py` ~2026-08-27):
- **Traffic source split** — confirm the Shorts feed drove the breakout.
- **Retention / avg view %** — the finalized drop-off curve for this hook+pivot.

### 02_saracie_energetica — "Unul din șase români nu-și poate încălzi locuința #Shorts"

**2026-08-22 — first hours after publish (YouTube Studio feedback)**

Working:
- **15 views** in the first hours — typical early-hours range for the channel.
- **View rate 61.5%** (chose to watch) — above the channel's ~58.3% average.
  Energy-poverty topic resonated in the Shorts feed.

To improve:
- **Avg view duration 25s = 51.3%** of the video — slightly below the channel's
  typical ~28s.
- **Drop-off toward the end.** The health-consequences explainer (from 0:21) is
  the crucial section but interest fades before it lands.

YouTube's recommendations:
- **Hook:** open the first second with a direct question or a stronger image to
  lift the view/choose rate further.
- **Pacing:** for future stat-driven Shorts (e.g. Eurostat data), use faster
  transitions between the numbers and the human impact to hold retention >60%.

## Lessons learned

### 2026-08-25 — first breakout + an analytics-reading mistake

**What worked (reuse it).** `09_depopulare` hit **1,325 views / 22 likes / 1
comment at ~24h — ~40–60× the channel's 11–37 first-day baseline**, the channel's
first real breakout. The winning formula was the 2026-08-24 re-render:
**hard-number declarative hook** ("Peste trei milioane…") **+ a concrete personal
mid-pivot** (the pension consequence). This matches the analytics-derived script
pattern — keep applying it to the stat-heavy Shorts (which historically had the
weakest retention, e.g. cancer col uterin at 42.8%).

**Reading-the-data lesson.** Realtime counts (YouTube Studio /
`videos.statistics`) and the **Analytics API** (`tools/analytics.py`,
`yt-analytics`) **disagree for ~1–3 days after publish** — the Analytics API and
the cached channel total lag badly. On 2026-08-25 the realtime counter showed
1,325 views while a 7-day `analytics.py` pull reported only 89 channel views and
didn't list the video at all (same channel `UClF3jQtev_wsMBZuce7ZQvg` — pure lag,
not a different account). **Rule:** for anything published in the last ~3 days,
trust Studio / realtime `videos.statistics`; use `analytics.py` only for
finalized traffic-source and retention breakdowns once the data settles.

**Two winning hook types (full-channel pull, 2026-08-25).** Ranking all live
videos by views surfaced a second breakout pattern beyond the hard-number hook:
- **Hard-number national-scale hook** — migration (1,325). "Peste trei milioane…"
- **Institutional-accountability hook** — the CJUE court-case video (`-lsgnUweXe8`,
  "România dată în judecată la Curtea de Justiție", illegal logging) is #2 at
  **121 views (~4–6× baseline)** with zero promotion. "Romania got sued / Romania
  leads the EU in X" framings — concrete, high-stakes — outperform.

**Retention tracks concreteness, not topic.** Finalized per-video retention:
videos that *hold* pair **one number with one human/relatable image** (toaletă
133% w/ replays, sărăcia copiilor 73.6%); videos that *bleed* stack multiple
stats (cancer col uterin 42.8%, sărăcie energetică 51.3% — Eurostat+OECD+natural
growth in one Short). **Rule: one stat, one image — stop stacking data points.**

**Ops note:** scheduled drafts (07/05/06/10/11/12/13/15) were still `private`
with 0 views on 2026-08-25 — the daily auto-flip-to-public isn't running by
itself (consistent with the "no scheduler" note above). Check each draft actually
goes Public at its publish time.

**Render gotchas (from building script 16, air pollution).**
- **Footage cache is keyed by slot index, not search term.** `make_video.py`
  reuses `output/clip_<slug>_<N>.mp4` if it exists — so changing
  `video_search_terms` does NOTHING until you `rm -f output/clip_<slug>_*.mp4`
  (and `img_<slug>_*`). Always clear a slug's cached clips before re-rendering a
  footage change, or you ship the old clips. See [[ignored-signal-render-cache-trap]].
- **Geo-guard only fires on the literal word "romania" in a term.** City names
  (Bucharest/Ploiești) slip through to ungeofenced Pexels → foreign leakage
  (an Istanbul "Atatürk Havalimanı" clip appeared; Bucharest footage stood in for
  Ploiești). Fix: use **location-neutral, people-free close-ups** (exhaust pipes,
  smokestacks, refinery flares, cooling towers, x-rays) — no wide city/skyline/
  traffic shots, no city names, no identifiable people. Keeps Romania-topic videos
  from showing places or faces that don't match.
- **Stock is uncontrollable for people/topic — use `ai:` terms for sensitive or
  people-risk scenes.** "Empty classroom/playground" Pexels queries still returned
  clips with people (various ethnicities) and off-topic shots (hit on script 17).
  Prefix a `video_search_terms` entry with **`ai:`** to force AI-generated imagery
  (Pollinations) that you fully control — no real people, guaranteed on-topic.
  Caveat: Pollinations is flaky (~half failed on first pass for 17); **re-run the
  render 2–3× — cached successes persist, only failures retry.** Result is stills
  (Ken Burns), not video — fine/fitting for grave topics.
- **Russia-flag matcher is a naive substring scan.** The word "Rusia" anywhere in
  the JSON (even a note saying "nu declanșează flag Rusia") trips the 24h hold.
  Don't name the keyword in verification_note.
- **Captions now keep `?` and `!`** (was stripping all trailing punctuation) — so
  the debate-CTA reads as a question on screen. Pipeline-wide change.
- **Length:** spelled-out Romanian numbers inflate runtime badly — a script that
  read ~32s on paper rendered 48.9s. Target the *rendered* length; trim to ~34s.

**`stat_windows` default unit is `%`.** If a stat window omits `"unit"`, the
renderer prints the value with a **`%` suffix** (make_video `make_stat_clip`,
`unit = stat.get("unit", "%")`). Correct for percentages (e.g. 17: 4,6% / 45%),
but WRONG for absolute values — 16 showed PM2.5 as "15.7%" and 18 showed roads as
"5200%". Fix: set **`"unit": ""`** (or a real unit like `" µg/m³"`) for any
non-percentage stat. Caught on 18; retro-fixed 16 (re-uploaded → Bf74MFSgqvk, old
draft deleted). Also note: value labels are hard-formatted `.1f`, so integers show
a trailing `.0` ("5200.0") — cosmetic.

**AI (`ai:`) prompts: avoid abstract words.** "glowing bar chart", "golden arrow
over an abstract grid", "economy concept" rendered as abstract blobs (flagged on
18). Use concrete, photographic scene descriptions (real highways, trains, ports,
cracked roads) — drop "concept/abstract/grid/glowing".

**Footage for abstract/economic topics (from clip 19 PNRR — screen every clip).**
Free stock (and AI) can't reliably show **euro cash, hospitals, or schools**: those
queries return US-dollar finance graphics, metro plazas, arty derelict buildings,
and even a road selfie that reappears for any generic "road" query. AI renders
abstract shells + illegible currency. **What free stock DOES deliver cleanly:**
aerial highways, construction sites, tower cranes, unfinished/under-construction
buildings, bridges. So for money/infrastructure stories: build b-roll from those
categories + let the **stat overlay carry the € figure**; avoid "euro banknotes",
"hospital", "school", "road construction" terms. **Always screen each clip** (grab
a frame per `clip_<slug>_N.mp4`) — and NEVER upload before the user reviews.
Process note: uploaded clip 19 unreviewed with mismatched footage → had to re-do.

**Topic sourcing.** YouTube Studio's **Inspiration / Research tab** is a good
source of channel-fit topic ideas but is **not exposed by any public API** — it
can't be pulled programmatically; ideas must be copied in manually. Candidates
surfaced 2026-08-25 (both fit the winning "systemic-failure data story" format):
- **Teen mothers** — Romania leads the EU in teenage births; ~1 in 10 births
  involves a minor; rural clinic underfunding → legislative silence.
- **Bucharest air quality** — particulate levels consistently exceed EU legal
  limits; trace pollutants from boulevards into homes.
  (Both are domestic social/environmental stories — standard 2-source verification
  applies; neither triggers the Russia enhanced-verification hold.)
- **Romania vs Poland comparison** (requested 2026-08-26; **numbers verified &
  CORRECTED 2026-08-26**). ⚠️ First-pass verification was wrong (trusted a
  secondary source); the primary Eurostat series corrects it:
  - **GDP/capita PPS (EU=100), Eurostat tec00114:**
    Poland 78 (2022) → 77 (2023) → 78 (2024);
    Romania 72 (2022) → 75 (2023) → 77 (2024).
    **Poland is still ahead every year** — Romania has NOT overtaken it. But Romania
    closed the gap fast: −6 (2022) → −2 (2023) → **−1 (2024)**. Story = convergence,
    NOT overtaking. (A Romania Insider piece claiming RO 78 / PL 77 in 2023 used an
    early preliminary later revised down to 75 — do not cite it.)
  - **Population: both shrinking.** Poland peaked ~38.6M → ~36.5M (2025), EU's
    largest absolute decline in 2023–24. Romania 23.2M (1990) → 19.06M (2024),
    −4.16M (63% emigration, 37% natural). Real gap is *emigration share*, not
    stability.
  - **Solid "Poland did better" contrasts:** (1) **resilience** — only EU economy to
    avoid the 2009 recession (+2.6–2.8%, "green island"), ~28 yrs unbroken growth
    1992–2020; Romania crashed 2009 + IMF/EU bailout + austerity. (2) **emigration** —
    Romania lost proportionally far more people; Poland net-immigration in the 2010s.
  - **Recommended angle (honest):** convergence + cost — "Romania has almost caught
    up to Poland (within 1 point of EU-avg GDP/capita) — but bled 4 million people
    and needed an IMF bailout to get there." Do NOT claim Romania overtook Poland.
  - Must-verify before scripting: re-pull Eurostat tec00114 for the latest year;
    figures are **PPS (purchasing power)** — Poland is further ahead in *nominal*
    GDP/capita, so the script must say "la paritatea puterii de cumpărare."
  - Sources: [PRIMARĂ] Eurostat GDP/capita PPS tec00114; [INSTITUȚIONAL] World Bank
    Romania migration SCD; OSW demographic commentary; Hoover/Brookings/CFR on
    Poland 2009. Non-sensitive; no Russia trigger. **Backlog — not scripted.**
