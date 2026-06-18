# The Ignored Signal — Claude Code Instructions

This is the development workspace for **The Ignored Signal** multilingual news platform.

## Project context
Read `PROJECT_BRIEF.md` for full context before making any changes.
Read `CLAUDE_CONTEXT.md` for a quick session summary.

---

## Stack
- React JSX (single file components where possible)
- Anthropic Claude API (`claude-sonnet-4-20250514`, max_tokens: 1000)
- Custom CSS-in-JS via style tags (no Tailwind, no external CSS framework)
- No browser storage APIs (use React state)
- Reddit public JSON API (no auth required)
- 9gag trending (public scrape)
- Claude web search tool enabled for Press Scanner and Verification Engine

## Claude API — web search enabled
```javascript
// For Press Coverage Analyzer and Verification Engine
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    tools: [{ type: "web_search_20250305", name: "web_search" }],
    messages: [{ role: "user", content: prompt }]
  })
});
// Handle mixed content blocks (text + tool_use)
const fullResponse = data.content
  .map(item => item.type === "text" ? item.text : "")
  .filter(Boolean)
  .join("\n");
```

## Reddit API (no auth)
```javascript
// Top posts today — use for Viral Content Scanner
const endpoints = [
  "https://www.reddit.com/r/europe/top.json?limit=25&t=day",
  "https://www.reddit.com/r/worldnews/top.json?limit=25&t=day",
  "https://www.reddit.com/r/de/top.json?limit=25&t=day",
  "https://www.reddit.com/r/france/top.json?limit=25&t=day",
  "https://www.reddit.com/r/italy/top.json?limit=25&t=day",
  "https://www.reddit.com/r/romania/top.json?limit=25&t=day",
];
// Add header to avoid 429: { "User-Agent": "TheIgnoredSignal/1.0" }
```

---

## Code standards
- All API calls wrapped in try/catch
- JSON responses: strip markdown fences before parsing
  ```javascript
  const clean = text.replace(/```json|```/g, "").trim();
  const parsed = JSON.parse(clean);
  ```
- Loading states on all async operations
- Error messages shown inline, never silent failures
- Mobile responsive — max-width 700px centered layout
- Dark theme by default

---

## File structure

```
src/
  components/
    intelligence/
      PressAnalyzer.jsx       # Scan outlets daily, score coverage gap
      ViralScanner.jsx        # Reddit + 9gag high-engagement stories
      VerificationEngine.jsx  # Source credibility — Verified/Partial/Rejected
    production/
      ScriptGenerator.jsx     # Friend-tone narration script per language
      VisibilityAdvisor.jsx   # SEO, hook, algorithm fit, source transparency
      ContentCalendar.jsx     # Plan across 5 languages × 2 platforms
      ExportPanel.jsx         # Production-ready script with timestamps
  App.jsx                     # Main tabbed layout — Intelligence | Production
  index.jsx                   # Entry point
```

---

## Intelligence pipeline — build order

### 1. Verification Engine (build first — everything depends on it)

Input: any story claim or URL
Process: Claude web search → find primary sources → rate credibility
Output:
```javascript
{
  status: "verified" | "partial" | "unverified",
  sources: [{ name, url, type, credibility }],
  russiaFlag: true | false,   // triggers enhanced rules
  notes: "string"
}
```

Verification thresholds:
- `verified` = 2+ independent legitimate sources found
- `partial` = 1 source found, needs second
- `unverified` = no legitimate primary source — NEVER publishes

Russia flag enhanced rules (auto-triggered for Russia/Ukraine/NATO/election stories):
- Requires 3+ sources minimum
- At least 2 must be official institutional (EU, NATO, national government, court)
- 24-hour hold before passing to production

Source credibility hierarchy:
1. Official EU/government documents
2. Court records
3. Peer-reviewed research
4. UN, Council of Europe, NATO reports
5. Amnesty International, Human Rights Watch
6. National statistics offices
7. Named senior officials on record

Never accepted:
- Anonymous accounts
- Social media posts without institutional backing
- Unnamed "sources familiar with the matter"

### 2. Press Coverage Analyzer

Input: language + category (optional)
Process: Claude web search scans major outlets → scores importance vs. coverage volume
Output:
```javascript
{
  stories: [{
    headline: "string",
    summary: "string",
    importanceScore: 1-10,
    coverageScore: 1-10,    // how much it was covered
    gapScore: 1-10,         // importance minus coverage — higher = more overlooked
    sources: ["url"],
    category: "string",
    language: "en|fr|de|it|ro"
  }]
}
```

