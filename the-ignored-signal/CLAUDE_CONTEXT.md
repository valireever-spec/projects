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
