# Verification Engine

The first component in The Ignored Signal's intelligence layer. Verifies claims and finds credible sources using Claude's web search capability.

## What it does

Takes a story claim, headline, or URL and:
1. Searches the web for credible sources using Claude API
2. Classifies sources by credibility tier (official institutions → NGOs → research → news)
3. Returns verification status: **verified**, **partial**, or **unverified**
4. Flags stories related to Russia/disinformation for enhanced verification rules

## Verification Logic

### Standard verification (non-Russia stories)
- **Verified** = 2+ independent legitimate sources found
- **Partial** = 1 source found, needs second independent source
- **Unverified** = 0 legitimate sources (story cannot be published)

### Enhanced verification (Russia-related stories)
Automatically triggered for stories containing: `russia`, `ukraine`, `nato`, `disinformation`, `hybrid war`, etc.

- **Verified** = 3+ sources WITH 2+ institutional sources (official EU/government/court/NATO)
- **Partial** = 2 sources but needs more institutional backing
- **Unverified** = Fewer than 3 sources or insufficient institutional backing
- **24-hour hold** applied before passing to Script Generator

## Source Credibility Hierarchy

1. **Official EU/Government Documents** (score: 10)
   - EU Commission decisions
   - Court records
   - Government ministries

2. **International Bodies** (score: 9)
   - UN reports
   - NATO reports
   - Council of Europe

3. **NGOs & Watchdogs** (score: 8)
   - Amnesty International
   - Human Rights Watch
   - Transparency organizations

4. **Statistics & Research** (score: 7)
   - National statistics offices
   - Peer-reviewed research
   - Academic institutions

5. **Named Officials** (score: 6)
   - Named person on record
   - Must include attribution

### Never Accepted
- Anonymous accounts
- Social media without institutional backing
- Unnamed sources ("sources familiar with the matter")

## API Usage

```javascript
// Input
claim: "EU passed new AI regulation in secret"

// Returns
{
  status: "verified",
  requiresHold: false,
  russiaFlag: false,
  sources: [
    {
      name: "EU Commission Official Statement",
      url: "https://...",
      type: "government",
      description: "Official announcement of AI Act passage",
      credibility: { tier: 1, score: 10, label: "Official EU Document" }
    },
    {
      name: "Reuters Coverage",
      url: "https://...",
      type: "news",
      description: "Reuters reporting on the regulation",
      credibility: { tier: 5, score: 6, label: "Named Official on Record" }
    }
  ],
  analysis: "Story verified through official EU sources...",
  message: "Verified with 2+ independent sources."
}
```

## Development

### Start the dev server
```bash
npm start
```
Opens http://localhost:3000

### Build for production
```bash
npm build
```

## Usage in the UI

1. Enter your Anthropic API key (click "Set API Key")
2. Paste story claim, headline, or URL to verify
3. Click "Verify Story"
4. Review sources, credibility ratings, and verification status
5. Decision: Pass to Script Generator (if verified) or reject/investigate further (if partial/unverified)

## Integration with other components

- **Output → Script Generator**: Only verified stories are sent to script writing
- **Russia flag → Enhanced rules**: Automatically applies strict verification thresholds
- **Verification status → Content Calendar**: Tracks which stories are publication-ready
- **Sources → Export**: Source citations included in final video captions

## Next components to build

1. ✅ **Verification Engine** (complete)
2. **Press Coverage Analyzer** — scan major outlets, score coverage gaps
3. **Viral Content Scanner** — Reddit + 9gag high-engagement posts
4. **Script Generator** — friend-tone narration scripts
5. **Visibility Advisor** — SEO and algorithm scoring
6. **Content Calendar** — plan 5 languages × 2 platforms
7. **Export Panel** — production-ready scripts with timestamps
