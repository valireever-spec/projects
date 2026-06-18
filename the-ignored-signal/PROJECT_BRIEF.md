# The Ignored Signal — Project Brief

> *Stories that existed. Signals that were real. Nobody amplified them. Until now.*

---

## 1. Concept

**The Ignored Signal** is an independent, anonymous, multilingual short-form news channel covering important European stories that mainstream media underreported, ignored, or explained poorly.

The tone is a trusted friend explaining something significant — clear, warm, serious, never sensationalist. Every story is backed by legitimate, named, verifiable sources shown on screen.

**The channel does not uncover secrets. It amplifies signals that were already there but nobody listened to.**

---

## 2. Mission Statement

> *"Stories that happened. Sources that prove it. Explained so anyone can understand."*

---

## 3. Brand

### Channel Names (by language)

| Flag | Language | Channel Name |
|------|----------|--------------| 
| 🇬🇧 | English  | **The Ignored Signal** |
| 🇫🇷 | French   | **Le Signal Ignoré** |
| 🇩🇪 | German   | **Das Überhörte Signal** |
| 🇮🇹 | Italian  | **Il Segnale Ignorato** |
| 🇷🇴 | Romanian | **Semnalul Ignorat** |

### Tagline
> *"The signal was always there. Nobody amplified it."*

### Visual Identity
- **Style:** Clean, stark, documentary aesthetic
- **Palette:** Black and white base with one strong accent — deep red (`#c0392b`) or electric blue (`#1a6bb5`)
- **Typography:** Sans-serif, typewriter or ticker energy
- **Feel:** Classified document being opened. Factual. Trustworthy. Not corporate, not conspiratorial
- **No face on camera. No real voice. AI narrator only.**

---

## 4. Target Audiences

| Language | Primary Audience |
|----------|-----------------|
| 🇬🇧 English  | UK, Ireland, Northern Europe, international English speakers |
| 🇫🇷 French   | France, Belgium, Switzerland, Luxembourg |
| 🇩🇪 German   | Germany, Austria, Switzerland |
| 🇮🇹 Italian  | Italy, Switzerland, Italian diaspora across Europe |
| 🇷🇴 Romanian | Romania, Romanian diaspora across Western Europe (Italy, Germany, Spain, UK) |

**Core audience profile:** Educated Europeans aged 25–50, secular-leaning, politically moderate, disillusioned with mainstream media, not conspiracy-minded — simply underserved by existing journalism.

**Addressable audience:** ~260–270 million people across the five language zones.

---

## 5. Platforms

- **YouTube Shorts** — one channel per language (five channels total)
- **TikTok** — one account per language (five accounts total)
- **Total:** 10 accounts across both platforms
- Each account is completely independent — separate brand, separate algorithm, separate audience

---

## 6. Monetization

### Phase 1 — Launch (no monetization)
- Full anonymity, no identity required
- Focus entirely on content quality and audience building
- Test format, tone, story selection, and platform response