Outlets to scan per language (pass to Claude web search):
- EN: BBC, Guardian, Reuters, Politico Europe, The Times
- FR: Le Monde, Le Figaro, Libération, Mediapart, AFP
- DE: Spiegel, FAZ, Süddeutsche Zeitung, Zeit, DPA
- IT: Repubblica, Corriere della Sera, ANSA, Il Fatto Quotidiano
- RO: Digi24, ProTV, G4Media, HotNews, Euractiv Romania

### 3. Viral Content Scanner

Input: language filter (optional)
Process: fetch Reddit JSON → filter high upvotes + low mainstream coverage → flag as community signal
Output:
```javascript
{
  posts: [{
    title: "string",
    url: "string",
    upvotes: number,
    subreddit: "string",
    mainstreamCoverage: true | false,
    verificationStatus: "pending",
    flaggedFor: "string"   // reason it was flagged
  }]
}
```

### 4. Script Generator

Input: verified story + language + platform
Output:
```javascript
{
  hook: "string",           // 3-5 seconds
  whatHappened: "string",   // 15-20 seconds
  whyItMatters: "string",   // 15-20 seconds
  sourceText: "string",     // shown on screen
  callToAction: "string",   // 5-7 seconds
  fullScript: "string",     // complete narration
  estimatedDuration: "number seconds",
  language: "en|fr|de|it|ro",
  platform: "youtube|tiktok"
}
```

### 5. Visibility Advisor

Input: title + script + hashtags + language + platform
Scores:
- SEO & discoverability (0-10)
- Hook strength (0-10)
- Algorithm fit (0-10)
- Source transparency (0-10)  ← unique to this platform
- Emotional resonance (0-10)
Output: grade (A+→F), overall score, strengths, improvements, optimized versions

### 6. Content Calendar

Grid view: 5 languages × 2 platforms × 7 days
Drag and drop story cards into slots
Shows: story title, verification status, language, platform, estimated publish time

### 7. Export Panel

Input: completed script
Output: formatted production document with:
- Full script with timestamp markers
- Source citations formatted for on-screen display
- Hashtags per platform
- Thumbnail text suggestions
- AI voice narration notes

---

## Design tokens
```css
--bg: #09090f
--card: #0e0e18
--border: #1b1b2a
--fg: #e9e5da
--muted: #636077
--accent: #c0392b        /* deep red */
--accent-alt: #1a6bb5    /* electric blue */
--emerald: #27ae78
--yellow: #f0a500
--display: 'Playfair Display', serif
--body: 'Lato', sans-serif
--mono: 'Fira Code', monospace
```

## Verification status colors
```css
--verified: #27ae78      /* green */
--partial: #f0a500       /* yellow */
--unverified: #c0392b    /* red */
--russia-flag: #e74c3c   /* bright red — enhanced rules */
```

---

## Languages supported
```javascript
const LANGUAGES = [
  { id: "en", label: "English",  flag: "🇬🇧", channelName: "The Ignored Signal" },
  { id: "fr", label: "French",   flag: "🇫🇷", channelName: "Le Signal Ignoré" },
  { id: "de", label: "German",   flag: "🇩🇪", channelName: "Das Überhörte Signal" },
  { id: "it", label: "Italian",  flag: "🇮🇹", channelName: "Il Segnale Ignorato" },
  { id: "ro", label: "Romanian", flag: "🇷🇴", channelName: "Semnalul Ignorat" },
];
```

## Content categories
```javascript
const CATEGORIES = [
  "EU Legislation & Policy",
  "Economic Stories",
  "Environmental Findings",
  "Scientific Research",
  "Historical Context",
  "Human Interest",
  "Hybrid War — Russia",      // triggers Russia disinfo flag
  "Human Rights Violations",
  "Corruption",
];

// These categories auto-trigger enhanced verification (3 sources, 24h hold)
const ENHANCED_VERIFICATION_CATEGORIES = [
  "Hybrid War — Russia",
];

// These keywords in any story auto-trigger Russia flag
const RUSSIA_FLAG_KEYWORDS = [
  "russia", "ukraine", "belarus", "nato", "election interference",
  "disinformation", "hybrid war", "energy dependency", "wagner",
  "kremlin", "fsb", "svr", "gia", "putin"
];
```

---

## Important
This project is completely isolated from all other projects.
No shared code, no shared accounts, no cross-references.
Do not reference, import from, or link to any other project in this workspace.
