# Claude Context — The Ignored Signal

You are helping build **The Ignored Signal**, an anonymous multilingual short-form news platform covering underreported European stories.

## Brand
- 🇬🇧 The Ignored Signal
- 🇫🇷 Le Signal Ignoré
- 🇩🇪 Das Überhörte Signal
- 🇮🇹 Il Segnale Ignorato
- 🇷🇴 Semnalul Ignorat

## Mission
Surface real European stories that were reported but ignored — factual, sourced, neutral. Tone: a trusted friend explaining something important. Never opinionated, never speculative, always sourced.

## Tech Stack
- React (JSX) frontend
- Anthropic Claude API (`claude-sonnet-4-20250514`, max_tokens: 1000)
- Claude web search tool (`web_search_20250305`) for Press Scanner and Verification Engine
- Reddit public JSON API (no auth) for Viral Scanner
- 9gag public scrape for Viral Scanner
- Custom CSS variables, no framework

## Key Editorial Rules
- One language per video, one platform per video
- Minimum two sources per story, at least one primary
- Sources shown on screen in every video
- No opinion, no speculation, no unverified claims
- Nothing publishes without Verified status from Verification Engine
- Russia/Ukraine/NATO stories: 3 sources minimum + 24h hold
- Full creator anonymity (ProtonMail + VoIP + Mullvad VPN + AI voice)
- No monetization at launch — Estonian OÜ added later

## Content Strategy (analytics-derived, 2026-08-28)
Data-driven priorities from live Sub Radar performance (94% Shorts-feed traffic → **retention is the master lever**). See `PUBLISHED.md` → Analytics snapshots / Lessons learned for the numbers.
- **Topic focus: MIGRATION/diaspora + INTERNAL POLITICS & GOVERNANCE** (corruption, courts/CJUE, EU-funds mismanagement, political dysfunction, cross-country governance comparisons). These break out (migration 1.342, doctors 291, court 125). **Deprioritize abstract stat topics** (energy poverty, child poverty, digital skills, literacy) — they consistently flop (17–56 views).
- **Audience is ~half diaspora** (2026-08-29 geo: 51% RO, 49% abroad — DE/IT/ES/AT/UK/FR + Moldova). The diaspora watches **1.5–2.3× longer** than domestic viewers (Italy 39s vs Romania 17s) — migration/depopulation/Poland topics are literally their story. Frame diaspora-relevant content **to the person abroad** ("tu, care ai plecat în Italia/Germania…"). Domestic retention (17s) is the weak spot; avoid a relentlessly fatalistic "Romania is failing" tone that makes home viewers swipe.
- **Diaspora-life pillar (Romanians in Germany / Italy / Spain):** make dedicated stories about the diaspora itself — conditions and work abroad, why they left, discrimination/exploitation, remittances home, whether they'd return, communities in Turin/Madrid/Munich. This super-serves the most-engaged ~half of the audience (DE 13% / IT 9% / ES 4%). Same rules: hard number, personal hook, ≥2 sources (Eurostat/INS/host-country stats).
- **Every topic must pass:** "does it hit the viewer personally in one sentence?"
- **Reduce statistics & methodology *in the narration*** (NOT a sourcing change — the 2-source rule and on-screen source card stay). One hero number, don't stack stats, and never recite methodology ("datele Eurostat arată…") in the spoken flow — keep sources on the card/description.
- **Personal "this is YOU" stake in the first ~8s** (before any data); **≤35s total**; **debate-question CTA** + auto-pinned comment.

## Content Categories
EU legislation, economic stories, environmental findings, scientific research, historical context, human interest, Russia hybrid war (enhanced verification), human rights violations, corruption

## Platforms
YouTube Shorts + TikTok — 5 languages × 2 platforms = 10 accounts total

## Intelligence Pipeline (build order)
1. **Verification Engine** — source credibility rating (Verified ✅ / Partial ⚠️ / Rejected ❌), Russia disinfo flag 🚩
2. **Press Coverage Analyzer** — Claude web search scans major outlets, scores importance vs. coverage gap
3. **Viral Content Scanner** — Reddit JSON API + 9gag scrape, flags high-engagement underreported posts
4. **Script Generator** — friend-tone narration per language with source citations and timestamps
5. **Visibility Advisor** — SEO, hook, algorithm fit, source transparency scoring
6. **Content Calendar** — 5 languages × 2 platforms grid view
7. **Export Panel** — production-ready script with timestamps and on-screen source formatting

## File Structure
```
src/
  components/
    intelligence/
      PressAnalyzer.jsx
      ViralScanner.jsx
      VerificationEngine.jsx
    production/
      ScriptGenerator.jsx
      VisibilityAdvisor.jsx
      ContentCalendar.jsx
      ExportPanel.jsx
  App.jsx
  index.jsx
```

## Design Tokens
```css
--bg: #09090f  --card: #0e0e18  --border: #1b1b2a
--fg: #e9e5da  --muted: #636077  --accent: #c0392b
--emerald: #27ae78  --yellow: #f0a500
--display: 'Playfair Display'  --body: 'Lato'  --mono: 'Fira Code'
```

## This project is completely separate from all other projects.
## Full brief: See PROJECT_BRIEF.md — Full technical spec: See CLAUDE.md