### Phase 2 — Monetization (when traction is proven)
- YouTube Partner Program + TikTok Creator Fund
- Revenue handled through an **Estonian e-Residency company**
  - Register at: [e-resident.gov.ee](https://e-resident.gov.ee)
  - Company name suggestion: `Ignored Signal Media OÜ`
  - Cost: ~€100–200 to set up
  - Full EU legal compliance, personal identity protected behind corporate structure
- Additional monetization paths: sponsorships from publishers, educational platforms, cultural organisations, Patreon, speaking engagements

---

## 7. Content Categories

| # | Category | Description |
|---|----------|-------------|
| 1 | **EU Legislation & Policy** | Decisions affecting 450 million Europeans passed with almost no public debate |
| 2 | **Economic Stories** | Housing crisis, energy poverty, real inflation impact, small business collapse |
| 3 | **Environmental Findings** | Research and damage that gets one news cycle then disappears |
| 4 | **Scientific Research** | Findings that complicate or contradict official positions |
| 5 | **Historical Context** | What shaped modern Europe that schools never taught |
| 6 | **Human Interest** | Extraordinary quiet stories from across the continent |
| 7 | **Hybrid War — Russia** | Disinformation networks, cyberattacks, energy weaponisation, election interference mechanisms — the how, not just the headline |
| 8 | **Human Rights Violations** | Per country — documented sources only (UN, Council of Europe, Amnesty International, Human Rights Watch, court records) |
| 9 | **Corruption** | EU institutions, national governments, corporate — verified cases only |

---

## 8. Editorial Rules

These rules are non-negotiable. They protect the channel legally and build audience trust.

1. **Minimum two independent legitimate sources per story**
2. **At least one primary source** — official document, government data, peer-reviewed research, court record
3. **Sources shown visibly on screen** in every video
4. **No speculation** — only verified facts
5. **No personal opinion** — present, do not editorialize
6. **No unverified accusations** against named individuals
7. **Include official government responses** where they exist
8. **Stories must directly affect or be relevant to ordinary Europeans**
9. **One language per video** — never mix languages in a single video
10. **One platform per video** — optimise for the specific platform's algorithm
11. **Nothing publishes without Verified status** from the Verification Engine

### What makes a story worth covering
- It directly affects ordinary Europeans
- It was reported briefly then disappeared from the news cycle
- The implications were never properly explained to a general audience
- The mainstream framing missed the real point
- It is fully verifiable from legitimate sources

### What does NOT get covered
- Stories requiring speculation to be interesting
- Sources that are questionable or unverifiable
- Stories already saturating mainstream media
- Anything requiring personal opinion to make sense of

---

## 9. Video Format

**Target length:** 45–90 seconds depending on story complexity

### Structure (per video)

| Segment | Duration | Content |
|---------|----------|---------| 
| **Hook** | 3–5s | The thing that was not reported — stated as a fact, not a question |
| **What happened** | 15–20s | The verified facts, clearly stated |
| **Why it matters** | 15–20s | The direct implication for ordinary Europeans |
| **The source** | 5s | Shown on screen — institution, document name, date |
| **Call to action** | 5–7s | *"Follow for more ignored signals"* |

### Tone
A trusted friend who happens to know things. Not a news anchor. Not an academic. Not an activist. Someone who read the report, understood it, and is now telling you clearly what it means for your life.

- Never opinionated
- Never sensationalist
- Never speculative
- Always sourced
- Always clear to a non-specialist

---

## 10. Intelligence Layer — Story Discovery & Verification

This is the editorial research engine that feeds the content pipeline. Three connected tools that work in sequence before any story reaches the script generator.

### Architecture

```
DISCOVERY                      VERIFICATION                  PRODUCTION
──────────────────────         ───────────────────           ──────────────────
Press Coverage Analyzer  →     Verification Engine     →     Script Generator
Viral Content Scanner    →     ↓                       →     Visibility Advisor
Manual Input             →     Verified ✅ / Partial ⚠️      Content Calendar
                               / Rejected ❌                  Export
                               ↓
                         Russia Disinfo Flag 🚩
                         (stricter rules apply)
```

### Tool 1 — Press Coverage Analyzer

Monitors major European outlets daily using Claude API with web search. Identifies stories that appeared once and disappeared, or important topics with suspiciously low coverage volume.

**Output:** List of candidate stories scored by importance-to-coverage ratio.

**Sources monitored per language:**

| Language | Outlets |
|----------|---------|
| 🇬🇧 English | BBC, Guardian, Reuters, Politico Europe, The Times |
| 🇫🇷 French | Le Monde, Le Figaro, Libération, Mediapart, AFP |
| 🇩🇪 German | Spiegel, FAZ, Süddeutsche Zeitung, Zeit, DPA |
| 🇮🇹 Italian | Repubblica, Corriere della Sera, ANSA, Il Fatto Quotidiano |
| 🇷🇴 Romanian | Digi24, ProTV, G4Media, HotNews, Euractiv Romania |

**Scoring formula:**
- Story importance (assessed by Claude based on impact on Europeans)
- Media coverage volume (number of outlets, depth of coverage)
- Coverage gap score = importance minus coverage
- Stories with high gap score surface as candidates

### Tool 2 — Viral Content Scanner

Monitors platforms where stories surface organically before or instead of mainstream press. High-engagement posts with no mainstream coverage flag as *"community signal — needs verification."*

**Sources monitored:**

| Platform | Subreddits / Sections |
|----------|----------------------|
| Reddit | r/europe, r/worldnews, r/de, r/france, r/italy, r/romania, r/EuropeanFederalists |
| 9gag | Trending section (public scrape) |
| Twitter/X | Trending by country — Phase 2 (requires paid API) |

**Reddit API** — public JSON, no authentication required:
```
https://www.reddit.com/r/europe/top.json?limit=25&t=day
https://www.reddit.com/r/worldnews/top.json?limit=25&t=day
```

**9gag** — public trending section, scrapable.

**Output:** Posts with high engagement and no mainstream coverage match — flagged for verification.

**Warning:** Viral content platforms carry high risk of:
- Emotionally manipulated framing
- Missing context
- Outright false but engaging content
- Coordinated seeding (especially relevant for Russia hybrid war category)

This is why nothing from this scanner publishes without passing the Verification Engine.

### Tool 3 — Verification Engine

The most critical tool in the stack. Every story — regardless of source — must pass through here before reaching the Script Generator.

**Verification levels:**

| Status | Criteria | Action |
|--------|----------|--------|
| ✅ **Verified** | Two or more independent legitimate sources confirmed | Passes to Script Generator |
| ⚠️ **Partial** | One source found, second not yet confirmed | Held — researcher must find second source |
| ❌ **Unverified** | No legitimate primary source found | Rejected — never publishes |

**Primary source types (in order of credibility):**
1. Official EU/government documents and proceedings
2. Court records
3. Peer-reviewed research
4. UN, Council of Europe, NATO official reports
5. Amnesty International, Human Rights Watch documented reports
6. National statistics offices
7. Named senior officials on record

**Secondary source types (acceptable as second source only):**
1. Major wire services (Reuters, AFP, DPA, ANSA)
2. Quality national newspapers with named journalists
3. Academic institutions

**Never accepted as sources:**
- Anonymous accounts
- Social media posts without institutional backing
- Blogs or opinion sites
- Unnamed "sources familiar with the matter"

### Russia Disinformation Flag 🚩

Any story touching these categories automatically triggers **enhanced verification rules:**
- Russia, Ukraine, Belarus conflict
- Election interference in European countries
- Energy policy and Russian gas/oil dependency
- NATO and European defence
- Migration stories with political angles

**Enhanced rules:**
- Minimum three independent sources (not two)
- At least two must be official institutional sources (EU, NATO, national government, court)
- Claude performs additional disinformation pattern check before passing to production
- Story held for 24 hours minimum to allow additional verification

**Reason:** These categories are the most actively targeted by coordinated disinformation seeding on Reddit, 9gag, and social platforms.

---

## 11. Anonymity Setup

**Full anonymity to the public audience. Legal identity known only to platforms and tax authorities (Phase 2).**

### Per-language account setup (repeat for each of the 5 languages)

| Step | Action | Tool |
|------|--------|------|
| 1 | Create encrypted email | [ProtonMail](https://proton.me) — e.g. `theignoredsignal.en@proton.me` |
| 2 | Get VoIP number for verification | [Hushed](https://hushed.com) or [Freezvon](https://freezvon.com) (~€5) |
| 3 | Install VPN | [Mullvad VPN](https://mullvad.net) (~€5/month, accepts cash, no account name required) |
| 4 | Create Google account | Always with VPN active, using ProtonMail as recovery email |
| 5 | Create YouTube Brand Account | Channel name = language-specific brand name |
| 6 | Create TikTok account | Using ProtonMail, VoIP number, VPN active |

### Ongoing anonymity rules

| Rule | Reason |
|------|--------|
| Always use VPN before opening any channel account | Home IP is the most identifying feature |
| Never access channel accounts from mobile data | Carrier data links directly to personal identity |
| Use AI voice narrator — never real voice | Voice is a biometric identifier |
| Never mention personal details anywhere | Even small details accumulate over time |
| Never respond to identity requests | No exceptions |
| Keep channel emails completely separate from personal life | Never check from personal devices without VPN |
| Never link to personal social media | Destroys anonymity instantly |
| Separate Google account per language channel | No cross-linking between channels |

### Suggested email naming convention
```
theignoredsignal.en@proton.me   → English channel
theignoredsignal.fr@proton.me   → French channel
theignoredsignal.de@proton.me   → German channel
theignoredsignal.it@proton.me   → Italian channel
theignoredsignal.ro@proton.me   → Romanian channel
```

---

## 12. Legal Coverage

- **Content type:** Neutral factual reporting of verifiable events — protected as journalism and public interest content across all EU member states and the UK
- **Relevant legal framework:** EU press freedom protections, UK Defamation Act 2013 (truth is an absolute defence), French law (Article 24 targets incitement against people, not factual reporting), German law (§130 StGB targets incitement, not journalism)
- **Defamation risk:** Managed through strict source discipline — only verified facts, only named institutional sources, official responses included
- **Key principle:** Reporting what happened ≠ incitement. The channel presents facts. Viewers draw conclusions.
- **Phase 2 legal protection:** Estonian OÜ company adds corporate layer between personal identity and public-facing monetization

---

## 13. Technology Stack

### Frontend
- **Framework:** React (JSX)
- **Styling:** Custom CSS variables, no external framework
- **Storage:** Browser state (Phase 1), persistent storage API (Phase 2)

### AI Layer
- **Model:** Anthropic Claude API — `claude-sonnet-4-20250514`
- **Max tokens:** 1000 per call
- **Web search:** Enabled via `web_search_20250305` tool for Press Scanner and Verification Engine
- **All API calls:** Wrapped in try/catch, JSON responses strip markdown fences before parsing

### Data Sources
- Reddit public JSON API (no auth)
- 9gag public trending (scrape)
- Major European news outlets (via Claude web search)
- Twitter/X API — Phase 2 (paid developer account)

### AI Voice Narration
- Tool to be selected: ElevenLabs or equivalent
- One distinct voice per language — consistent across all videos on that channel
- Never the creator's real voice

---

## 14. Platform Tools — Full List

| Tool | Purpose | Status |
|------|---------|--------|
| **Press Coverage Analyzer** | Scan outlets daily, score importance vs. coverage gap | To build |
| **Viral Content Scanner** | Monitor Reddit, 9gag for high-engagement underreported stories | To build |
| **Verification Engine** | Cross-reference sources, rate credibility, flag disinfo | To build |
| **Script Generator** | Friend-tone narration script per language with source citations | To build |
| **Visibility Advisor** | Score content for SEO, hook strength, algorithm fit, source transparency | To build |
| **Content Calendar** | Plan weekly content across 5 languages × 2 platforms | To build |
| **Export Panel** | Production-ready script with timestamps | To build |

---

## 15. Launch Strategy

### Phase 1 — Proof of concept
- Launch **one channel, one language** — whichever language the creator is most comfortable with
- Produce 10 videos across different content categories
- Observe: which categories get traction, what completion rates look like, what audience engagement feels like
- Do not monetize, do not reveal identity, do not cross-promote

### Phase 2 — Validation
- If Channel 1 shows consistent growth after 30–60 days, clone the operation into Language 2
- Refine the script format based on what worked in Phase 1
- Begin planning Estonian company registration for future monetization
- Activate Twitter/X API for enhanced viral scanning

### Phase 3 — Scale
- Roll out remaining three languages using the proven formula
- Enable monetization across all channels via Estonian OÜ
- Begin content calendar planning across all five languages simultaneously

### First 10 recommended stories (universal, low-risk, high-impact)
1. EU legislation that passed in the last 6 months with no media coverage
2. A documented Russian disinformation campaign targeting a specific European country
3. A housing crisis data story — real numbers vs. official narrative
4. A human rights violation documented by the Council of Europe but unreported nationally
5. An environmental finding buried after one news cycle
6. A corruption case with court records that mainstream media dropped
7. Energy poverty statistics that don't make headlines
8. A scientific finding that complicates an official government position
9. A quiet extraordinary human interest story from an underreported European community
10. A historical context story explaining why a current European problem exists

---

## 16. Separation from Other Projects

**This project has absolutely no connection to any other channel, project, or identity.**

- Different Google accounts
- Different ProtonMail addresses
- Different VoIP numbers
- Different VPN sessions
- Different brand, name, visual identity
- No cross-promotion ever
- No shared content ever
- No shared codebase
- No links between projects in any direction

---

## 17. Key Decisions Already Made

| Decision | Choice |
|----------|--------|
| Channel name family | The Ignored Signal / Le Signal Ignoré / Das Überhörte Signal / Il Segnale Ignorato / Semnalul Ignorat |
| Monetization at launch | No — add later via Estonian OÜ when traction proven |
| Languages | English, French, German, Italian, Romanian |
| Platforms | YouTube Shorts + TikTok |
| Video length | 45–90 seconds |
| On-camera presence | None — AI voice, text, visuals only |
| Editorial line | Neutral, factual, sourced — no opinion, no speculation |
| Content scope | All underreported European stories — not limited to any single topic |
| Launch approach | One language first, prove it works, then scale |
| Intelligence layer | Press scanner + viral scanner + verification engine — mandatory pipeline |
| Russia stories | Enhanced verification — 3 sources minimum, 24h hold |

---

## 18. Next Development Steps

### Platform
- [ ] Press Coverage Analyzer — Claude API + web search, daily scan by language
- [ ] Viral Content Scanner — Reddit JSON API + 9gag scraper
- [ ] Verification Engine — source credibility rating, Russia disinfo flag
- [ ] Script Generator — friend tone, per language, source citation formatting
- [ ] Visibility Advisor — SEO, hook, algorithm fit, source transparency scoring
- [ ] Content Calendar — 5 languages × 2 platforms
- [ ] Export Panel — production-ready script with timestamps

### Infrastructure
- [ ] Set up ProtonMail accounts (five — one per language)
- [ ] Acquire VoIP numbers (five — one per language)
- [ ] Configure Mullvad VPN
- [ ] Create Google Brand Accounts (five)
- [ ] Create TikTok accounts (five)
- [ ] Select AI voice narrator tool (ElevenLabs or equivalent)
- [ ] Configure one distinct voice per language

### Phase 2 additions
- [ ] Estonian e-Residency company registration
- [ ] AdSense account under company name
- [ ] Twitter/X paid developer API for enhanced viral scanning

---

*Last updated: June 2026*
*Status: Pre-launch — platform in development*
